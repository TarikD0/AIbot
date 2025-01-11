import json
import tweepy
import openai
import os
import requests


os.makedirs("images", exist_ok=True)




def post_tweet(tweet_text, image_path, parent_tweet_id=None):
    # Setup for v1.1 API for media upload
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    
    # Upload the media (image)
    with open(image_path, 'rb') as image_file:
        media = api.media_upload(media=image_file)
    
    # Setup for v2 API for tweet creation
    client = tweepy.Client(bearer_token=BEARER_TOKEN, 
                           consumer_key=API_KEY, 
                           consumer_secret=API_SECRET, 
                           access_token=ACCESS_TOKEN, 
                           access_token_secret=ACCESS_SECRET)
    
    # Post the tweet with the image
    if parent_tweet_id:
        response = client.create_tweet(text=tweet_text, media_ids=[media.media_id], in_reply_to_tweet_id=parent_tweet_id)
    else:
        response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])
    
    return response.data['id'] if response else None

    
def get_first_sentence(text):
    """Extract the first sentence from the given text."""
    return text.split('.')[0].strip() + '.' if '.' in text else text.strip()


def generate_thread_with_images(prompt, num_tweets=2):
    """Generate a thread of tweets with images based on a prompt."""
    thread = []
    for i in range(num_tweets):
        # Generate tweet text
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at writing engaging tweets about Christian figures."},
                {"role": "user", "content": f"{prompt} - Tweet {i+1}"}
            ]
        )
        tweet_text = response.choices[0].message.content.strip()

        short_prompt = get_first_sentence(tweet_text)

        # Generate image description based on tweet content
        image_prompt = f"Create an image related to: {short_prompt}"
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )

        # Download the image
        image_url = image_response.data[0].url
        image_path = f"images/tweet_{i+1}.png"
        save_image(image_url, image_path)

        # Add tweet and image info to the thread
        thread.append({"tweet": tweet_text, "image": image_path, "status": "new"})
    return thread

def save_image(url, path):
    """Download and save the image from the URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(path, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")


def save_to_database(thread, file_name="tweets.json"):
    """Save generated tweets with images to a JSON file."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.extend(thread)

    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


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

def mark_figure_as_used(figure_name, figures_data):
    """Mark the given Christian figure as used in the data."""
    for figure in figures_data:
        if figure['name'] == figure_name:
            figure['used'] = True
            break
    
    # Save the updated data back to the JSON file
    with open('christian_figures.json', 'w') as file:
        json.dump(figures_data, file, indent=4)

def main():
    # Initialize Tweepy client
    client = initialize_client(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    with open('topics.json', 'r') as file:
        christian_figures_data = json.load(file)

    unused_figure = next((figure for figure in christian_figures_data if not figure['used']), None)


    if unused_figure:
     figure_name = unused_figure['name']
     print(f"Generating new tweets about {figure_name} and saving to database...")
     prompt = f"Write a Twitter thread about {figure_name}."
     thread = generate_thread_with_images(prompt)
     # Save the thread to the database
     save_to_database(thread)
    # Post tweets from the generated thread
    thread_ids = []
    for i, tweet_data in enumerate(thread):
        tweet_text, image_path = tweet_data["tweet"], tweet_data["image"]
        print(f"Posting tweet {i+1}: {tweet_text} with image: {image_path}")
            # For the first tweet in the thread, there's no parent tweet ID
        if i == 0:
            response = post_tweet(client, tweet_text, image_path)
        else:
            # For subsequent tweets, pass the ID of the previous tweet to make a thread
            response = post_tweet(tweet_text, image_path, thread_ids[-1])
        if response:
            thread_ids.append(response)
            print("Tweet posted successfully.")
        else:
            print("Failed to post tweet.")
            # Optionally, you might want to break the loop if posting fails
            # break

        # Mark the figure as used and save back to the JSON file
    if thread_ids:  # Only if we successfully posted at least one tweet
        mark_figure_as_used(figure_name, christian_figures_data)
    else:
        print("Failed to post any tweets in the thread.")
   


if __name__ == "__main__":
    main()
