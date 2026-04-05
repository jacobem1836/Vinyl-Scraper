from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class WishlistItemCreate(BaseModel):
    type: str           # "album", "artist", or "label"
    query: str
    notes: Optional[str] = None
    notify_below_pct: float = 20.0
    notify_email: bool = True


class WishlistItemUpdate(BaseModel):
    type: Optional[str] = None
    query: Optional[str] = None
    notes: Optional[str] = None
    notify_below_pct: Optional[float] = None
    notify_email: Optional[bool] = None
    is_active: Optional[bool] = None


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wishlist_item_id: int
    source: str
    title: str
    price: Optional[float]
    currency: str
    condition: Optional[str]
    seller: Optional[str]
    ships_from: Optional[str] = None
    url: str
    found_at: datetime
    is_active: bool
    is_in_stock: bool = True


class WishlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    query: str
    notes: Optional[str]
    notify_below_pct: float
    notify_email: bool
    created_at: datetime
    last_scanned_at: Optional[datetime]
    is_active: bool
    artwork_url: Optional[str] = None       # Discogs thumb URL (nullable for items without art)
    best_price: Optional[float] = None      # computed field, not a DB column
    best_price_source: Optional[str] = None # "discogs" or "ebay"
    listing_count: int = 0
    typical_price: Optional[float] = None      # median of all active listing prices
    top_listings: list[dict] = []              # top 3 cheapest listings (title, price, source, url, currency)
