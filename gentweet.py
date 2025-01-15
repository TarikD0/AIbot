import json
import os
import requests
import openai

# Ensure the images directory exists
os.makedirs("images", exist_ok=True)

openai.api_key = "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"


import json

def get_next_topic(file_name="topics.json"):
    """Retrieve the next unused topic from the topics database."""
    try:
        print("trying")
        with open(file_name, "r") as f:
            print("we have opened file")
            content = f.read().strip()
            print("we have read") 
            if content:  # Check if the file is not empty
                topics = json.loads(content)  # This will fail if the content is invalid
                print("there is content")
            else:
                topics = []  # Initialize as an empty list if the file is empty
        print(f"Loaded topics: {topics}")

    except FileNotFoundError:
        print("No topics database found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    for index, topic in enumerate(topics):
        print(f"Checking topic: {topic}")
        if not topic["used"]:
            print(f"Found unused topic: {topic['name']}")
            return topic["name"], index  # Return the topic name and its index

    print("No unused topics available.")
    return None, None


def mark_topic_as_used(index, file_name="topics.json"):
    """Mark a topic as used in the topics database."""
    try:
        with open(file_name, "r") as f:
            topics = json.load(f)

        topics[index]["used"] = True

        with open(file_name, "w") as f:
            json.dump(topics, f, indent=4)
    except Exception as e:
        print(f"Error marking topic as used: {e}")

def get_first_sentence(text):
    """Extract the first sentence from the given text."""
    return text.split('.')[0].strip() + '.' if '.' in text else text.strip()


def save_image(url, path):
    """Download and save the image from the URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(path, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")


def generate_thread_with_images(prompt, topic, num_tweets=5):
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
        image_prompt = f"Create an artistic image related to: {short_prompt}"
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )

        # Download the image
        image_url = image_response.data[0].url
        image_path = f"images/{topic}_{i+1}.png"
        save_image(image_url, image_path)

        # Add tweet and image info to the thread
        thread.append({"tweet": tweet_text, "image": image_path, "status": "new"})
    return thread


def save_to_database(thread, file_name="tweets.json"):
    """Save generated tweets with images to a JSON file."""
    try:
        with open(file_name, "r") as f:
            # Read the content and ensure it's not empty
            content = f.read().strip()
            if content:  # Check if the file is not empty
                try:
                    data = json.loads(content)  # Try to load the JSON data
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {file_name}. Initializing with empty list.")
                    data = []  # Initialize as an empty list if decoding fails
            else:
                data = []  # Initialize as an empty list if the file is empty
    except FileNotFoundError:
        print(f"{file_name} not found. Initializing with empty list.")
        data = []  # Initialize as an empty list if the file doesn't exist

    # Add the new thread to the data
    data.extend(thread)

    # Save the data back to the file
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # Generate tweets with images and save to database
    print("hello")
    topic, index = get_next_topic()
    print("world")
    if topic:
        
        print(f"Generating tweets for topic: {topic}")
        
        prompt = f"Write a Twitter article about a key Christian figure like {topic}."
        thread = generate_thread_with_images(prompt, topic)
        save_to_database(thread)
        mark_topic_as_used(index)
        print(f"Marked topic '{topic}' as used.")

        print("Tweets saved to database.")
    else: 
        print("No topics to generate tweets for.")

