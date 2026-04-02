import asyncio
import re

import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

# BigCommerce-based store search endpoint
SEARCH_URL = "https://www.clarityrecords.com.au/search.php"
BASE_URL = "https://www.clarityrecords.com.au"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

_PRICE_RE = re.compile(r"\$?([\d,]+\.?\d*)")


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    """Search Clarity Records (BigCommerce platform) and return vinyl listing dicts.

    NOTE: Site was unreachable during implementation. Selectors follow BigCommerce
    standard patterns and may need adjustment once the site is confirmed reachable.
    """
    _ = item_type  # store search is keyword-based, item_type not used

    try:
        async with _semaphore:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(SEARCH_URL, params={"q": query})
                await asyncio.sleep(1.5)  # rate-limit: small AU store

        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        results: list[dict] = []

        # Standard BigCommerce product grid selectors
        # Products appear in .productGrid .product or .card elements
        product_grid = soup.find(class_="productGrid")
        if product_grid:
            product_items = product_grid.find_all(class_="product")
        else:
            # Fallback: look for card elements anywhere in main content
            product_items = soup.find_all("article", class_="card")

        for item in product_items:
            # Title: .card-title a or .product-title a
            title_tag = item.find(class_="card-title")
            if title_tag:
                title_link = title_tag.find("a") or title_tag
            else:
                title_link = item.find("a", class_="product-title") or item.find("a")

            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            if not title:
                continue

            # URL from anchor href
            href = title_link.get("href", "")
            if not href:
                href = (item.find("a") or {}).get("href", "")
            if not href:
                continue
            url = href if href.startswith("http") else BASE_URL + href

            # Price: .price--withTax preferred, fallback .price--withoutTax
            price: float | None = None
            price_tag = item.find(class_="price--withTax") or item.find(
                class_="price--withoutTax"
            )
            if price_tag:
                m = _PRICE_RE.search(price_tag.get_text(strip=True))
                if m:
                    try:
                        price = float(m.group(1).replace(",", ""))
                    except ValueError:
                        price = None

            results.append(
                {
                    "source": "clarity",
                    "title": title,
                    "url": url,
                    "price": price,
                    "currency": "AUD",
                    "condition": None,
                    "seller": None,
                    "ships_from": "Australia",
                    "is_in_stock": True,
                }
            )

            if len(results) >= 10:
                break

        if not results:
            print(
                f"[Clarity] Parsed 0 results for '{query}' -- selectors may need updating"
            )

        return results

    except Exception as e:
        print(f"[Clarity] Error scanning '{query}': {e}")
        return []
