import json
import tweepy


def initialize_client(bearer_token, api_key, api_secret, access_token, access_secret):
    """Initialize the Tweepy client."""
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
    return client


def post_tweet(client, tweet_text, image_path):
    """Post a tweet with an image."""
    # Upload the media (image)
    media = client.media_upload(image_path)
    
    # Post the tweet with the image
    response = client.update_status(status=tweet_text, media_ids=[media.media_id_string])
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
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALYDxwEAAAAA6Uc1GuxpnewnIRCc0CfMJf6SDDs%3D9bNqIYGnOhNOwWXVG5TCOW4Sv1VoFBsJRVS0GVTgH1Et2MnoQH"
    API_KEY = "bzG4CpfP2HAZ7uTj2rgZAzDDo"
    API_SECRET = "vdrZ9xZbZzgirUHaTho8DNu6JzlVUXRRsiChkNdF1VCuAQiOFy"
    ACCESS_TOKEN = "592917190-HtqKpRHwz4sOvSZ8UkQyjqi6d8aKqr3ocwYoWv1G"
    ACCESS_SECRET = "lZbzxqlG3404p3hBn9aT5GbxQYLph5ItXhy7cJwZ2fpch"

    # Initialize Tweepy client
    client = initialize_client(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    # Post the next tweet from the database
    tweet_text, image_path, index = get_next_tweet()
    if tweet_text and image_path:
        print(f"Posting tweet: {tweet_text} with image: {image_path}")
        response_id = post_tweet(client, tweet_text, image_path)
        if response_id:
            print(f"Tweet posted successfully: {response_id}")
            mark_tweet_as_used(index)
        else:
            print("Failed to post tweet.")
    else:
        print("No new tweets to post.")
