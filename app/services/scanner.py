import asyncio
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Listing, WishlistItem
from app.services import discogs, shopify
from app.services import scan_status
from app.services.cache import invalidate_dashboard_cache


async def scan_item(db: Session, item: WishlistItem, track: bool = False) -> list[Listing]:
    if track:
        scan_status.item_started(item.id, item.query, item.type)

    discogs_results, shopify_results = await asyncio.gather(
        discogs.search_and_get_listings(item.query, item.type),
        shopify.search_and_get_listings(item.query, item.type),
    )
    all_results = discogs_results + shopify_results

    new_listings: list[Listing] = []

    for result in all_results:
        url = result.get("url")
        if not url:
            continue

        existing = (
            db.query(Listing)
            .filter(Listing.wishlist_item_id == item.id, Listing.url == url)
            .first()
        )
        if existing:
            new_stock = result.get("is_in_stock")
            if new_stock is not None:
                existing.is_in_stock = new_stock
            continue

        listing = Listing(
            wishlist_item_id=item.id,
            source=result.get("source", ""),
            title=result.get("title", "Untitled"),
            price=result.get("price"),
            currency=result.get("currency", "USD"),
            condition=result.get("condition"),
            seller=result.get("seller"),
            ships_from=result.get("ships_from"),
            url=url,
            found_at=datetime.utcnow(),
            is_active=True,
            is_in_stock=result.get("is_in_stock", True),
        )
        db.add(listing)
        new_listings.append(listing)

    if new_listings:
        db.commit()
        for listing in new_listings:
            db.refresh(listing)

    item.last_scanned_at = datetime.utcnow()
    db.commit()
    db.refresh(item)

    invalidate_dashboard_cache()

    if track:
        scan_status.item_finished(item.id, item.query, len(new_listings))

    return new_listings


async def scan_all_items(db: Session, track: bool = False) -> dict:
    items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

    if track:
        scan_status.reset(mode="all", total=len(items))

    semaphore = asyncio.Semaphore(3)
    summary_items: list[dict] = []
    total_new_listings = 0

    async def _scan(item: WishlistItem) -> dict:
        async with semaphore:
            new_listings = await scan_item(db, item, track=track)
            count = len(new_listings)
            return {"id": item.id, "query": item.query, "new_listings": count}

    results = await asyncio.gather(*[_scan(item) for item in items])

    for r in results:
        summary_items.append(r)
        total_new_listings += r["new_listings"]

    if track:
        scan_status.finish()

    return {
        "items_scanned": len(items),
        "new_listings_found": total_new_listings,
        "items": summary_items,
    }
