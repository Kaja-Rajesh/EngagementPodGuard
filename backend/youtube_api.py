import os
import requests
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

BASE_URL = "https://www.googleapis.com/youtube/v3"


# ==========================================
# GET YOUTUBE CHANNEL
# ==========================================

def get_channel_by_handle(handle: str):

    # Remove @ if the user enters @username
    handle = handle.strip().lstrip("@")

    url = f"{BASE_URL}/channels"

    params = {
        "part": "snippet,statistics,contentDetails",
        "forHandle": handle,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": response.text
        }

    data = response.json()

    if not data.get("items"):
        return {
            "status": "error",
            "message": "YouTube channel not found"
        }

    channel = data["items"][0]

    uploads_playlist_id = (
        channel["contentDetails"]
        ["relatedPlaylists"]
        ["uploads"]
    )

    return {
        "status": "success",
        "channel": {
            "id": channel["id"],
            "title": channel["snippet"]["title"],
            "description": channel["snippet"].get(
                "description",
                ""
            ),
            "published_at": channel["snippet"].get(
                "publishedAt"
            ),
            "thumbnail": channel["snippet"]
                ["thumbnails"]
                ["high"]
                ["url"],
            "subscribers": channel["statistics"].get(
                "subscriberCount"
            ),
            "views": channel["statistics"].get(
                "viewCount"
            ),
            "videos": channel["statistics"].get(
                "videoCount"
            ),
            "uploads_playlist_id": uploads_playlist_id
        }
    }

# ==========================================
# GET CHANNEL VIDEOS
# ==========================================

def get_channel_videos(
    channel_id: str,
    max_results: int = 20
):

    url = f"{BASE_URL}/search"

    params = {
        "part": "snippet",
        "channelId": channel_id,
        "type": "video",
        "order": "date",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": response.text
        }

    data = response.json()

    videos = []

    for item in data.get("items", []):

        video_id = item["id"]["videoId"]

        videos.append({
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "description": item["snippet"].get(
                "description",
                ""
            ),
            "published_at": item["snippet"].get(
                "publishedAt"
            ),
            "thumbnail": item["snippet"]
                ["thumbnails"]
                ["high"]
                ["url"]
        })

    return {
        "status": "success",
        "count": len(videos),
        "videos": videos
    }
# ==========================================
# GET VIDEO COMMENTS
# ==========================================

def get_video_comments(
    video_id: str,
    max_results: int = 50
):

    url = f"{BASE_URL}/commentThreads"

    params = {
        "part": "snippet,replies",
        "videoId": video_id,
        "maxResults": max_results,
        "textFormat": "plainText",
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": response.text
        }

    data = response.json()

    comments = []

    for item in data.get("items", []):

        top_comment = (
            item["snippet"]
            ["topLevelComment"]
            ["snippet"]
        )

        comments.append({
            "comment_id": item["snippet"]["topLevelComment"]["id"],
            "author": top_comment.get(
                "authorDisplayName",
                ""
            ),
            "author_channel_id": top_comment.get(
                "authorChannelId",
                {}
            ).get("value"),
            "text": top_comment.get(
                "textOriginal",
                top_comment.get("textDisplay", "")
            ),
            "like_count": top_comment.get(
                "likeCount",
                0
            ),
            "published_at": top_comment.get(
                "publishedAt"
            ),
            "updated_at": top_comment.get(
                "updatedAt"
            ),
            "reply_count": item["snippet"].get(
                "totalReplyCount",
                0
            )
        })

    return {
        "status": "success",
        "video_id": video_id,
        "count": len(comments),
        "comments": comments
    }