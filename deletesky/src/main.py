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

def delete_records(client, did, collection, delete_before_date, delete_fn, type_name):
    """Helper to delete records from a collection with pagination."""
    cursor = None
    deleted_count = 0
    while True:
        try:
            response = client.com.atproto.repo.list_records(
                repo=did,
                collection=collection,
                cursor=cursor,
                limit=100
            )
            for record in response.records:
                try:
                    created_at_str = getattr(record.value, 'created_at', None)
                    if not created_at_str:
                        continue

                    # Parse ISO 8601 string to datetime object
                    created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))

                    if created_at < delete_before_date:
                        if hasattr(record.value, 'text'):
                            print(f"Deleting {type_name}: {record.value.text[:50]}...")
                        else:
                            print(f"Deleting {type_name}: {record.uri}")

                        delete_fn(record.uri)
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {type_name} {record.uri}: {e}")

            if not response.cursor:
                break
            cursor = response.cursor
        except Exception as e:
            print(f"Error listing records for {collection}: {e}")
            break
    return deleted_count


def main():
    if not USERNAME or not PASSWORD:
        print("Error: BSKY_USERNAME and BSKY_PASSWORD environment variables must be set.")
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
            did = client.me.did

            # Delete posts
            print("Checking posts...")
            delete_records(client, did, "app.bsky.feed.post", delete_before_date, client.delete_post, "post")

            # Delete reposts
            if DELETE_REPOSTS:
                print("Checking reposts...")
                delete_records(client, did, "app.bsky.feed.repost", delete_before_date, client.delete_repost, "repost")

            # Delete likes
            if DELETE_LIKES:
                print("Checking likes...")
                delete_records(client, did, "app.bsky.feed.like", delete_before_date, client.delete_like, "like")

            break  # Success, exit retry loop

        except InvokeTimeoutError:
            print(f"Attempt {retry + 1} of {MAX_RETRIES} timed out. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


if __name__ == "__main__":
    main()
