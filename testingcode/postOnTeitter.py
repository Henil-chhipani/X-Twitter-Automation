import os
from dotenv import load_dotenv
import tweepy

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET_KEY")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Initialize Tweepy Client with the keys
client = tweepy.Client(
    consumer_key=consumer_key, 
    consumer_secret=consumer_secret,
    access_token=access_token, 
    access_token_secret=access_secret
)

try:
    # Create and send a tweet
    response = client.create_tweet(text="I have achieved X(twitter) automation with python.....😎😎😎")
    print("Tweet posted successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
    