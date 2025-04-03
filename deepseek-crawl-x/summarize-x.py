import tweepy
from transformers import pipeline
import datetime
import time

# Set up Twitter API keys (replace with your own keys)
API_KEY = "your_api_key"
API_SECRET_KEY = "your_api_secret_key"
ACCESS_TOKEN = "your_access_token"
ACCESS_TOKEN_SECRET = "your_access_token_secret"

# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(consumer_key=API_KEY, consumer_secret=API_SECRET_KEY,
                                access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Initialize Hugging Face Summarizer using the open-source BART model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Set Elon Musk's Twitter handle
twitter_handle = 'elonmusk'

# Function to retrieve and summarize Elon Musk's tweets for the day
def get_and_summarize_tweets():
    # Get today's date in the format "YYYY-MM-DD"
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Get the last 5 tweets from Elon Musk's Twitter account
    tweets = api.user_timeline(screen_name=twitter_handle, count=5, tweet_mode="extended")
    
    tweet_texts = []
    for tweet in tweets:
        # Check if the tweet was posted today
        if tweet.created_at.strftime('%Y-%m-%d') == today_date:
            tweet_texts.append(tweet.full_text)
    
    if tweet_texts:
        print(f"Today's tweets from {twitter_handle}:")
        
        for i, tweet in enumerate(tweet_texts, 1):
            print(f"\nTweet {i}: {tweet}")
            
            # Summarize the tweet using the BART model
            summary = summarizer(tweet, max_length=50, min_length=25, do_sample=False)
            print(f"Summary: {summary[0]['summary_text']}")
    else:
        print(f"No tweets from {twitter_handle} today.")

# Schedule the function to run once a day (or any interval you want)
while True:
    get_and_summarize_tweets()
    # Wait for 24 hours (86400 seconds) before running again
    time.sleep(86400)
