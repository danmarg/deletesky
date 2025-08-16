# deletesky
Autodelete old Bluesky posts.
=======
# DeleteSky

A Python ATProto client to delete your old posts.

## Configuration

This tool is configured using environment variables.

### Required
*   `BSKY_USERNAME`: Your Bluesky username.
*   `BSKY_PASSWORD`: Your Bluesky app password.

### Optional
*   `BSKY_DAYS_TO_KEEP`: How old posts should be before deleting (in days). Defaults to `14`.
*   `BSKY_DELETE_REPOSTS`: Set to `True` to delete reposts, `False` otherwise. Defaults to `True`.
*   `BSKY_DELETE_LIKES`: Set to `True` to delete likes, `False` otherwise. Defaults to `True`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Before running, make sure you have set the required environment variables.

```bash
export BSKY_USERNAME="your-username"
export BSKY_PASSWORD="your-app-password"

python deletesky/src/main.py
```
