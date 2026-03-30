import asyncio

import httpx

from app.config import settings

BASE_URL = "https://api.discogs.com"


def _get_headers() -> dict:
    return {
        "Authorization": f"Discogs token={settings.discogs_token}",
        "User-Agent": "VinylWishlist/1.0",
    }


async def _get_marketplace_listings(
    client: httpx.AsyncClient,
    release_id: int,
    title: str,
    max_results: int,
) -> list[dict]:
    """Fetch individual marketplace listings for a release, with ships_from."""
    resp = await client.get(
        f"{BASE_URL}/marketplace/search",
        params={
            "release_id": release_id,
            "sort": "price",
            "sort_order": "asc",
            "format": "Vinyl",
            "per_page": max_results,
        },
        headers=_get_headers(),
    )
    if resp.status_code != 200:
        return []

    listings = []
    for item in resp.json().get("listings", []):
        price_info = item.get("price", {})
        price = price_info.get("value")
        listing_id = item.get("id")
        if not listing_id or price is None:
            continue
        listings.append({
            "source": "discogs",
            "title": title,
            "price": float(price),
            "currency": price_info.get("currency", "USD"),
            "condition": item.get("condition"),
            "seller": (item.get("seller") or {}).get("username"),
            "ships_from": item.get("ships_from"),
            "url": f"https://www.discogs.com/sell/item/{listing_id}",
        })
    return listings


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5) -> list[dict]:
    if not settings.discogs_token:
        return []

    try:
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
            listings: list[dict] = []

            for result in results[:3]:
                release_id = result.get("id")
                title = result.get("title")
                if not release_id or not title:
                    continue

                new = await _get_marketplace_listings(client, release_id, title, max_results)
                listings.extend(new)
                if len(listings) >= max_results:
                    break
                await asyncio.sleep(0.5)

            return listings[:max_results]
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

            for release in releases[:5]:
                release_id = release.get("id") or release.get("main_release")
                title = release.get("title")
                if not release_id or not title:
                    continue

                new = await _get_marketplace_listings(client, release_id, title, max_results)
                listings.extend(new)
                if len(listings) >= max_results:
                    break
                await asyncio.sleep(0.5)

            return listings[:max_results]
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

            for release in releases[:5]:
                release_id = release.get("id")
                title = release.get("title")
                if not release_id or not title:
                    continue

                new = await _get_marketplace_listings(client, release_id, title, max_results)
                listings.extend(new)
                if len(listings) >= max_results:
                    break
                await asyncio.sleep(0.5)

            return listings[:max_results]
    except httpx.HTTPError as e:
        print(f"[Discogs] HTTP error in label search '{query}': {e}")
        return []
    except Exception as e:
        print(f"[Discogs] Error in label search '{query}': {e}")
        return []
