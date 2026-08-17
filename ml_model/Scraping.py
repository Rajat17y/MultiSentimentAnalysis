"""
Multi-Platform Social Media Comment Scraper
============================================
Fetches comments from Reddit, HackerNews, YouTube, and Dev.to
for a given topic — all FREE, no paid subscriptions required.

Platforms & Auth:
  - Reddit       → No API key needed (public JSON API)
  - HackerNews   → No API key needed (Algolia search API)
  - YouTube      → Needs a FREE Google API key
                   Get one at: https://console.cloud.google.com
                   Enable "YouTube Data API v3" (free quota: 10,000 units/day)
  - Dev.to       → No API key needed (public REST API)

Usage:
    result = scrape_comments("artificial intelligence", youtube_api_key="YOUR_KEY")
    for platform, comments in result.items():
        print(f"\\n=== {platform} ({len(comments)} comments) ===")
        for c in comments[:3]:
            print(" -", c[:120])
"""

from __future__ import annotations

import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

num_comments = 100
# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CommentScraper/1.0; "
        "+https://github.com/comment-scraper)"
    )
}


def _get(url: str, extra_headers: Optional[dict] = None, timeout: int = 10) -> dict:
    """Simple HTTP GET that returns parsed JSON."""
    req = urllib.request.Request(url, headers={**HEADERS, **(extra_headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _truncate(text: str, max_len: int = 500) -> str:
    text = text.strip().replace("\n", " ")
    return text[:max_len] + "…" if len(text) > max_len else text


# ─────────────────────────────────────────────────────────────
#  Reddit  (public JSON API — no auth)
# ─────────────────────────────────────────────────────────────

def scrape_reddit(topic: str, target: int = num_comments) -> list[str]:
    """
    Search Reddit for posts matching the topic, then collect
    comments from the top posts until we have `target` comments.
    """
    comments: list[str] = []

    # 1. Find top posts
    search_url = (
        "https://www.reddit.com/search.json?"
        + urllib.parse.urlencode({
            "q": topic,
            "sort": "top",
            "t": "month",
            "limit": 10,
            "type": "link",
        })
    )
    data = _get(search_url)
    posts = data.get("data", {}).get("children", [])

    for post in posts:
        if len(comments) >= target:
            break

        pd = post.get("data", {})
        subreddit = pd.get("subreddit", "")
        post_id   = pd.get("id", "")
        if not subreddit or not post_id:
            continue

        # 2. Fetch comments for this post
        comments_url = (
            f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
            f"?limit=50&depth=1"
        )
        try:
            cdata = _get(comments_url)
            # cdata[1] contains the comment listing
            for child in cdata[1].get("data", {}).get("children", []):
                cd = child.get("data", {})
                body = cd.get("body", "").strip()
                if body and body != "[deleted]" and body != "[removed]":
                    comments.append(_truncate(body))
                if len(comments) >= target:
                    break
        except Exception:
            pass  # skip posts whose comment thread fails

        time.sleep(0.5)  # be polite to Reddit's servers

    return comments[:target]


# ─────────────────────────────────────────────────────────────
#  HackerNews  (Algolia search API — no auth)
# ─────────────────────────────────────────────────────────────

def scrape_hackernews(topic: str, target: int = num_comments) -> list[str]:
    """
    Use the Algolia HN Search API to find comments directly.
    https://hn.algolia.com/api
    """
    comments: list[str] = []
    page = 0

    while len(comments) < target:
        url = (
            "https://hn.algolia.com/api/v1/search?"
            + urllib.parse.urlencode({
                "query": topic,
                "tags":  "comment",
                "hitsPerPage": 50,
                "page": page,
            })
        )
        data = _get(url)
        hits = data.get("hits", [])
        if not hits:
            break

        for hit in hits:
            text = hit.get("comment_text") or ""
            # Strip basic HTML tags
            import re
            text = re.sub(r"<[^>]+>", "", text).strip()
            text = text.replace("&#x27;", "'").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
            if text:
                comments.append(_truncate(text))
            if len(comments) >= target:
                break

        page += 1
        if page >= data.get("nbPages", 1):
            break

    return comments[:target]


# ─────────────────────────────────────────────────────────────
#  YouTube  (Data API v3 — free quota, needs key)
# ─────────────────────────────────────────────────────────────

def scrape_youtube(topic: str, api_key: str, target: int = num_comments) -> list[str]:
    """
    1. Search for videos about the topic.
    2. Pull top-level comments from those videos.
    Requires a free Google Cloud API key with YouTube Data API v3 enabled.
    """
    comments: list[str] = []

    # 1. Search videos
    search_url = (
        "https://www.googleapis.com/youtube/v3/search?"
        + urllib.parse.urlencode({
            "part":       "id",
            "q":          topic,
            "type":       "video",
            "maxResults": 5,
            "order":      "relevance",
            "key":        api_key,
        })
    )
    search_data = _get(search_url)
    video_ids = [
        item["id"]["videoId"]
        for item in search_data.get("items", [])
        if item.get("id", {}).get("videoId")
    ]

    for vid_id in video_ids:
        if len(comments) >= target:
            break

        threads_url = (
            "https://www.googleapis.com/youtube/v3/commentThreads?"
            + urllib.parse.urlencode({
                "part":            "snippet",
                "videoId":         vid_id,
                "maxResults":      50,
                "order":           "relevance",
                "textFormat":      "plainText",
                "key":             api_key,
            })
        )
        try:
            ct_data = _get(threads_url)
            for item in ct_data.get("items", []):
                text = (
                    item.get("snippet", {})
                        .get("topLevelComment", {})
                        .get("snippet", {})
                        .get("textDisplay", "")
                        .strip()
                )
                if text:
                    comments.append(_truncate(text))
                if len(comments) >= target:
                    break
        except Exception:
            pass

    return comments[:target]


# ─────────────────────────────────────────────────────────────
#  Dev.to  (public REST API — no auth)
# ─────────────────────────────────────────────────────────────

def scrape_devto(topic: str, target: int = num_comments) -> list[str]:
    """
    Search Dev.to articles by tag/keyword, then fetch their comments.
    https://developers.forem.com/api
    """
    import re
    comments: list[str] = []

    # Search articles
    articles_url = (
        "https://dev.to/api/articles?"
        + urllib.parse.urlencode({
            "q":        topic,
            "per_page": 10,
            "state":    "rising",
        })
    )
    articles = _get(articles_url)

    for article in articles:
        if len(comments) >= target:
            break

        article_id = article.get("id")
        if not article_id:
            continue

        comments_url = f"https://dev.to/api/comments?a_id={article_id}"
        try:
            raw = _get(comments_url)
            # Flatten top-level + child comments
            def extract(nodes):
                for node in nodes:
                    body = re.sub(r"<[^>]+>", "", node.get("body_html", "")).strip()
                    if body:
                        yield body
                    yield from extract(node.get("children", []))

            for body in extract(raw):
                comments.append(_truncate(body))
                if len(comments) >= target:
                    break
        except Exception:
            pass

        time.sleep(0.3)

    return comments[:target]


# ─────────────────────────────────────────────────────────────
#  Main orchestrator
# ─────────────────────────────────────────────────────────────

def scrape_comments(
    topic: str,
    youtube_api_key: Optional[str] = None,
    comments_per_platform: int = num_comments,
) -> dict[str, list[str]]:
    """
    Scrape comments from multiple social platforms for a given topic.

    Parameters
    ----------
    topic                : Search term / hashtag / keyword
    youtube_api_key      : Optional. Free Google Cloud API key.
                           Without it, YouTube is silently skipped.
    comments_per_platform: Minimum target comments per platform (default 20).

    Returns
    -------
    dict  {platform_name: [comment, comment, ...]}
          Platforms with errors return an empty list (never raises).
    """
    results: dict[str, list[str]] = {}

    platforms = {
        "Reddit":      lambda: scrape_reddit(topic, comments_per_platform),
        "HackerNews":  lambda: scrape_hackernews(topic, comments_per_platform),
        "Dev.to":      lambda: scrape_devto(topic, comments_per_platform),
    }

    if youtube_api_key:
        platforms["YouTube"] = lambda: scrape_youtube(
            topic, youtube_api_key, comments_per_platform
        )

    for platform, fetcher in platforms.items():
        print(f"[{platform}] Fetching comments for '{topic}'…", flush=True)
        try:
            comments = fetcher()
            results[platform] = comments
            print(f"[{platform}] ✓ {len(comments)} comments fetched.")
        except urllib.error.HTTPError as e:
            print(f"[{platform}] ✗ HTTP {e.code}: {e.reason}")
            results[platform] = []
        except urllib.error.URLError as e:
            print(f"[{platform}] ✗ Network error: {e.reason}")
            results[platform] = []
        except Exception as e:
            print(f"[{platform}] ✗ Unexpected error: {e}")
            results[platform] = []

    return results


# ─────────────────────────────────────────────────────────────
#  CLI entry-point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "machine learning"

    # ── Optional: set your YouTube API key here ──────────────
    YOUTUBE_API_KEY = None   # e.g. "AIzaSy..."
    # ─────────────────────────────────────────────────────────

    print(f"\n{'='*55}")
    print(f"  Comment Scraper  |  topic: \"{topic}\"")
    print(f"{'='*55}\n")

    data = scrape_comments(
        topic,
        youtube_api_key=YOUTUBE_API_KEY,
        comments_per_platform=num_comments,
    )

    print(f"\n{'='*55}")
    for platform, comments in data.items():
        print(f"\n▶  {platform}  ({len(comments)} comments)")
        print("-" * 50)
        for i, c in enumerate(comments, 1):
            print(f"  {i:>2}. {c[:120]}")

    print(f"\n{'='*55}")
    print(f"  Total comments: {sum(len(v) for v in data.values())}")
    print(f"{'='*55}\n")