import asyncio
import re

import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

# Neto-based search — keyword param is 'kw', path is site root
SEARCH_URL = "https://www.discrepancy-records.com.au/"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

_PRICE_RE = re.compile(r"\$?([\d,]+\.?\d*)")


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    """Search Discrepancy Records (Neto platform) and return vinyl listing dicts."""
    _ = item_type  # store search is keyword-based, item_type not used

    try:
        async with _semaphore:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(SEARCH_URL, params={"kw": query})
                await asyncio.sleep(1.5)  # rate-limit: small AU store

        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        results: list[dict] = []

        # Products are rendered in .products-row > .thumbnail containers
        for thumbnail in soup.find_all(class_="thumbnail"):
            link = thumbnail.find("a")
            if not link:
                continue

            url = link.get("href", "")
            if not url:
                continue
            # Ensure absolute URL
            if url.startswith("/"):
                url = "https://www.discrepancy-records.com.au" + url

            # Title from the link's title attribute; strip "buy " prefix if present
            raw_title = link.get("title", "").strip()
            title = raw_title[4:].strip() if raw_title.lower().startswith("buy ") else raw_title
            if not title:
                # Fallback: text from .view-more inside the thumbnail
                view_more = thumbnail.find(class_="view-more")
                title = view_more.get_text(strip=True) if view_more else ""
            if not title:
                continue

            # Price: p.funky inside .pei-bottom (not always present)
            price: float | None = None
            funky = thumbnail.find("p", class_="funky")
            if funky:
                price_text = funky.get_text(strip=True)
                m = _PRICE_RE.search(price_text)
                if m:
                    try:
                        price = float(m.group(1).replace(",", ""))
                    except ValueError:
                        price = None

            img_tag = thumbnail.find("img")
            image_url = img_tag.get("src") if img_tag else None
            if image_url and image_url.startswith("/"):
                image_url = "https://www.discrepancy-records.com.au" + image_url

            results.append(
                {
                    "source": "discrepancy",
                    "title": title,
                    "url": url,
                    "price": price,
                    "currency": "AUD",
                    "condition": None,
                    "seller": None,
                    "ships_from": "Australia",
                    "is_in_stock": True,
                    "image_url": image_url,
                }
            )

            if len(results) >= 10:
                break

        if not results:
            print(
                f"[Discrepancy] Parsed 0 results for '{query}' -- selectors may need updating"
            )

        return results

    except Exception as e:
        print(f"[Discrepancy] Error scanning '{query}': {e}")
        return []
