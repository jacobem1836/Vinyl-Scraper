"""Scan wishlist items across all source adapters and persist listings.

One SQLAlchemy Session per item scan; never share a Session across concurrent coroutines.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import SessionLocal
from app.models import Listing, User, WishlistItem
from app.services import notifier, scan_status
from app.services.adapter import get_enabled_adapters
from app.services.pricing import get_rates
from app.services.relevance import is_digital, score_listing

ITEM_CONCURRENCY = 3


@dataclass
class ScanResult:
    new_listings: list[Listing] = field(default_factory=list)
    failed_sources: list[str] = field(default_factory=list)
    hidden_low_relevance: int = 0


async def _run_adapters(item: WishlistItem) -> tuple[list[dict], list[str], set[str]]:
    """Returns (results, failed_source_names, succeeded_source_names)."""
    adapters = get_enabled_adapters()
    coros = []
    for a in adapters:
        kwargs = {"discogs_release_id": item.discogs_release_id} if a["name"] == "discogs" and item.discogs_release_id else {}
        coros.append(a["fn"](item.query, item.type, **kwargs))
    outcomes = await asyncio.gather(*coros, return_exceptions=True)
    results, failed, ok = [], [], set()
    for a, r in zip(adapters, outcomes):
        if isinstance(r, Exception):
            print(f"[Scanner] {a['name']} failed for '{item.query}': {r}")
            failed.append(a["name"])
            continue
        ok.add(a["name"])
        for d in r:
            # Multi-store adapters mark each store that answered with {"_ok_source": key}; listings carry the store key as source.
            if "_ok_source" in d:
                ok.add(d["_ok_source"])
            else:
                results.append(d)
    return results, failed, ok


async def scan_item(db: Session, item: WishlistItem) -> ScanResult:
    """Fetch all sources for one item, upsert listings, deactivate ones no longer offered."""
    result = ScanResult()
    now = datetime.utcnow()
    raw, result.failed_sources, ok_sources = await _run_adapters(item)

    cover_image = next((r.get("_cover_image") for r in raw if r.get("_cover_image")), None)
    existing = {l.url: l for l in item.listings}
    seen_urls: set[str] = set()

    for r in raw:
        url = r.get("url")
        if not url or url in seen_urls:
            continue
        title = r.get("title") or "Untitled"
        if is_digital(title, r.get("format")):
            continue
        score = score_listing(item.query, title)
        if score < settings.relevance_threshold:
            result.hidden_low_relevance += 1
            continue
        seen_urls.add(url)
        listing = existing.get(url)
        if listing is None:
            listing = Listing(wishlist_item_id=item.id, url=url, found_at=now)
            db.add(listing)
            item.listings.append(listing)
            result.new_listings.append(listing)
        else:
            listing.prev_price = listing.price
            listing.prev_is_in_stock = listing.is_in_stock
        listing.source = r.get("source", listing.source or "")
        listing.title = title
        listing.price = r.get("price")
        listing.currency = (r.get("currency") or "AUD").upper()
        listing.condition = r.get("condition")
        listing.seller = r.get("seller")
        listing.ships_from = r.get("ships_from")
        listing.image_url = r.get("image_url")
        listing.is_in_stock = bool(r.get("is_in_stock", True))
        listing.is_active = True
        listing.relevance_score = score
        listing.last_seen_at = now

    # A source that answered but no longer lists a URL means that listing is gone. Failed sources are left alone.
    for l in item.listings:
        if l.url not in seen_urls and l.source in ok_sources and l.is_active:
            l.is_active = False
            l.prev_is_in_stock = l.is_in_stock
            l.is_in_stock = False

    # Artwork: Discogs cover art first (clean scans), then a store product image, then an eBay seller photo.
    store_image = next((l.image_url for l in result.new_listings if l.image_url and l.source != "ebay"), None)
    any_image = next((l.image_url for l in result.new_listings if l.image_url), None)
    item.artwork_url = cover_image or store_image or item.artwork_url or any_image
    item.last_scanned_at = now
    db.commit()
    return result


async def scan_user(user_id: int, item_ids: list[int] | None = None, notify: bool = True) -> dict:
    """Scan a user's active items (or a subset) with bounded concurrency, then send one digest email."""
    with SessionLocal() as db:
        q = db.query(WishlistItem).filter_by(user_id=user_id, is_active=True)
        if item_ids:
            q = q.filter(WishlistItem.id.in_(item_ids))
        ids = [i.id for i in q.all()]

    scan_status.start(user_id, len(ids))
    rates = await get_rates()
    sem = asyncio.Semaphore(ITEM_CONCURRENCY)
    digest: list[tuple[WishlistItem, dict]] = []
    summary = {"items_scanned": 0, "new_listings": 0, "failed_sources": 0}

    async def _one(item_id: int) -> None:
        async with sem:
            with SessionLocal() as db:
                item = db.get(WishlistItem, item_id, options=[selectinload(WishlistItem.listings)])
                if item is None:
                    return
                scan_status.item_started(user_id, item.id, item.query, item.type)
                try:
                    res = await scan_item(db, item)
                except Exception as e:
                    db.rollback()
                    print(f"[Scanner] item {item.id} '{item.query}' failed: {e}")
                    scan_status.item_finished(user_id, item.id, item.query, 0, item.type, failed_sources=len(get_enabled_adapters()))
                    return
                summary["items_scanned"] += 1
                summary["new_listings"] += len(res.new_listings)
                summary["failed_sources"] += len(res.failed_sources)
                scan_status.item_finished(user_id, item.id, item.query, len(res.new_listings), item.type, len(res.failed_sources))
                if notify and item.notify_email and not notifier.within_cooldown(item):
                    events = notifier.collect_events(item, res.new_listings, rates)
                    if events:
                        db.expunge(item)  # detach so the digest can read it after the session closes
                        digest.append((item, events))

    try:
        await asyncio.gather(*[_one(i) for i in ids])
        if digest:
            with SessionLocal() as db:
                user = db.get(User, user_id)
                if user and await notifier.send_digest(user, digest, rates):
                    sent_at = datetime.utcnow()
                    db.query(WishlistItem).filter(WishlistItem.id.in_([i.id for i, _ in digest])).update(
                        {WishlistItem.last_notified_at: sent_at}, synchronize_session=False
                    )
                    db.commit()
    finally:
        scan_status.finish(user_id)
    return summary


async def scan_everyone() -> None:
    """Scheduled entry point: every user with active items, one after another."""
    with SessionLocal() as db:
        user_ids = [row[0] for row in db.query(WishlistItem.user_id).filter_by(is_active=True).distinct().all()]
    for uid in user_ids:
        if scan_status.is_running(uid):
            continue
        try:
            s = await scan_user(uid, notify=True)
            print(f"[Scheduler] user {uid}: {s}")
        except Exception as e:
            print(f"[Scheduler] user {uid} scan failed: {e}")
