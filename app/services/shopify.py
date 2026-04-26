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
    {
        "key": "wax_museum",
        "name": "Wax Museum Records",
        "base_url": "https://waxmuseumrecords.com.au",
    },
    {
        "key": "red_eye",
        "name": "Red Eye Records",
        "base_url": "https://www.redeye.com.au",
    },
    {
        "key": "rockaway",
        "name": "Rockaway Records",
        "base_url": "https://rockaway.com.au",
    },
    {
        "key": "happy_valley",
        "name": "Happy Valley Shop",
        "base_url": "https://happyvalleyshop.com",
    },
    {
        "key": "rare_records",
        "name": "Rare Records",
        "base_url": "https://www.rarerecords.com.au",
    },
    {
        "key": "heartland",
        "name": "Heartland Records",
        "base_url": "https://heartlandrecords.com.au",
        "search_type": "products_json",
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

        image_url = product.get("image")

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
                "image_url": image_url,
            }
        )

    return results


async def _search_store_products_json(
    client: httpx.AsyncClient,
    store: dict[str, str],
    query: str,
    max_results: int,
) -> list[dict[str, Any]]:
    base_url = store["base_url"]

    try:
        response = await client.get(
            f"{base_url}/products.json",
            params={"limit": 250},
        )
        response.raise_for_status()
        products = response.json().get("products", [])
    except httpx.HTTPError as exc:
        print(f"[Shopify] Error querying {store['key']}: {exc}")
        return []
    except Exception as exc:
        print(f"[Shopify] Unexpected error from {store['key']}: {exc}")
        return []

    query_lower = query.lower()
    results: list[dict[str, Any]] = []

    for product in products:
        title = product.get("title")
        handle = product.get("handle")
        if not title or not handle:
            continue
        if query_lower not in title.lower():
            continue

        variants = product.get("variants") or []
        if not variants:
            continue
        variant = variants[0]
        price_str = variant.get("price")
        if price_str in (None, ""):
            continue
        try:
            price = float(price_str)
        except (TypeError, ValueError):
            continue

        is_in_stock = variant.get("available", True)

        images = product.get("images") or []
        image_url = images[0].get("src") if images else None

        results.append(
            {
                "source": store["key"],
                "title": title,
                "price": price,
                "currency": "AUD",
                "ships_from": "Australia",
                "url": f"{base_url}/products/{handle}",
                "condition": None,
                "is_in_stock": is_in_stock,
                "seller": None,
                "image_url": image_url,
            }
        )

        if len(results) >= max_results:
            break

    return results


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5) -> list[dict]:
    _ = item_type

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers=_HEADERS,
    ) as client:
        async def _dispatch(store: dict[str, str]) -> list[dict[str, Any]]:
            if store.get("search_type") == "products_json":
                return await _search_store_products_json(client, store, query, max_results)
            return await _search_store(client, store, query, max_results)

        all_results = await asyncio.gather(*[_dispatch(store) for store in STORES])

    return [listing for store_results in all_results for listing in store_results]
