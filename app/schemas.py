from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class WishlistItemCreate(BaseModel):
    type: str           # "album", "artist", or "label"
    query: str
    notes: Optional[str] = None
    price_ceiling: Optional[float] = None
    notify_email: bool = True


class WishlistItemUpdate(BaseModel):
    type: Optional[str] = None
    query: Optional[str] = None
    notes: Optional[str] = None
    price_ceiling: Optional[float] = None
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
    url: str
    found_at: datetime
    is_active: bool


class WishlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    query: str
    notes: Optional[str]
    price_ceiling: Optional[float]
    notify_email: bool
    created_at: datetime
    last_scanned_at: Optional[datetime]
    is_active: bool
    best_price: Optional[float] = None      # computed field, not a DB column
    best_price_source: Optional[str] = None # "discogs" or "ebay"
    listing_count: int = 0
