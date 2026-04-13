from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)        # "album", "artist", or "label"
    query = Column(String, nullable=False)       # search term
    notes = Column(String, nullable=True)
    notify_below_pct = Column(Float, nullable=False, default=20.0)  # notify when listing is X% below median price
    notify_email = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_scanned_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    artwork_url = Column(String, nullable=True)  # Discogs thumb URL, populated on first scan
    discogs_release_id = Column(Integer, nullable=True)  # pinned Discogs release ID for precise scanning
    relevance_threshold = Column(Float, nullable=True)  # D-05: per-item override of settings.relevance_threshold_default
    last_notified_at = Column(DateTime, nullable=True)   # timestamp of last digest email sent for this item
    notify_drop_mode = Column(String, nullable=False, default="pct")  # "pct" or "usd" — price-drop trigger mode
    notify_drop_pct = Column(Float, nullable=True)       # per-item pct threshold override; null falls back to global default
    notify_drop_usd = Column(Float, nullable=True)       # per-item usd threshold override; null falls back to global default

    listings = relationship("Listing", back_populates="wishlist_item", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    wishlist_item_id = Column(Integer, ForeignKey("wishlist_items.id"), nullable=False)
    source = Column(String, nullable=False)         # 'discogs', 'thevinylstore', 'dutchvinyl', 'strangeworld', 'goldmine', 'utopia'
    title = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    condition = Column(String, nullable=True)
    seller = Column(String, nullable=True)
    ships_from = Column(String, nullable=True)  # country the seller ships from
    url = Column(String, nullable=False)
    found_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_in_stock = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)  # product image URL from source adapter
    relevance_score = Column(Float, nullable=True)  # D-03: rapidfuzz score 0-100 vs item "artist title"
    prev_price = Column(Float, nullable=True)           # price at previous scan; None on first scan
    prev_is_in_stock = Column(Boolean, nullable=True)   # stock status at previous scan; None on first scan

    wishlist_item = relationship("WishlistItem", back_populates="listings")

    __table_args__ = (
        UniqueConstraint("wishlist_item_id", "url", name="uq_listing_item_url"),
    )
