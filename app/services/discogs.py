import asyncio

import httpx

from app.services.http import USER_AGENT

from app.config import settings

BASE_URL = "https://api.discogs.com"

# Discogs enforces ~60 authenticated requests/min per token. Bound how many items can
# be scanning Discogs concurrently so a busy scan_all_items run doesn't blow the budget.
_semaphore = asyncio.Semaphore(2)


def _get_headers() -> dict:
    return {
        "Authorization": f"Discogs token={settings.discogs_token}",
        "User-Agent": USER_AGENT,
    }


async def _get(client: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response | None:
    """GET with Discogs rate-limit awareness: retries once on 429, and throttles
    when the remaining budget in the current 60s window gets low."""
    try:
        resp = await client.get(url, params=params, headers=_get_headers())
    except httpx.HTTPError as e:
        print(f"[Discogs] Request error for {url}: {e}")
        return None

    if resp.status_code == 429:
        print(f"[Discogs] 429 rate limited on {url}, sleeping 60s and retrying once")
        await asyncio.sleep(60)
        try:
            resp = await client.get(url, params=params, headers=_get_headers())
        except httpx.HTTPError as e:
            print(f"[Discogs] Request error on retry for {url}: {e}")
            return None

    remaining = resp.headers.get("X-Discogs-Ratelimit-Remaining")
    if remaining is not None:
        try:
            if int(remaining) < 5:
                print(f"[Discogs] Ratelimit remaining low ({remaining}), sleeping 60s for window reset")
                await asyncio.sleep(60)
        except ValueError:
            pass

    return resp


def _build_listing(title: str, release_id: int, stats: dict) -> dict:
    num_for_sale = stats.get("num_for_sale", 0)
    blocked = stats.get("blocked_from_sale", False)
    lowest = stats.get("lowest_price") or {}
    is_in_stock = num_for_sale > 0 and not blocked

    price = float(lowest["value"]) if is_in_stock and lowest.get("value") is not None else None
    currency = lowest.get("currency") if is_in_stock and lowest.get("currency") else "AUD"

    return {
        "source": "discogs",
        "title": title,
        "price": price,
        "currency": currency,
        "condition": None,
        "seller": None,
        # Discogs has no official public endpoint for individual marketplace listings
        # (the previously used one was an undocumented, unofficial endpoint). Leave
        # ships_from unset here -- the landed-cost layer applies its own fallback.
        "ships_from": None,
        "is_in_stock": is_in_stock,
        "url": f"https://www.discogs.com/sell/list?release_id={release_id}&sort=price%2Casc",
    }


async def _get_marketplace_stats(client: httpx.AsyncClient, release_id: int) -> dict | None:
    resp = await _get(client, f"{BASE_URL}/marketplace/stats/{release_id}", params={"curr_abbr": "AUD"})
    if resp is None or resp.status_code != 200:
        return None
    return resp.json()


async def typeahead_search(query: str, item_type: str = "album", max_results: int = 5) -> list[dict]:
    """Search Discogs for typeahead suggestions. Supports album (release), artist, and label types."""
    if not settings.discogs_token:
        return []
    async with _semaphore:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                if item_type == "artist":
                    params = {"q": query, "type": "artist", "per_page": max_results}
                elif item_type == "label":
                    params = {"q": query, "type": "label", "per_page": max_results}
                else:
                    # album (default)
                    params = {"q": query, "type": "release", "format": "Vinyl", "per_page": max_results}

                resp = await _get(client, f"{BASE_URL}/database/search", params=params)
                if resp is None or resp.status_code != 200:
                    return []
                results = resp.json().get("results", [])
                suggestions = []
                for r in results[:max_results]:
                    if item_type in ("artist", "label"):
                        # Artist/label results: title is just the name, no " - " split
                        suggestions.append({
                            "release_id": r.get("id"),
                            "title": r.get("title", "").strip(),
                            "artist": "",
                            "year": None,
                            "thumb": r.get("thumb") or r.get("cover_image") or None,
                        })
                    else:
                        raw_title = r.get("title", "")
                        # Discogs release title field is "Artist - Title"; split on first " - "
                        if " - " in raw_title:
                            artist, title = raw_title.split(" - ", 1)
                        else:
                            artist = ""
                            title = raw_title
                        year = r.get("year")
                        if not year or str(year) == "0":
                            year = None
                        suggestions.append({
                            "release_id": r.get("id"),
                            "title": title.strip(),
                            "artist": artist.strip(),
                            "year": str(year) if year else None,
                            "thumb": r.get("thumb") or r.get("cover_image") or None,
                        })
                return suggestions
        except Exception as e:
            print(f"[Discogs] Typeahead error: {e}")
            return []


async def _get_release_listings(client: httpx.AsyncClient, release_id: int) -> list[dict]:
    """Fetch a listing for a specific pinned Discogs release ID: 1 release call
    (title/artwork) + 1 marketplace stats call (pricing)."""
    try:
        detail_resp = await _get(client, f"{BASE_URL}/releases/{release_id}")
        if detail_resp is None or detail_resp.status_code != 200:
            return []
        detail = detail_resp.json()
        title = detail.get("title", "")

        cover_uri = None
        images = detail.get("images", [])
        if images:
            cover_uri = images[0].get("uri") or images[0].get("uri150")

        stats = await _get_marketplace_stats(client, release_id)
        if stats is None:
            return []

        listing = _build_listing(title=title, release_id=release_id, stats=stats)
        if cover_uri:
            listing["_cover_image"] = cover_uri
        return [listing]
    except Exception as e:
        print(f"[Discogs] Error fetching release {release_id}: {e}")
        return []


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5, discogs_release_id: int | None = None) -> list[dict]:
    if not settings.discogs_token:
        return []

    async with _semaphore:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                if discogs_release_id is not None and item_type in ("album", "subject"):
                    return await _get_release_listings(client, discogs_release_id)
                if item_type in ("album", "subject"):
                    return await _get_album_listings(client, query, max_results)
                if item_type == "artist":
                    return await _get_artist_listings(client, query, max_results)
                if item_type == "label":
                    return await _get_label_listings(client, query, max_results)
                return []
        except Exception as e:
            print(f"[Discogs] Error scanning '{query}': {e}")
            return []


