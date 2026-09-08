from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    invited_at = Column(DateTime, nullable=True)  # set when the owner invites this address


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)  # "album", "artist", "label", "subject"
    query = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    notify_below_pct = Column(Float, nullable=False, default=20.0)  # alert when landed price is X% below typical
    notify_email = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_scanned_at = Column(DateTime, nullable=True)
    last_notified_at = Column(DateTime, nullable=True)  # digest cooldown anchor
    is_active = Column(Boolean, default=True)
    artwork_url = Column(String, nullable=True)
    discogs_release_id = Column(Integer, nullable=True)  # pinned Discogs release for precise scanning

    user = relationship("User", back_populates="items")
    listings = relationship("Listing", back_populates="wishlist_item", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    wishlist_item_id = Column(Integer, ForeignKey("wishlist_items.id", ondelete="CASCADE"), nullable=False)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String, default="AUD")
    condition = Column(String, nullable=True)
    seller = Column(String, nullable=True)
    ships_from = Column(String, nullable=True)  # origin country, drives shipping estimate
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    found_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True)  # last scan in which the source returned this URL
    is_active = Column(Boolean, default=True)  # False once the source stops returning it
    is_in_stock = Column(Boolean, default=True)
    prev_price = Column(Float, nullable=True)  # price at the previous scan, for price-drop detection
    prev_is_in_stock = Column(Boolean, nullable=True)  # stock at the previous scan, for back-in-stock detection
    relevance_score = Column(Float, nullable=True)  # 0-100 title match against the wishlist query

    wishlist_item = relationship("WishlistItem", back_populates="listings")

    __table_args__ = (UniqueConstraint("wishlist_item_id", "url", name="uq_listing_item_url"),)
