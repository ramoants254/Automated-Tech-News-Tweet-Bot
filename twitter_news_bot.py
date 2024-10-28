import os
import tweepy
import logging
import time
import random
import requests
from dotenv import load_dotenv
from tweepy.errors import TweepyException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up API credentials
API_KEY = os.getenv('TWITTER_API_KEY')
API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
NEWS_API_TOKEN = os.getenv('NEWS_API_TOKEN')

# Check for missing environment variables
required_vars = [API_KEY, API_KEY_SECRET, BEARER_TOKEN, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, NEWS_API_TOKEN]
if not all(required_vars):
    logging.error("Missing environment variables. Please check the .env file.")
    exit(1)

# Tweepy client setup
client = tweepy.Client(BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# News API endpoint
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
NEWS_API_HEADERS = {"Authorization": f"Bearer {NEWS_API_TOKEN}"}

# Expanded tweet components for more diverse and engaging tweets
start_phrases = [
    "Have you heard about",
    "Recently, I came across",
    "Today’s buzz in tech is all about",
    "Can you believe",
    "Breaking news in tech:",
    "Exciting tech updates:",
    "Guess what’s new in technology?",
    "Let’s talk tech—have you seen",
    "Unbelievable progress in tech!",
    "Here's what's making waves in tech:",
]

endings = [
    "This is quite a breakthrough! 🌟",
    "Amazing strides in technology! 🚀",
    "What an exciting future ahead! 💡",
    "The future feels closer than ever! ⚙️",
    "Tech keeps surprising us! 🤖",
]

# Function to fetch the latest tech news
def fetch_tech_news():
    params = {"category": "technology", "country": "us", "pageSize": 5}
    response = requests.get(NEWS_API_URL, headers=NEWS_API_HEADERS, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles if article.get("title")]
    else:
        logging.error(f"Failed to fetch news: {response.status_code}")
        return []

# Function to generate a tweet from a news headline
def generate_news_tweet(headline):
    start = random.choice(start_phrases)
    ending = random.choice(endings)
    return f"{start} {headline} {ending}"

# Function to load and filter previously posted tweets
def load_and_filter_posted_tweets():
    posted_tweets = set()
    if os.path.exists('posted_tweets.txt'):
        with open('posted_tweets.txt', 'r') as file:
            posted_tweets = {line.strip() for line in file.readlines()}
    return posted_tweets

# Function to save posted tweets
def save_posted_tweets(posted_tweets):
    with open('posted_tweets.txt', 'w') as file:
        for tweet in posted_tweets:
            file.write(tweet + '\n')

# Function to post engaging tweets on Twitter
def post_engaging_tweets():
    try:
        posted_tweets = load_and_filter_posted_tweets()
        tech_news = fetch_tech_news()
        
        # Set a limit for tweets to be posted daily (example: 5)
        daily_limit = 5
        count = 0

        for headline in tech_news:
            if count >= daily_limit:
                break

            tweet_text = generate_news_tweet(headline)

            # Check for repetition
            if tweet_text not in posted_tweets:
                try:
                    client.create_tweet(text=tweet_text)
                    logging.info("Posted a new tech tweet.")
                    posted_tweets.add(tweet_text)
                    count += 1
                    time.sleep(3600)  # Sleep for 1 hour between posts

                except TweepyException as e:
                    if 'rate limit' in str(e).lower():
                        logging.warning("Rate limit reached. Pausing for 15 minutes.")
                        time.sleep(15 * 60)
                    else:
                        logging.error(f"Error posting to Twitter: {e}")
                    continue

        save_posted_tweets(posted_tweets)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    post_engaging_tweets()
