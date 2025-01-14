import google.generativeai as genai
import tweepy
import schedule
import time
import os
from dotenv import load_dotenv
import json
import re 

load_dotenv()
# Access API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET_KEY")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction="You are a 23-year-old Android developer from Gujarat, India, with 2 years of experience. In your first year, you developed apps using Java and XML, and in your second year, you specialized in Kotlin and Jetpack Compose. You are passionate about engineering, love solving problems, and enjoy helping others. You are proficient in core Android development concepts, including activities, fragments, services, broadcast receivers, Retrofit, Gradle, Room database wrapper, Glide, Firebase, basic Hilt for dependency injection, MediaPlayer, file management, and Jetpack Compose. You are familiar with the MVVM and MVI architectural patterns commonly used in Android app development. You also have expertise with the CameraX API for advanced camera functionality. However, you are not yet familiar with CI/CD pipelines or deep linking in Android. To grow your personal brand, you post three daily tweets: 10 AM: A tweet focused on Android development. 12 PM: A motivational or engineering-related tweet. 7 PM: A tweet about a Gen Z topic you enjoy. Your hobbies include watching random YouTube videos on history, geopolitics, Indian local politics, personal finance, the stock market, memes, stand-up comedy, sci-fi movies, rational thinking, debunking pseudoscience, and Indian startup news. You are driven by your passion for rational thinking, innovation, and sharing meaningful insights with others.")


# Initialize Tweepy Client with the keys
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_secret
)

# Array to store generated tweets
tweets_to_post = []


def clean_response(response_text):
    """
    Remove markdown syntax (e.g., ```json) from the response.
    """
    # Remove triple backticks and "json" keyword
    response_text = re.sub(r"```json|```", "", response_text).strip()
    return response_text

# Function to generate tweets in JSON format
def generate_tweets():
    global tweets_to_post

    # Ensure the array is empty before generating new tweets
    if len(tweets_to_post) > 0:
        print("Tweets already generated for the day. Skipping generation.")
        return

    # Prompt to generate tweets in JSON format
    prompt = """
Generate three tweets in the following JSON format:
[
  {
    "time": "10:00 AM",
    "tweet": "Your Android-related tweet here."
  },
  {
    "time": "12:00 PM",
    "tweet": "Your motivational or engineering-related tweet here."
  },
  {
    "time": "7:00 PM",
    "tweet": "Your Gen Z topic tweet here."
  }
]
"""

    # Generate tweets
    response = model.generate_content(prompt)
    print("response from gemini"+response.text)

    try:
        # Clean the response
        cleaned_response = clean_response(response.text)
        print("Cleaned response:", cleaned_response)  # Debugging: Print the cleaned response

        # Parse the JSON response
        tweets_data = json.loads(cleaned_response)
        print("Parsed tweet data:", tweets_data)  # Debugging: Print parsed data

        # Store tweets in the array
        for tweet in tweets_data:
            tweets_to_post.append(tweet)
        print("Tweets generated and stored in JSON format.")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON response:", e)
        print("Attempting to extract JSON using regex...")

        # Fallback: Use regex to extract JSON
        try:
            tweet_pattern = re.compile(r'{\s*"time"\s*:\s*".+?"\s*,\s*"tweet"\s*:\s*".+?"\s*}')
            matches = tweet_pattern.findall(response.text)

            if matches:
                for match in matches:
                    # Convert each matched string to a Python dictionary
                    tweet_data = json.loads(match)
                    tweets_to_post.append(tweet_data)
                print("Tweets extracted and stored successfully using regex.")
            else:
                print("No matches found in the response text. Raw response:", response.text)
        except Exception as e:
            print("An error occurred while extracting JSON using regex:", e)
    except Exception as e:
        print("An error occurred:", e)

# Function to post a tweet


def post_tweet(tweet):
    try:
        print("twittting")
        res = client.create_tweet(text=tweet)
        print("Tweet posted successfully:", tweet)
    except Exception as e:
        print("Failed to post tweet:", e)

# Function to post tweets at scheduled times


# Function to post tweets at scheduled times
def post_scheduled_tweets():
    global tweets_to_post

    if len(tweets_to_post) == 0:
        print("No tweets to post. Skipping.")
        return

    # Post the next tweet in the queue
    tweet_data = tweets_to_post.pop(0)
    tweet_text = tweet_data["tweet"]  # Extract the "tweet" field (string) from the dictionary
    post_tweet(tweet_text)
    print("Tweet posted. Remaining tweets:", len(tweets_to_post))

    # If all tweets are posted, clear the array
    if len(tweets_to_post) == 0:
        print("All tweets posted for the day. Array cleared.")


# Schedule tasks
schedule.every().day.at("12:00:01").do(
    generate_tweets)  # Generate tweets at 7 AM
schedule.every().day.at("15:47:30").do(
    post_scheduled_tweets)  # Post first tweet at 10 AM
schedule.every().day.at("03:47:33").do(
    post_scheduled_tweets)  # Post second tweet at 12 PM
schedule.every().day.at("03:47:35").do(
    post_scheduled_tweets)  # Post third tweet at 7 PM

# Keep the script running
print("Scheduler started. Waiting for scheduled tasks...")
while True:
    schedule.run_pending()
    time.sleep(1)


