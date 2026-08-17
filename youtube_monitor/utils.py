import re
import requests
from typing import Optional

def extract_video_id(url_or_id: str) -> str:

    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url_or_id
        )

        if match:
            return match.group(1)

    if re.match(
        r"^[A-Za-z0-9_-]{11}$",
        url_or_id.strip()
    ):
        return url_or_id.strip()

    return ""

def fetch_video_info(
    api_key,
    video_id
):

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/videos"
    )

    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("items"):
        return {}

    item = data["items"][0]

    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "views": item["statistics"].get(
            "viewCount",
            0
        ),
        "comment_count": item["statistics"].get(
            "commentCount",
            0
        )
    }

def get_live_chat_id(
    api_key,
    video_id
):

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/videos"
    )

    params = {
        "part": "liveStreamingDetails",
        "id": video_id,
        "key": api_key
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("items"):
        return None

    live_details = (
        data["items"][0]
        .get("liveStreamingDetails", {})
    )

    return live_details.get(
        "activeLiveChatId"
    )

def fetch_live_chat_messages(
    api_key,
    live_chat_id,
    page_token=None,
    max_results=50
):

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/liveChat/messages"
    )

    params = {
        "part": "snippet,authorDetails",
        "liveChatId": live_chat_id,
        "maxResults": min(
            max_results,
            2000
        ),
        "key": api_key
    }

    if page_token:
        params["pageToken"] = page_token

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise ValueError(
            data["error"]["message"]
        )

    messages = []

    for item in data.get("items", []):

        snippet = item.get(
            "snippet",
            {}
        )

        author = item.get(
            "authorDetails",
            {}
        )

        messages.append({
            "id": item.get("id"),

            "text": snippet.get(
                "displayMessage",
                ""
            ),

            "author": author.get(
                "displayName",
                "Anonymous"
            ),

            "published": snippet.get(
                "publishedAt",
                ""
            ),

            "is_moderator": author.get(
                "isChatModerator",
                False
            ),

            "is_owner": author.get(
                "isChatOwner",
                False
            )
        })

    return {
        "messages": messages,

        "next_page_token":
            data.get("nextPageToken"),

        "polling_interval":
            data.get(
                "pollingIntervalMillis",
                5000
            ) / 1000
    }

def detect_spike(
    history,
    window=10,
    threshold=0.35
):

    if len(history) < window + 2:
        return None

    recent = history[-window:]

    baseline = history[
        -(window * 3):-window
    ]

    if not baseline:
        return None

    recent_neg = (
        sum(
            1
            for item in recent
            if item["label"] == "NEG"
        )
        / len(recent)
    )

    base_neg = (
        sum(
            1
            for item in baseline
            if item["label"] == "NEG"
        )
        / len(baseline)
    )

    delta = recent_neg - base_neg

    if delta >= threshold:

        return {
            "recent_neg": recent_neg,
            "base_neg": base_neg,
            "delta": delta
        }

    return None