from collections.abc import Awaitable, Callable
from typing import TypedDict

from app.services import discogs, ebay, shopify
from app.services.http import USER_AGENT  # noqa: F401  (re-exported for callers)


class ListingDict(TypedDict, total=False):
    source: str          # required
    title: str           # required
    url: str             # required
    price: float | None
    currency: str
    condition: str | None
    seller: str | None
    ships_from: str | None
    is_in_stock: bool
    image_url: str | None


AdapterFn = Callable[[str, str], Awaitable[list[dict]]]

# Dropped 2026-09: clarity (domain gone), juno and discrepancy (Cloudflare JS challenge walls),
# bandcamp (robots.txt disallows /search and there is no public search API).
ADAPTER_REGISTRY: list[dict] = [
    {"name": "discogs", "fn": discogs.search_and_get_listings, "enabled": True},
    {"name": "shopify", "fn": shopify.search_and_get_listings, "enabled": True},
    {"name": "ebay", "fn": ebay.search_and_get_listings, "enabled": True},
]


def get_enabled_adapters() -> list[dict]:
    return [a for a in ADAPTER_REGISTRY if a["enabled"]]
