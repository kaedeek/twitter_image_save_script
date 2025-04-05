from dotenv import load_dotenv
import urllib.request
import tweepy
import os
import time

load_dotenv()

IMG_PATH = "./image/"

BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

def main(uid):
    tweet_count = 0
    total_images = 0
    pagination_token = None

    while True:
        try:
            tweets = client.get_users_tweets(
                id=uid,
                max_results=100,
                tweet_fields=["attachments", "created_at"],
                media_fields=["url"],
                expansions=["attachments.media_keys"],
                pagination_token=pagination_token
            )
        except tweepy.errors.TooManyRequests as e:
            print("Rate limit reached. Waiting before retrying...")
            time.sleep(15 * 60)  # Wait for 15 minutes
            continue

        if not tweets.data:
            print("Completed retrieving all tweets.")
            break

        media_dict = {m.media_key: m.url for m in tweets.includes["media"]} if "media" in tweets.includes else {}

        for tweet in tweets.data:
            if "attachments" in tweet and "media_keys" in tweet.attachments:
                for media_key in tweet.attachments["media_keys"]:
                    if media_key in media_dict:
                        Save(media_dict[media_key])
                        total_images += 1

        tweet_count += len(tweets.data)
        print(f"Processed {tweet_count} tweets, saved {total_images} images.")

        pagination_token = tweets.meta.get("next_token")
        if not pagination_token:
            break

def Save(url):
    ourl = f"{url}:orig"
    path = os.path.join(IMG_PATH, url.split("/")[-1])

    try:
        req = urllib.request.urlopen(ourl)
        with open(path, "wb") as f:
            f.write(req.read())
        print(f"Image saved successfully: {path}")
    except Exception as e:
        print(f"Save error: {e}")

if __name__ == "__main__":
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)

    username = "username"
    try:
        user_data = client.get_user(username=username)
        uid = user_data.data.id
    except Exception as e:
        print(f"Error retrieving user information: {e}")
        exit()

    main(uid)