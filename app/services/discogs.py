import asyncio

import httpx

from app.config import settings

BASE_URL = "https://api.discogs.com"


def _get_headers() -> dict:
    return {
        "Authorization": f"Discogs token={settings.discogs_token}",
        "User-Agent": "VinylWishlist/1.0",
    }


def _build_listing(title: str, release_id: int, lowest_price: float) -> dict:
    return {
        "source": "discogs",
        "title": title,
        "price": float(lowest_price),
        "currency": "USD",
        "condition": None,
        "seller": None,
        "ships_from": None,
        "url": f"https://www.discogs.com/sell/list?release_id={release_id}&sort=price%2Casc",
    }


async def typeahead_search(query: str, max_results: int = 5) -> list[dict]:
    """Search Discogs releases for typeahead suggestions. Returns up to max_results results, 1 API call only."""
    if not settings.discogs_token:
        return []
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                f"{BASE_URL}/database/search",
                params={"q": query, "type": "release", "format": "Vinyl", "per_page": max_results},
                headers=_get_headers(),
            )
            if resp.status_code != 200:
                return []
            results = resp.json().get("results", [])
            suggestions = []
            for r in results[:max_results]:
                raw_title = r.get("title", "")
                # Discogs title field is "Artist - Title"; split on first " - "
                if " - " in raw_title:
                    artist, title = raw_title.split(" - ", 1)
                else:
                    artist = ""
                    title = raw_title
                year = r.get("year")
                if not year or str(year) == "0":
                    year = None
                thumb = r.get("thumb") or r.get("cover_image") or None
                suggestions.append({
                    "release_id": r.get("id"),
                    "title": title.strip(),
                    "artist": artist.strip(),
                    "year": str(year) if year else None,
                    "thumb": thumb,
                })
            return suggestions
    except Exception as e:
        print(f"[Discogs] Typeahead error: {e}")
        return []


