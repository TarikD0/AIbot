import json
import os
import requests
import openai

# Ensure the images directory exists
os.makedirs("images", exist_ok=True)

openai.api_key = "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"


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


def generate_thread_with_images(prompt, num_tweets=5):
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
        image_path = f"images/tweet_{i+1}.png"
        save_image(image_url, image_path)

        # Add tweet and image info to the thread
        thread.append({"tweet": tweet_text, "image": image_path, "status": "new"})
    return thread


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


if __name__ == "__main__":
    # Generate tweets with images and save to database
    print("Generating tweets...")
    prompt = "Write a Twitter article about a key Christian figure like St. Paul."
    thread = generate_thread_with_images(prompt)
    save_to_database(thread)
    print("Tweets saved to database.")
