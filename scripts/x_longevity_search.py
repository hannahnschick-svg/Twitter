#!/usr/bin/env python3
"""Fetch longevity-adjacent posts from X (Twitter) over the last N hours.

Reads config.py for keywords/accounts, calls the X API v2 recent-search
endpoint, dedupes results, and prints a JSON array of posts to stdout:

    [
      {
        "id": "...",
        "url": "https://x.com/<user>/status/<id>",
        "author": "<username>",
        "author_name": "<display name>",
        "text": "...",
        "created_at": "...",
        "matched": "keyword-or-account that triggered inclusion"
      },
      ...
    ]

"text" is the full post body: for long-form posts the API truncates the
top-level `text` field, so the complete `note_tweet.text` is preferred
whenever it's present.

Requires the X_BEARER_TOKEN environment variable (an X API app with
access to the recent-search endpoint -- Basic tier or higher).
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

SEARCH_URL = f"https://{config.API_HOST}/2/tweets/search/recent"
MAX_QUERY_LEN = 500  # stay under the API's 512-char limit with margin


def chunk_by_length(items, prefix_len, joiner_len=4, max_len=MAX_QUERY_LEN):
    """Group items into chunks whose joined length fits the query budget."""
    chunks, current, current_len = [], [], prefix_len
    for item in items:
        item_len = len(item) + joiner_len
        if current and current_len + item_len > max_len:
            chunks.append(current)
            current, current_len = [], prefix_len
        current.append(item)
        current_len += item_len
    if current:
        chunks.append(current)
    return chunks


def build_queries():
    suffix = f" {config.EXTRA_FILTERS}"
    queries = []

    for chunk in chunk_by_length(config.KEYWORDS, prefix_len=len(suffix)):
        body = " OR ".join(f'"{k}"' if " " in k else k for k in chunk)
        queries.append(("keyword", f"({body}){suffix}"))

    for chunk in chunk_by_length(
        [f"from:{a}" for a in config.ACCOUNTS], prefix_len=len(suffix)
    ):
        body = " OR ".join(chunk)
        queries.append(("account", f"({body}){suffix}"))

    return queries


def search(bearer_token, query, start_time, next_token=None):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": query,
        "start_time": start_time,
        "max_results": config.MAX_RESULTS_PER_CALL,
        # note_tweet carries the untruncated body of long-form posts.
        "tweet.fields": "created_at,author_id,note_tweet",
        "expansions": "author_id",
        "user.fields": "username,name",
    }
    if next_token:
        params["next_token"] = next_token

    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    if resp.status_code == 429:
        reset = int(resp.headers.get("x-rate-limit-reset", time.time() + 60))
        wait = max(reset - int(time.time()), 1)
        print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
        time.sleep(wait)
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def full_text(tweet):
    """Prefer the complete long-form body over the truncated preview."""
    note = tweet.get("note_tweet") or {}
    return note.get("text") or tweet["text"]


def main():
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        print(
            "ERROR: X_BEARER_TOKEN is not set. See README.md for how to get "
            "X API access and configure it.",
            file=sys.stderr,
        )
        sys.exit(1)

    start_time = (
        datetime.now(timezone.utc) - timedelta(hours=config.LOOKBACK_HOURS)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    posts_by_id = {}
    for label, query in build_queries():
        next_token = None
        for _ in range(config.MAX_PAGES_PER_QUERY):
            try:
                data = search(bearer_token, query, start_time, next_token)
            except requests.HTTPError as e:
                print(
                    f"Query failed ({label}): {e} -- {e.response.text}",
                    file=sys.stderr,
                )
                break

            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            for tweet in data.get("data", []):
                if tweet["id"] in posts_by_id:
                    continue
                user = users.get(tweet.get("author_id"), {})
                username = user.get("username", "i")
                posts_by_id[tweet["id"]] = {
                    "id": tweet["id"],
                    "url": f"https://x.com/{username}/status/{tweet['id']}",
                    "author": username,
                    "author_name": user.get("name", ""),
                    "text": full_text(tweet),
                    "created_at": tweet.get("created_at"),
                    "matched": label,
                }

            next_token = data.get("meta", {}).get("next_token")
            if not next_token:
                break

    posts = sorted(posts_by_id.values(), key=lambda p: p["created_at"] or "", reverse=True)
    print(json.dumps(posts, indent=2))


if __name__ == "__main__":
    main()