async def _get_release_listings(release_id: int, max_results: int = 5) -> list[dict]:
    """Fetch listings for a specific Discogs release ID (pinned release path)."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                f"{BASE_URL}/releases/{release_id}",
                headers=_get_headers(),
            )
            if resp.status_code != 200:
                return []
            detail = resp.json()
            num_for_sale = detail.get("num_for_sale", 0)
            lowest_price = detail.get("lowest_price")
            title = detail.get("title", "")
            listings: list[dict] = []
            cover_uri = None
            images = detail.get("images", [])
            if images:
                cover_uri = images[0].get("uri") or images[0].get("uri150")
            if num_for_sale > 0 and lowest_price is not None:
                listing = _build_listing(title=title, release_id=release_id, lowest_price=lowest_price)
                if cover_uri:
                    listing["_cover_image"] = cover_uri
                listings.append(listing)
            return listings
    except Exception as e:
        print(f"[Discogs] Error fetching release {release_id}: {e}")
        return []


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5, discogs_release_id: int | None = None) -> list[dict]:
    if not settings.discogs_token:
        return []

    try:
        if discogs_release_id is not None and item_type in ("album", "subject"):
            return await _get_release_listings(discogs_release_id, max_results)
        if item_type in ("album", "subject"):
            return await _get_album_listings(query, max_results)
        if item_type == "artist":
            return await _get_artist_listings(query, max_results)
        if item_type == "label":
            return await _get_label_listings(query, max_results)
        return []
    except Exception as e:
        print(f"[Discogs] Error scanning '{query}': {e}")
        return []


async def _get_album_listings(query: str, max_results: int) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            search_resp = await client.get(
                f"{BASE_URL}/database/search",
                params={"q": query, "type": "release", "format": "Vinyl", "per_page": 5},
                headers=_get_headers(),
            )
            if search_resp.status_code != 200:
                return []

            results = search_resp.json().get("results", [])
            first_thumb = results[0].get("thumb") if results else None
            listings: list[dict] = []
            cover_uri = None

            for result in results[:3]:
                release_id = result.get("id")
                title = result.get("title")
                if not release_id or not title:
                    continue

                detail_resp = await client.get(
                    f"{BASE_URL}/releases/{release_id}",
                    headers=_get_headers(),
                )
                if detail_resp.status_code != 200:
                    await asyncio.sleep(0.5)
                    continue

                detail = detail_resp.json()
                if cover_uri is None:
                    images = detail.get("images", [])
                    if images:
                        cover_uri = images[0].get("uri") or images[0].get("uri150")
                num_for_sale = detail.get("num_for_sale", 0)
                lowest_price = detail.get("lowest_price")

                if num_for_sale > 0 and lowest_price is not None:
                    listings.append(_build_listing(title=title, release_id=release_id, lowest_price=lowest_price))
                    if len(listings) >= max_results:
                        break

                await asyncio.sleep(0.5)

            if listings and (cover_uri or first_thumb):
                listings[0]["_cover_image"] = cover_uri or first_thumb
            return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in album search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in album search '{query}': {e}")
        return []


async def _get_artist_listings(query: str, max_results: int) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            search_resp = await client.get(
                f"{BASE_URL}/database/search",
                params={"q": query, "type": "artist", "per_page": 3},
                headers=_get_headers(),
            )
            if search_resp.status_code != 200:
                return []

            artist_results = search_resp.json().get("results", [])
            if not artist_results:
                return []

            first_thumb = artist_results[0].get("thumb") if artist_results else None
            artist_id = artist_results[0].get("id")
            if not artist_id:
                return []

            releases_resp = await client.get(
                f"{BASE_URL}/artists/{artist_id}/releases",
                params={"per_page": 10, "sort": "year", "sort_order": "desc"},
                headers=_get_headers(),
            )
            if releases_resp.status_code != 200:
                return []

            releases = releases_resp.json().get("releases", [])
            listings: list[dict] = []
            cover_uri = None

            for release in releases[:5]:
                release_id = release.get("id") or release.get("main_release")
                title = release.get("title")
                if not release_id or not title:
                    continue

                detail_resp = await client.get(
                    f"{BASE_URL}/releases/{release_id}",
                    headers=_get_headers(),
                )
                if detail_resp.status_code != 200:
                    await asyncio.sleep(0.5)
                    continue

                detail = detail_resp.json()
                if cover_uri is None:
                    images = detail.get("images", [])
                    if images:
                        cover_uri = images[0].get("uri") or images[0].get("uri150")
                num_for_sale = detail.get("num_for_sale", 0)
                lowest_price = detail.get("lowest_price")

                if num_for_sale > 0 and lowest_price is not None:
                    listings.append(_build_listing(title=title, release_id=release_id, lowest_price=lowest_price))
                    if len(listings) >= max_results:
                        break

                await asyncio.sleep(0.5)

            if listings and (cover_uri or first_thumb):
                listings[0]["_cover_image"] = cover_uri or first_thumb
            return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in artist search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in artist search '{query}': {e}")
        return []


async def _get_label_listings(query: str, max_results: int) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            search_resp = await client.get(
                f"{BASE_URL}/database/search",
                params={"q": query, "type": "label", "per_page": 3},
                headers=_get_headers(),
            )
            if search_resp.status_code != 200:
                return []

            label_results = search_resp.json().get("results", [])
            if not label_results:
                return []

            first_thumb = label_results[0].get("thumb") if label_results else None
            label_id = label_results[0].get("id")
            if not label_id:
                return []

            releases_resp = await client.get(
                f"{BASE_URL}/labels/{label_id}/releases",
                params={"per_page": 10},
                headers=_get_headers(),
            )
            if releases_resp.status_code != 200:
                return []

            releases = releases_resp.json().get("releases", [])
            listings: list[dict] = []
            cover_uri = None

            for release in releases[:5]:
                release_id = release.get("id")
                title = release.get("title")
                if not release_id or not title:
                    continue

                detail_resp = await client.get(
                    f"{BASE_URL}/releases/{release_id}",
                    headers=_get_headers(),
                )
                if detail_resp.status_code != 200:
                    await asyncio.sleep(0.5)
                    continue

                detail = detail_resp.json()
                if cover_uri is None:
                    images = detail.get("images", [])
                    if images:
                        cover_uri = images[0].get("uri") or images[0].get("uri150")
                num_for_sale = detail.get("num_for_sale", 0)
                lowest_price = detail.get("lowest_price")

                if num_for_sale > 0 and lowest_price is not None:
                    listings.append(_build_listing(title=title, release_id=release_id, lowest_price=lowest_price))
                    if len(listings) >= max_results:
                        break

                await asyncio.sleep(0.5)

            if listings and (cover_uri or first_thumb):
                listings[0]["_cover_image"] = cover_uri or first_thumb
            return listings
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in label search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in label search '{query}': {e}")
        return []
