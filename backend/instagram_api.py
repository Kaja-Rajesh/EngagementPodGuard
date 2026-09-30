import os
import requests
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)
load_dotenv()

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

BASE_URL = "https://graph.instagram.com"


# ==========================================
# GET INSTAGRAM PROFILE
# ==========================================

def get_instagram_profile():

    url = f"{BASE_URL}/me"

    params = {
        "fields": "id,username,name,account_type,profile_picture_url",
        "access_token": INSTAGRAM_ACCESS_TOKEN
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

    return {
        "status": "success",
        "profile": data
    }


# ==========================================
# GET INSTAGRAM MEDIA
# ==========================================

def get_instagram_media(limit: int = 20):

    url = f"{BASE_URL}/me/media"

    params = {
        "fields": (
            "id,"
            "caption,"
            "media_type,"
            "media_url,"
            "permalink,"
            "thumbnail_url,"
            "timestamp,"
            "like_count,"
            "comments_count"
        ),
        "limit": limit,
        "access_token": INSTAGRAM_ACCESS_TOKEN
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

    media = []

    for item in data.get("data", []):

        media.append({
            "id": item.get("id"),
            "caption": item.get("caption"),
            "media_type": item.get("media_type"),
            "media_url": item.get("media_url"),
            "permalink": item.get("permalink"),
            "thumbnail_url": item.get("thumbnail_url"),
            "timestamp": item.get("timestamp"),
            "like_count": item.get("like_count", 0),
            "comments_count": item.get(
                "comments_count",
                0
            )
        })

    return {
        "status": "success",
        "count": len(media),
        "media": media
    }