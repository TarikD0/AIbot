import json
import tweepy

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


def post_tweet(client_v2, api_v1, tweet_text, image_path):

    """Post a tweet with an image."""
    # Upload the media (image)
    media = api_v1.media_upload(image_path)
    
    # Post the tweet with the image
    response = client_v2.create_tweet(
        text=tweet_text,
        media_ids=[media.media_id_string]
    )
    print("Tweet posted successfully!")
    return response.id  # Return the tweet ID if successful
    


def get_next_tweet(file_name="tweets.json"):
    """Retrieve the next unused tweet with image from the JSON database."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No tweet database found.")
        return None, None, None

    for index, entry in enumerate(data):
        if entry["status"] == "new":
            return entry["tweet"], entry["image"], index  # Return tweet, image path, and index

    print("No new tweets available.")
    return None, None, None


def mark_tweet_as_used(index, file_name="tweets.json"):
    """Mark a tweet as used in the JSON database."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)

        data[index]["status"] = "used"

        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error marking tweet as used: {e}")


if __name__ == "__main__":
    # Set your Twitter API credentials
    
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api_v1 = tweepy.API(auth)

    # Initialize Tweepy client
    client_v2 = initialize_client(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    # Post the next tweet from the database
    tweet_text, image_path, index = get_next_tweet()
    if tweet_text and image_path:
        print(f"Posting tweet: {tweet_text} with image: {image_path}")
        response_id = post_tweet(client_v2, api_v1, tweet_text, image_path)
        if response_id:
            print(f"Tweet posted successfully: {response_id}")
            mark_tweet_as_used(index)
        else:
            print("Failed to post tweet.")
    else:
        print("No new tweets to post.")
