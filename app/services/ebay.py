import asyncio
import base64
import time

import httpx

from app.config import settings

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
SCOPE = "https://api.ebay.com/oauth/api_scope"

_token: str | None = None
_token_expiry: float = 0.0
_token_lock = asyncio.Lock()
_semaphore = asyncio.Semaphore(5)  # Browse API allows high concurrency


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
        return []

    async with _semaphore:
        try:
            token = await _get_token()

            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    SEARCH_URL,
                    params={
                        "q": query,
                        "filter": "buyingOptions:{FIXED_PRICE}",
                        "limit": "10",
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-EBAY-C-MARKETPLACE-ID": "EBAY_AU",
                        "X-EBAY-C-ENDUSERCTX": "contextualLocation=country%3DAU",
                    },
                )
                resp.raise_for_status()

            items = resp.json().get("itemSummaries", [])
            listings = []
            for item in items:
                try:
                    listings.append({
                        "source": "ebay",
                        "title": item["title"],
                        "url": item["itemWebUrl"],
                        "price": float(item["price"]["value"]),
                        "currency": "AUD",  # EBAY_AU marketplace prices in AUD
                        "condition": item.get("condition", ""),
                        "seller": item.get("seller", {}).get("username"),
                        "ships_from": "Australia",
                        "is_in_stock": True,
                    })
                except (KeyError, ValueError):
                    continue

            return listings

        except Exception as e:
            print(f"[eBay] Error scanning '{query}': {e}")
            return []
