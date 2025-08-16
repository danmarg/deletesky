# deletesky/src/main.py

import datetime
import os
import sys
import time
from atproto import Client, Request
from atproto_client.exceptions import InvokeTimeoutError
from httpx import Timeout

USERNAME = os.getenv("BSKY_USERNAME")
PASSWORD = os.getenv("BSKY_PASSWORD")
DAYS_TO_KEEP = int(os.getenv("BSKY_DAYS_TO_KEEP", "14"))
DELETE_REPOSTS = os.getenv("BSKY_DELETE_REPOSTS", "True").lower() == "true"
DELETE_LIKES = os.getenv("BSKY_DELETE_LIKES", "True").lower() == "true"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def main():
    if not USERNAME or not PASSWORD:
        print("Error: ATPROTO_USERNAME and ATPROTO_PASSWORD environment variables must be set.")
        sys.exit(1)

    custom_request = Request(timeout=Timeout(timeout=30.0))
    client = Client(request=custom_request)
    client.login(USERNAME, PASSWORD)

    print(f"Successfully logged in as {USERNAME}")

    # Calculate the date to delete posts from
    delete_before_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DAYS_TO_KEEP)

    print(f"Deleting content older than {delete_before_date.isoformat()}")

    for retry in range(MAX_RETRIES):
        try:
            profile = client.get_profile(client.me.handle)

            # Delete posts
            response = client.app.bsky.feed.get_author_feed({'actor': profile.did})
            for post in response.feed:
                post_record = post.post.record
                post_uri = post.post.uri
                if post_record.created_at < delete_before_date.isoformat():
                    print(f"Deleting post: {post_record.text}")
                    client.delete_post(post_uri)

            # Delete reposts
            if DELETE_REPOSTS:
                reposts = client.com.atproto.repo.list_records(
                    {"repo": profile.did, "collection": "app.bsky.feed.repost"}
                )
                for repost in reposts.records:
                    if repost.value.created_at < delete_before_date.isoformat():
                        print(f"Deleting repost: {repost.uri}")
                        client.delete_repost(repost.uri)

            # Delete likes
            if DELETE_LIKES:
                likes = client.com.atproto.repo.list_records(
                    {"repo": profile.did, "collection": "app.bsky.feed.like"}
                )
                for like in likes.records:
                    if like.value.created_at < delete_before_date.isoformat():
                        print(f"Deleting like: {like.uri}")
                        client.delete_like(like.uri)

            break  # Success, exit retry loop

        except InvokeTimeoutError:
            print(f"Attempt {retry + 1} of {MAX_RETRIES} timed out. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


if __name__ == "__main__":
    main()
