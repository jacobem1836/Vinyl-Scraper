import asyncio
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Listing, WishlistItem
from app.services import discogs, shopify


async def scan_item(db: Session, item: WishlistItem) -> list[Listing]:
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

    return new_listings


async def scan_all_items(db: Session) -> dict:
    items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

    summary_items: list[dict] = []
    total_new_listings = 0

    for item in items:
        new_listings = await scan_item(db, item)
        count = len(new_listings)
        total_new_listings += count
        summary_items.append({"id": item.id, "query": item.query, "new_listings": count})

    return {
        "items_scanned": len(items),
        "new_listings_found": total_new_listings,
        "items": summary_items,
    }
