# deletesky
Autodelete old Bluesky posts.
=======
# DeleteSky

A Python ATProto client to delete your old posts.

## Configuration

This tool is configured using environment variables.

### Required
*   `ATPROTO_USERNAME`: Your ATProto username.
*   `ATPROTO_PASSWORD`: Your ATProto app password.

### Optional
*   `DAYS_TO_KEEP`: How old posts should be before deleting (in days). Defaults to `14`.
*   `DELETE_REPOSTS`: Set to `True` to delete reposts, `False` otherwise. Defaults to `True`.
*   `DELETE_LIKES`: Set to `True` to delete likes, `False` otherwise. Defaults to `False`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Before running, make sure you have set the required environment variables.

```bash
export ATPROTO_USERNAME="your-username"
export ATPROTO_PASSWORD="your-app-password"

python -m deletesky.src.main
```
