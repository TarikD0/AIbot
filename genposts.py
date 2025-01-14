import tweepy
import json
import os
import time


BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAD6FyAEAAAAA%2BZ4sMKRAqbVI87HuB0HJGhrBenI%3DHqsVffS1lmKoMrQghxYylWuEougJOEHXVGsgKjXMX7VerfasaS"
API_KEY = "bjb24r5PBXIWVZNCueyrzraRk"
API_SECRET = "tYkgZyaFak5OTOgVPM8sKC64rJSDYYSBFUfASS1wl0euxQdVle"
ACCESS_TOKEN = "1875194125739290624-ERmbePZAHhw4h001ECPdj24LQ0bSRC"
ACCESS_SECRET = "aWvcadMBWoJfP1ScyA4KLWKeMbjYyIaovimIJL4sCdfWq"


def initialize_client(api_key, api_secret, access_token, access_secret):
    """Initialize the Tweepy client."""
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
    return client


def load_new_tweets(file_name="tweets.json", count=5):
    """Load the next batch of new tweets."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
        new_tweets = [entry for entry in data if entry["status"] == "new"][:count]
        return new_tweets, data
    except FileNotFoundError:
        print("Tweet database not found.")
        return [], []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return [], []


def save_tweet_status(data, file_name="tweets.json"):
    """Save updated tweet statuses back to the database."""
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


def post_thread(client_v2, api_v1, tweets):
    """Post a thread of tweets."""
    if not tweets:
        print("No tweets available to post.")
        return

    thread_ids = []  # To store the thread's tweet IDs
    parent_tweet_id = None

    for tweet in tweets:
        tweet_text = tweet["tweet"]
        image_path = tweet["image"]

        # Validate image file
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue

        # Upload image
        media = api_v1.media_upload(image_path)
        if parent_tweet_id:
            response = client_v2.create_tweet(
                text=tweet_text,
                media_ids=[media.media_id_string],
                in_reply_to_tweet_id=parent_tweet_id,
            )
        else:
            response = client_v2.create_tweet(
                    text = tweet_text,
                    media_ids = [media.media_id_string],
                )

        tweet_id = response.data.get("id")
        # Post tweet (reply to previous tweet if part of a thread)
        print(f"Tweet posted: {tweet_id}")
        thread_ids.append(tweet_id)
        parent_tweet_id = tweet_id  # Set parent tweet ID for the next tweet
        time.sleep(5)

    
    print(f"Thread posted successfully")
    return thread_ids


def main():
    # Initialize Tweepy API (v1.1)
    auth = tweepy.OAuth1UserHandler(
        API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
    )
    api_v1 = tweepy.API(auth)

    # Load 5 new tweets for the thread
    tweets, data = load_new_tweets()
    client_v2 = initialize_client(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    if tweets:
        # Post the thread
        thread_ids = post_thread(client_v2, api_v1, tweets)

        # Mark the tweets as used
        for tweet in tweets:
            tweet["status"] = "used"

        # Save updated statuses back to the database
        save_tweet_status(data)

        print(f"Thread posted successfully! Tweet IDs: {thread_ids}")
    else:
        print("No new tweets to post.")

if __name__ == "__main__":
    main()