async def _get_album_listings(client: httpx.AsyncClient, query: str, max_results: int) -> list[dict]:
    """1 search call + at most 3 marketplace stats calls (one per top search result)."""
    try:
        search_resp = await _get(
            client,
            f"{BASE_URL}/database/search",
            params={"q": query, "type": "release", "format": "Vinyl", "per_page": 5},
        )
        if search_resp is None or search_resp.status_code != 200:
            return []

        results = search_resp.json().get("results", [])
        listings: list[dict] = []
        cover_uri = None

        for result in results[:3]:
            release_id = result.get("id")
            title = result.get("title")
            if not release_id or not title:
                continue

            stats = await _get_marketplace_stats(client, release_id)
            if stats is None:
                continue

            listings.append(_build_listing(title=title, release_id=release_id, stats=stats))
            if cover_uri is None:
                cover_uri = result.get("cover_image") or result.get("thumb")

            if len(listings) >= max_results:
                break

        if listings and cover_uri:
            listings[0]["_cover_image"] = cover_uri
        return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in album search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in album search '{query}': {e}")
        return []


async def _get_artist_listings(client: httpx.AsyncClient, query: str, max_results: int) -> list[dict]:
    try:
        search_resp = await _get(
            client,
            f"{BASE_URL}/database/search",
            params={"q": query, "type": "artist", "per_page": 3},
        )
        if search_resp is None or search_resp.status_code != 200:
            return []

        artist_results = search_resp.json().get("results", [])
        if not artist_results:
            return []

        first_thumb = artist_results[0].get("thumb") if artist_results else None
        artist_id = artist_results[0].get("id")
        if not artist_id:
            return []

        releases_resp = await _get(
            client,
            f"{BASE_URL}/artists/{artist_id}/releases",
            params={"per_page": 10, "sort": "year", "sort_order": "desc"},
        )
        if releases_resp is None or releases_resp.status_code != 200:
            return []

        releases = releases_resp.json().get("releases", [])
        listings: list[dict] = []
        cover_uri = None

        for release in releases[:5]:
            release_id = release.get("id") or release.get("main_release")
            title = release.get("title")
            if not release_id or not title:
                continue

            stats = await _get_marketplace_stats(client, release_id)
            if stats is None:
                continue

            listings.append(_build_listing(title=title, release_id=release_id, stats=stats))
            if cover_uri is None:
                cover_uri = release.get("thumb")

            if len(listings) >= max_results:
                break

        if listings and (cover_uri or first_thumb):
            listings[0]["_cover_image"] = cover_uri or first_thumb
        return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in artist search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in artist search '{query}': {e}")
        return []


async def _get_label_listings(client: httpx.AsyncClient, query: str, max_results: int) -> list[dict]:
    try:
        search_resp = await _get(
            client,
            f"{BASE_URL}/database/search",
            params={"q": query, "type": "label", "per_page": 3},
        )
        if search_resp is None or search_resp.status_code != 200:
            return []

        label_results = search_resp.json().get("results", [])
        if not label_results:
            return []

        first_thumb = label_results[0].get("thumb") if label_results else None
        label_id = label_results[0].get("id")
        if not label_id:
            return []

        releases_resp = await _get(
            client,
            f"{BASE_URL}/labels/{label_id}/releases",
            params={"per_page": 10},
        )
        if releases_resp is None or releases_resp.status_code != 200:
            return []

        releases = releases_resp.json().get("releases", [])
        listings: list[dict] = []
        cover_uri = None

        for release in releases[:5]:
            release_id = release.get("id")
            title = release.get("title")
            if not release_id or not title:
                continue

            stats = await _get_marketplace_stats(client, release_id)
            if stats is None:
                continue

            listings.append(_build_listing(title=title, release_id=release_id, stats=stats))
            if cover_uri is None:
                cover_uri = release.get("thumb")

            if len(listings) >= max_results:
                break

        if listings and (cover_uri or first_thumb):
            listings[0]["_cover_image"] = cover_uri or first_thumb
        return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in label search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in label search '{query}': {e}")
        return []
