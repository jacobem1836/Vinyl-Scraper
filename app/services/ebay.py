import asyncio
import base64
import re
import time

import httpx

from app.services.http import USER_AGENT

from app.config import settings

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
SCOPE = "https://api.ebay.com/oauth/api_scope"

_token: str | None = None
_token_expiry: float = 0.0
_token_lock = asyncio.Lock()
_semaphore = asyncio.Semaphore(5)  # Browse API allows high concurrency

# ISO 3166-1 alpha-2 -> English country name, matching app/services/shipping.py's
# SHIPPING_TABLE keys. Unmapped codes fall back to None (landed-cost layer applies
# its own fallback shipping estimate in that case).
_COUNTRY_NAMES: dict[str, str] = {
    "AU": "Australia",
    "NZ": "New Zealand",
    "GB": "United Kingdom",
    "US": "United States",
    "CA": "Canada",
    "DE": "Germany",
    "FR": "France",
    "NL": "Netherlands",
    "BE": "Belgium",
    "IT": "Italy",
    "ES": "Spain",
    "SE": "Sweden",
    "DK": "Denmark",
    "NO": "Norway",
    "CH": "Switzerland",
    "AT": "Austria",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "FI": "Finland",
    "PT": "Portugal",
    "JP": "Japan",
    "KR": "South Korea",
    "HK": "Hong Kong",
    "SG": "Singapore",
}

# Drop obvious non-vinyl matches by title (cassette/CD listings sometimes slip through
# the category filter, e.g. bundle listings).
_NON_VINYL_RE = re.compile(r"\b(cassette|cd)\b", re.IGNORECASE)


def _ships_from(item: dict) -> str | None:
    code = (item.get("itemLocation") or {}).get("country")
    if not code:
        return None
    return _COUNTRY_NAMES.get(code.upper())


async def _get_token() -> str:
    global _token, _token_expiry
    async with _token_lock:
        if _token and time.time() < _token_expiry - 60:
            return _token

        creds = base64.b64encode(
            f"{settings.ebay_app_id}:{settings.ebay_cert_id}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                TOKEN_URL,
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                },
                data={"grant_type": "client_credentials", "scope": SCOPE},
            )
            resp.raise_for_status()
            data = resp.json()
            _token = data["access_token"]
            _token_expiry = time.time() + data["expires_in"]
            return _token


async def search_and_get_listings(query: str, item_type: str) -> list[dict]:

    if not settings.ebay_app_id or not settings.ebay_cert_id:
        print("[eBay] Skipping — credentials not configured (set EBAY_APP_ID and EBAY_CERT_ID env vars)")
        return []

    async with _semaphore:
        try:
            token = await _get_token()

            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    SEARCH_URL,
                    params={
                        "q": query,
                        "category_ids": "176985",  # eBay: Music > Records/Vinyl
                        "filter": "buyingOptions:{FIXED_PRICE}",  # price tracker, not an auction tool
                        "limit": "10",
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": USER_AGENT,
                        "X-EBAY-C-MARKETPLACE-ID": "EBAY_AU",
                        "X-EBAY-C-ENDUSERCTX": "contextualLocation=country%3DAU",
                    },
                )
                resp.raise_for_status()

            items = resp.json().get("itemSummaries", [])
            listings = []
            for item in items:
                title = item.get("title", "")
                if _NON_VINYL_RE.search(title):
                    continue
                try:
                    listings.append({
                        "source": "ebay",
                        "title": title,
                        "url": item["itemWebUrl"],
                        "price": float(item["price"]["value"]),
                        "currency": item["price"].get("currency", "AUD"),
                        "condition": item.get("condition", ""),
                        "seller": item.get("seller", {}).get("username"),
                        "ships_from": _ships_from(item),
                        "is_in_stock": True,
                        "image_url": item.get("image", {}).get("imageUrl"),
                    })
                except (KeyError, ValueError):
                    continue

            return listings

        except Exception as e:
            print(f"[eBay] Error scanning '{query}': {e}")
            return []
