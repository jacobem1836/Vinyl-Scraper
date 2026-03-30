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


def post_item(base_url: str, api_key: str, item: dict, scan: bool = False) -> bool:
    """POST to /api/wishlist. Returns True on success."""
    url = f"{base_url.rstrip('/')}/api/wishlist?scan={'true' if scan else 'false'}"
    data = json.dumps(item).encode("utf-8")
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
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        if body:
            print(f"HTTP error {e.code} for {item['type']}: {item['query']} - {body}")
        else:
            print(f"HTTP error {e.code} for {item['type']}: {item['query']}")
        return False
    except urllib.error.URLError as e:
        print(f"Connection error for {item['type']}: {item['query']} - {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for {item['type']}: {item['query']} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Bulk import wishlist items")
    parser.add_argument("--file", default=DEFAULT_FILE)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--scan", action="store_true", default=False,
                        help="Trigger a scan for each item on import (slow). Default: no scan.")
    args = parser.parse_args()

    api_key = load_env_api_key()

    print(f"Importing from {args.file} to {args.url}...")

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file {args.file}: {e}")
        sys.exit(1)

    added = 0
    failed = 0

    for line in lines:
        item = parse_line(line)
        if item is None:
            continue

        ok = post_item(args.url, api_key, item, scan=args.scan)
        if ok:
            added += 1
            print(f"✓ Added: {item['type']}: {item['query']}")
        else:
            failed += 1
            print(f"✗ Failed: {item['type']}: {item['query']}")

    print(f"Done. {added} added, {failed} failed.")


if __name__ == "__main__":
    main()
