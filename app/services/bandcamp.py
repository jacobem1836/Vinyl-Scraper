import asyncio

import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

SEARCH_URL = "https://bandcamp.com/search"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    """Search Bandcamp for physical vinyl listings.

    Bandcamp's search does not expose a physical merch filter via URL params.
    We search albums (item_type=a) and filter results whose title or subhead
    contains 'vinyl' (case-insensitive), which catches albums sold as vinyl releases.
    """
    _ = item_type  # Bandcamp search is keyword-based
    async with _semaphore:
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(
                    SEARCH_URL,
                    params={"q": query, "item_type": "a"},
                )

            resp.raise_for_status()
            await asyncio.sleep(1.5)

            soup = BeautifulSoup(resp.text, "lxml")
            results = soup.select(".searchresult")

            if not results:
                return []

            listings = []
            non_vinyl_count = 0

            for result in results:
                itemtype_el = result.select_one(".itemtype")
                heading_el = result.select_one(".heading a")
                subhead_el = result.select_one(".subhead")
                price_el = result.select_one(".price")

                if not heading_el:
                    continue

                title = heading_el.get_text(strip=True)
                url = heading_el.get("href", "")
                # Strip Bandcamp tracking params from URL
                if "?" in url:
                    url = url.split("?")[0]

                itemtype = itemtype_el.get_text(strip=True) if itemtype_el else ""
                subhead = subhead_el.get_text(strip=True) if subhead_el else ""

                # Filter to vinyl-only: check title, itemtype, and subhead for "vinyl"
                combined_text = f"{title} {itemtype} {subhead}".lower()
                if "vinyl" not in combined_text:
                    non_vinyl_count += 1
                    continue

                # Parse price (may not be present on search results page)
                price: float | None = None
                if price_el:
                    price_text = (
                        price_el.get_text(strip=True)
                        .replace("$", "")
                        .replace(",", "")
                        .strip()
                    )
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass

                listings.append(
                    {
                        "source": "bandcamp",
                        "title": title,
                        "url": url,
                        "price": price,
                        "currency": "USD",
                        "condition": None,
                        "seller": None,
                        "ships_from": None,  # varies by artist/label
                        "is_in_stock": True,
                    }
                )

                if len(listings) >= 10:
                    break

            if non_vinyl_count > 0 and not listings:
                print(
                    f"[Bandcamp] No vinyl results for '{query}'"
                    f" (non-vinyl physical merch found but filtered)"
                )

            return listings

        except Exception as e:
            print(f"[Bandcamp] Error scanning '{query}': {e}")
            return []
