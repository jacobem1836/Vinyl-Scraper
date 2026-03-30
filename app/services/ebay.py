from __future__ import annotations

import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup


def _parse_price(price_text: str) -> float | None:
    """Parse '$12.99' or '$10.00 to $15.00' -> float."""
    if not price_text:
        return None

    text = price_text.replace(",", "")
    matches = re.findall(r"(\d+(?:\.\d+)?)", text)
    if not matches:
        return None

    try:
        return float(matches[0])
    except (TypeError, ValueError):
        return None


def _normalize_ebay_url(href: str) -> str:
    """Extract item ID and return https://www.ebay.com/itm/{id}."""
    match = re.search(r"/itm/(?:[^/]+/)?(\d+)", href)
    if match:
        return f"https://www.ebay.com/itm/{match.group(1)}"
    return href


async def search_and_get_listings(query: str, item_type: str, max_results: int = 5) -> list[dict[str, Any]]:
    # item_type is currently not used for eBay query filtering.
    _ = item_type

    base_url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": f"{query} vinyl record",
        "_sacat": "176985",
        "LH_BIN": "1",
        "_sop": "15",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0, headers=headers) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            await asyncio.sleep(1)
    except httpx.HTTPError as exc:
        print(f"eBay request error: {exc}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select(".s-item")
    if not items:
        return []

    listings: list[dict[str, Any]] = []

    for item in items:
        title_el = item.select_one(".s-item__title")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        if title == "Shop on eBay":
            continue

        price_el = item.select_one(".s-item__price")
        price = _parse_price(price_el.get_text(" ", strip=True)) if price_el else None

        condition_el = item.select_one(".SECONDARY_INFO") or item.select_one(".s-item__subtitle")
        condition = condition_el.get_text(" ", strip=True) if condition_el else None

        seller_el = item.select_one(".s-item__seller-info-text") or item.select_one(".mbg-nw")
        seller = seller_el.get_text(" ", strip=True) if seller_el else None

        link_el = item.select_one(".s-item__link")
        href = link_el.get("href") if link_el else None
        if not href:
            continue

        listings.append(
            {
                "source": "ebay",
                "title": title,
                "price": price,
                "currency": "USD",
                "condition": condition,
                "seller": seller,
                "url": _normalize_ebay_url(href),
            }
        )

        if len(listings) >= max_results:
            break

    return listings
