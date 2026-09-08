from __future__ import annotations

import asyncio
import random
import re
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
    # Added 2026-09 after probing ~33 AU stores; all verified returning AUD product JSON with robots.txt allowing the path.
    {"key": "artistfirst", "name": "Artist First", "base_url": "https://artistfirst.com.au"},
    {"key": "rockinghorse", "name": "Rocking Horse Records", "base_url": "https://rockinghorse.net"},
    {"key": "greville", "name": "Greville Records", "base_url": "https://grevillerecords.com.au"},
    {"key": "repressed", "name": "Repressed Records", "base_url": "https://repressedrecords.com"},
    {"key": "musicfarmers", "name": "Music Farmers", "base_url": "https://musicfarmers.com"},
    {"key": "poisoncity", "name": "Poison City Records", "base_url": "https://poisoncityestore.com"},
    {"key": "roundandround", "name": "Round and Round Records", "base_url": "https://roundandroundrecords.com"},
    {"key": "roundreptile", "name": "Round Reptile Records", "base_url": "https://roundreptile.com"},
    {"key": "warnermusic", "name": "Warner Music Australia Store", "base_url": "https://store.warnermusic.com.au"},
    {"key": "title", "name": "Title", "base_url": "https://titlemusicfilmbooks.com"},
    {"key": "jetblackcat", "name": "Jet Black Cat Music", "base_url": "https://jetblackcatmusic.com"},
    # Not included: JB Hi-Fi (robots.txt disallows /search and /products.json only exposes the newest 250 products).
    {"key": "vinylrevival", "name": "Vinyl Revival", "base_url": "https://www.vinylrevival.com.au"},
]

STORE_NAMES: dict[str, str] = {s["key"]: s["name"] for s in STORES}

# NOTE on User-Agent: these storefronts are behind Cloudflare and were verified (live
# check, 2026-09) to return a 429 "Verifying your connection" managed-challenge page
# for *both* a self-identifying UA (adapter.USER_AGENT) and a browser-like UA equally --
# the block is TLS/behavioral fingerprinting, not the UA string, so switching UA buys
# nothing here. Keeping the existing browser-like UA since it's the tested prior
# behavior and there's no evidence a self-identifying UA does better or worse.
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Bound concurrent outbound requests across the STORES list, with jitter: many of these stores sit
# behind the same Cloudflare zone, and a synchronous burst from one IP trips a shared challenge for minutes.
_semaphore = asyncio.Semaphore(3)


async def _polite_delay() -> None:
    await asyncio.sleep(random.uniform(0.4, 1.6))

# This is a vinyl price tracker -- keep only listings that plausibly are vinyl records,
# and drop obvious non-vinyl merch that a keyword search can otherwise pull in.
_VINYL_RE = re.compile(r'\b(vinyl|LP|12"|12-inch|7"|7-inch|10"|record)\b', re.IGNORECASE)
_NON_VINYL_RE = re.compile(
    r'\b(CD|cassette|tape|digital|blu-ray|dvd|book|t-shirt|tee|hoodie|poster|slipmat)\b',
    re.IGNORECASE,
)


def _is_vinyl(product_type: Any, tags: Any, title: str) -> bool:
    if isinstance(tags, list):
        tags_str = " ".join(str(t) for t in tags)
    else:
        tags_str = str(tags or "")

    haystack = " ".join([str(product_type or ""), tags_str, title or ""])
    if not _VINYL_RE.search(haystack):
        return False
    if _NON_VINYL_RE.search(title or ""):
        return False
    return True


async def _search_store(
    client: httpx.AsyncClient,
    store: dict[str, str],
    query: str,
    max_results: int,
) -> list[dict[str, Any]] | None:
    base_url = store["base_url"]

    async with _semaphore:
        await _polite_delay()
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
            print(f"[Shopify] {store['key']}: request failed ({exc})")
            return None
        except Exception as exc:
            print(f"[Shopify] {store['key']}: unexpected error ({exc})")
            return None

    results: list[dict[str, Any]] = []

    for product in products:
        handle = product.get("handle")
        title = product.get("title")
        price_str = product.get("price")
        if not handle or not title or price_str in (None, ""):
            continue

        if not _is_vinyl(product.get("product_type"), product.get("tags"), title):
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

    print(f"[Shopify] {store['key']}: fetched {len(products)}, kept {len(results)} vinyl")
    return results


async def _search_store_products_json(
    client: httpx.AsyncClient,
    store: dict[str, str],
    query: str,
    max_results: int,
) -> list[dict[str, Any]] | None:
    base_url = store["base_url"]

    async with _semaphore:
        await _polite_delay()
        try:
            response = await client.get(
                f"{base_url}/products.json",
                params={"limit": 250},
            )
            response.raise_for_status()
            products = response.json().get("products", [])
        except httpx.HTTPError as exc:
            print(f"[Shopify] {store['key']}: request failed ({exc})")
            return None
        except Exception as exc:
            print(f"[Shopify] {store['key']}: unexpected error ({exc})")
            return None

    query_lower = query.lower()
    results: list[dict[str, Any]] = []

    for product in products:
        title = product.get("title")
        handle = product.get("handle")
        if not title or not handle:
            continue
        if query_lower not in title.lower():
            continue

        if not _is_vinyl(product.get("product_type"), product.get("tags"), title):
            continue

        variants = product.get("variants") or []
        if not variants:
            continue

        available_variant = next((v for v in variants if v.get("available")), None)
        variant = available_variant or variants[0]
        price_str = variant.get("price")
        if price_str in (None, ""):
            continue
        try:
            price = float(price_str)
        except (TypeError, ValueError):
            continue

        is_in_stock = available_variant is not None

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

    print(f"[Shopify] {store['key']}: fetched {len(products)}, kept {len(results)} vinyl")
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

        all_results = await asyncio.gather(
            *[_dispatch(store) for store in STORES], return_exceptions=True
        )

    listings: list[dict] = []
    for store, store_results in zip(STORES, all_results):
        if isinstance(store_results, Exception):
            print(f"[Shopify] {store['key']}: unhandled error ({store_results})")
            continue
        if store_results is None:
            continue  # request failed: the scanner must not treat this store's listings as gone
        listings.append({"_ok_source": store["key"]})
        listings.extend(store_results)

    return listings
