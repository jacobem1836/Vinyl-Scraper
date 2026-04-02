import asyncio

import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

# Juno search returns 0 results via the /search/ endpoint because product listings are
# rendered client-side via JavaScript. The artist browse page (/artists/{query}/) returns
# full static HTML including prices. We use this as the effective search mechanism for
# artist-name queries. See SUMMARY.md for details.
BASE_URL = "https://www.juno.co.uk"
ARTIST_URL = "https://www.juno.co.uk/artists/{query}/"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    """Search Juno Records for vinyl listings by artist name."""
    _ = item_type  # Juno artist browse is keyword-based; media_type=vinyl filters format
    async with _semaphore:
        try:
            # Juno's /search/ endpoint loads results via JavaScript (client-side rendered).
            # The /artists/{query}/ page returns static HTML including prices.
            url = ARTIST_URL.format(query=query.replace(" ", "+"))
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(url, params={"media_type": "vinyl"})

            if resp.status_code == 403:
                print(f"[Juno] 403 Forbidden for '{query}' -- User-Agent may be blocked")
                return []

            if resp.status_code == 404:
                print(f"[Juno] No artist page for '{query}' (404)")
                return []

            resp.raise_for_status()
            await asyncio.sleep(2.0)

            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select(".dv-item")

            if not items:
                print(
                    f"[Juno] Parsed 0 results for '{query}' -- selectors may need updating"
                )
                return []

            listings = []
            for item in items:
                # Title: anchor linking to /products/ (not the artist/label links)
                title_el = next(
                    (
                        a
                        for a in item.select("a[href*='/products/']")
                        if a.get_text(strip=True)
                    ),
                    None,
                )
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                absolute_url = href if href.startswith("http") else BASE_URL + href

                # Price: .price_lrg inside .pl-big-price (e.g. "£18.13")
                price_el = item.select_one(".price_lrg")
                price: float | None = None
                if price_el:
                    price_text = price_el.get_text(strip=True).replace("£", "").replace(",", "").strip()
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass

                # Stock: .glyphicon-check present when in stock
                in_stock = item.select_one(".pl-big-price .glyphicon-check") is not None

                listings.append(
                    {
                        "source": "juno",
                        "title": title,
                        "url": absolute_url,
                        "price": price,
                        "currency": "GBP",
                        "condition": None,
                        "seller": None,
                        "ships_from": "United Kingdom",
                        "is_in_stock": in_stock,
                    }
                )

                if len(listings) >= 10:
                    break

            return listings

        except Exception as e:
            print(f"[Juno] Error scanning '{query}': {e}")
            return []
