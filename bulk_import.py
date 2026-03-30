#!/usr/bin/env python3
"""Bulk-import wishlist items from a text file into the Vinyl Wishlist app."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_FILE = "wishlist.txt"
DEFAULT_URL = "http://localhost:8000"
VALID_TYPES = {"album", "artist", "label", "subject"}


def load_env_api_key() -> str:
    """Try to read API_KEY from .env file."""
    env_path = ".env"
    fallback = "change-me-please"

    if not os.path.exists(env_path):
        return fallback

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        return fallback

    return fallback


def parse_line(line: str) -> dict | None:
    """Parse 'album: Dark Side of the Moon' -> {"type": "album", "query": "Dark Side of the Moon"}"""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if ":" not in stripped:
        print(f"Warning: skipping invalid line (missing ':'): {stripped}")
        return None

    item_type_raw, query_raw = stripped.split(":", 1)
    item_type = item_type_raw.strip().lower()
    query = query_raw.strip()

    if item_type not in VALID_TYPES:
        print(f"Warning: skipping invalid type '{item_type}': {stripped}")
        return None

    if not query:
        print(f"Warning: skipping empty query: {stripped}")
        return None

    return {
        "type": item_type,
        "query": query,
        "notify_below_pct": 20.0,
        "notify_email": True,
    }


def post_bulk(base_url: str, api_key: str, items: list[dict]) -> int:
    """POST all items to /api/wishlist/bulk in one request. Returns count added."""
    url = f"{base_url.rstrip('/')}/api/wishlist/bulk"
    data = json.dumps(items).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("added", 0)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        print(f"HTTP error {e.code}: {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Bulk import wishlist items")
    parser.add_argument("--file", default=DEFAULT_FILE)
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()

    api_key = load_env_api_key()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file {args.file}: {e}")
        sys.exit(1)

    items = [item for line in lines if (item := parse_line(line)) is not None]

    if not items:
        print("No valid items found in file.")
        sys.exit(0)

    print(f"Importing {len(items)} items to {args.url}...")
    added = post_bulk(args.url, api_key, items)
    print(f"Done. {added} items added. Run 'Scan All' from the dashboard to fetch prices.")


if __name__ == "__main__":
    main()
