from fastapi import APIRouter, Depends, Form, Header, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Listing, WishlistItem
from app.schemas import ListingResponse, WishlistItemCreate, WishlistItemResponse
from app.services import notifier, scanner
from app.services.notifier import compute_typical_price

web_router = APIRouter(tags=["web"])
api_router = APIRouter(prefix="/api", tags=["api"])


async def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _enrich_item(item: WishlistItem) -> dict:
    all_listings = list(item.listings or [])
    active_priced = [l for l in all_listings if l.is_active and l.price is not None]

    best_listing = min(active_priced, key=lambda l: l.price) if active_priced else None

    return {
        "id": item.id,
        "type": item.type,
        "query": item.query,
        "notes": item.notes,
        "notify_below_pct": item.notify_below_pct,
        "notify_email": item.notify_email,
        "created_at": item.created_at,
        "last_scanned_at": item.last_scanned_at,
        "is_active": item.is_active,
        "best_price": best_listing.price if best_listing else None,
        "best_price_source": best_listing.source if best_listing else None,
        "listing_count": len(all_listings),
        "typical_price": compute_typical_price(active_priced),
        "top_listings": [
            {"title": l.title, "price": l.price, "source": l.source, "url": l.url, "currency": l.currency}
            for l in sorted(active_priced, key=lambda l: l.price)[:3]
        ],
    }


@web_router.post("/wishlist/add")
async def add_wishlist_item_web(
    type: str = Form(...),
    query: str = Form(...),
    notes: str | None = Form(None),
    notify_below_pct: float = Form(20.0),
    notify_email: bool = Form(True),
    db: Session = Depends(get_db),
):
    item = WishlistItem(
        type=type,
        query=query,
        notes=notes,
        notify_below_pct=notify_below_pct,
        notify_email=notify_email,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    new_listings = await scanner.scan_item(db, item)
    if item.notify_email and new_listings:
        await notifier.send_deal_email(item, new_listings)

    return RedirectResponse(url="/", status_code=303)


@web_router.post("/wishlist/{item_id}/delete")
async def delete_wishlist_item_web(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@web_router.post("/wishlist/{item_id}/scan")
async def scan_single_item_web(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_listings = await scanner.scan_item(db, item)

    if item.notify_email and new_listings:
        notifiable = [l for l in new_listings if notifier.should_notify(item, l, list(item.listings or []))]
        if notifiable:
            await notifier.send_deal_email(item, notifiable)

    return RedirectResponse(url=f"/item/{item_id}", status_code=303)


@web_router.post("/scan-all")
async def scan_all_items_web(db: Session = Depends(get_db)):
    summary = await scanner.scan_all_items(db)

    for item_summary in summary.get("items", []):
        new_count = item_summary.get("new_listings", 0)
        if not new_count:
            continue

        item = db.query(WishlistItem).filter_by(id=item_summary["id"], is_active=True).first()
        if not item or not item.notify_email:
            continue

        recent_new = (
            db.query(Listing)
            .filter_by(wishlist_item_id=item.id, is_active=True)
            .order_by(Listing.found_at.desc())
            .limit(new_count)
            .all()
        )

        notifiable = [l for l in recent_new if notifier.should_notify(item, l, list(item.listings or []))]
        if notifiable:
            await notifier.send_deal_email(item, notifiable)

    return RedirectResponse(url="/", status_code=303)


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


@api_router.get(
    "/wishlist",
    response_model=list[WishlistItemResponse],
    dependencies=[Depends(require_api_key)],
)
async def list_wishlist_items_api(db: Session = Depends(get_db)):
    items = (
        db.query(WishlistItem)
        .filter_by(is_active=True)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    return [_enrich_item(item) for item in items]


@api_router.post(
    "/wishlist",
    response_model=WishlistItemResponse,
    dependencies=[Depends(require_api_key)],
)
async def create_wishlist_item_api(payload: WishlistItemCreate, db: Session = Depends(get_db)):
    item = WishlistItem(
        type=payload.type,
        query=payload.query,
        notes=payload.notes,
        notify_below_pct=payload.notify_below_pct,
        notify_email=payload.notify_email,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    new_listings = await scanner.scan_item(db, item)

    if item.notify_email and new_listings:
        notifiable = [l for l in new_listings if notifier.should_notify(item, l, list(item.listings or []))]
        if notifiable:
            await notifier.send_deal_email(item, notifiable)

    db.refresh(item)
    return _enrich_item(item)


@api_router.delete("/wishlist/{item_id}", dependencies=[Depends(require_api_key)])
async def delete_wishlist_item_api(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"deleted": True}


@api_router.get(
    "/wishlist/{item_id}/listings",
    response_model=list[ListingResponse],
    dependencies=[Depends(require_api_key)],
)
async def list_item_listings_api(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    listings = (
        db.query(Listing)
        .filter_by(wishlist_item_id=item_id)
        .order_by(Listing.price.asc().nullslast())
        .all()
    )
    return listings


@api_router.post("/scan", dependencies=[Depends(require_api_key)])
async def scan_all_items_api(db: Session = Depends(get_db)):
    return await scanner.scan_all_items(db)
