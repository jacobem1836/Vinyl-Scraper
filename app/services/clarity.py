import asyncio

import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

BASE_URL = "https://clarityrecords.com.au"
SEARCH_URL = "https://clarityrecords.com.au/search.php"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    """Search Clarity Records (BigCommerce) for vinyl listings by query."""
    _ = item_type  # Clarity search is keyword-based via BigCommerce search_query param
    async with _semaphore:
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(SEARCH_URL, params={"search_query": query})

            if resp.status_code == 403:
                print(f"[Clarity] 403 Forbidden for '{query}' -- User-Agent may be blocked")
                return []

            if resp.status_code == 404:
                print(f"[Clarity] No results page for '{query}' (404)")
                return []

            resp.raise_for_status()
            await asyncio.sleep(2.0)

            soup = BeautifulSoup(resp.text, "lxml")

            # BigCommerce Stencil theme uses <li class="product"> or <article class="card">
            cards = soup.select("li.product") or soup.select("article.card")

            if not cards:
                print(
                    f"[Clarity] Parsed 0 results for '{query}' -- selectors may need updating"
                )
                return []

            listings = []
            for card in cards:
                # Title + URL: .card-title a or first product link
                title_el = card.select_one(".card-title a") or card.select_one("a[href*='/products/']") or card.select_one("a[href*='.html']")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                if href.startswith("//"):
                    absolute_url = "https:" + href
                elif href.startswith("/"):
                    absolute_url = BASE_URL + href
                elif href.startswith("http"):
                    absolute_url = href
                else:
                    absolute_url = BASE_URL + "/" + href

                # Price: BigCommerce Stencil price selectors
                price_el = (
                    card.select_one(".price--withoutTax")
                    or card.select_one(".price--main")
                    or card.select_one(".price")
                )
                price: float | None = None
                if price_el:
                    price_text = (
                        price_el.get_text(strip=True)
                        .replace("$", "")
                        .replace("AUD", "")
                        .replace(",", "")
                        .strip()
                    )
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass

                # Stock detection: check for sold-out class or text
                card_text = card.get_text(separator=" ").lower()
                is_in_stock = not (
                    card.select_one(".card-out-of-stock")
                    or card.select_one(".sold-out")
                    or "sold out" in card_text
                    or "out of stock" in card_text
                )

                # Image: first img in card, handle relative URLs
                img_el = card.select_one("img")
                image_url: str | None = None
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-src")
                    if image_url and image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url and image_url.startswith("/"):
                        image_url = BASE_URL + image_url

                listings.append(
                    {
                        "source": "clarity",
                        "title": title,
                        "url": absolute_url,
                        "price": price,
                        "currency": "AUD",
                        "condition": None,
                        "seller": None,
                        "ships_from": "Australia",
                        "is_in_stock": is_in_stock,
                        "image_url": image_url,
                    }
                )

                if len(listings) >= 10:
                    break

            return listings

        except Exception as e:
            print(f"[Clarity] Error scanning '{query}': {e}")
            return []
