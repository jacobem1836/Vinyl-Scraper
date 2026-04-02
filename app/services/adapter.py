from collections.abc import Awaitable, Callable
from typing import TypedDict

from app.services import discogs, shopify


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


AdapterFn = Callable[[str, str], Awaitable[list[dict]]]

ADAPTER_REGISTRY: list[dict] = [
    {"name": "discogs", "fn": discogs.search_and_get_listings, "enabled": True},
    {"name": "shopify", "fn": shopify.search_and_get_listings, "enabled": True},
]


def get_enabled_adapters() -> list[dict]:
    return [a for a in ADAPTER_REGISTRY if a["enabled"]]
