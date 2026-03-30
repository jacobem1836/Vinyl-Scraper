from __future__ import annotations

import asyncio
from typing import Any

import httpx

STORES: list[dict[str, str]] = [
    {
        "key": "thevinylstore",
        "name": "The Vinyl Store",
        "base_url": "https://www.thevinylstore.com.au",
    },
    {
        "key": "dutchvinyl",
        "name": "Dutch Vinyl",
        "base_url": "https://www.dutchvinyl.com.au",
    },
    {
        "key": "strangeworld",
        "name": "Strangeworld Records",
        "base_url": "https://www.strangeworldrecords.com.au",
    },
    {
        "key": "goldmine",
        "name": "Goldmine Records",
        "base_url": "https://www.goldminerecords.com.au",
    },
    {
        "key": "utopia",
        "name": "Utopia Records",
        "base_url": "https://utopia.com.au",
    },
    {
        "key": "umusic",
        "name": "uMusic Shop AU",
        "base_url": "https://shop.umusic.com.au",
    },
]

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


async def _search_store(
    client: httpx.AsyncClient,
    store: dict[str, str],
    query: str,
    max_results: int,
) -> list[dict[str, Any]]:
    base_url = store["base_url"]

    try:
        response = await client.get(
            f"{base_url}/search/suggest.json",
            params={
                "q": query,
                "resources[type]": "product",
                "resources[limit]": max_results,
            },
        )
        response.raise_for_status()
        products = response.json()["resources"]["results"]["products"]
    except httpx.HTTPError as exc:
        print(f"[Shopify] Error querying {store['key']}: {exc}")
        return []
    except Exception as exc:
        print(f"[Shopify] Unexpected error from {store['key']}: {exc}")
        return []

    results: list[dict[str, Any]] = []

    for product in products:
        handle = product.get("handle")
        title = product.get("title")
        price_str = product.get("price")
        if not handle or not title or price_str in (None, ""):
            continue

        try:
            price = float(price_str)
        except (TypeError, ValueError):
            continue

        results.append(
            {
                "source": store["key"],
                "title": title,
                "price": price,
                "currency": "AUD",
                "ships_from": "Australia",
                "url": f"{base_url}/products/{handle}",
                "condition": None,
                "is_in_stock": product.get("available", True),
                "seller": None,
            }
        )

    return results


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5) -> list[dict]:
    _ = item_type

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers=_HEADERS,
    ) as client:
        all_results = await asyncio.gather(
            *[_search_store(client, store, query, max_results) for store in STORES]
        )

    return [listing for store_results in all_results for listing in store_results]
