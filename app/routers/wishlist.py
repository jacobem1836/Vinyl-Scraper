import asyncio

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Header, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models import Listing, WishlistItem
from app.schemas import ListingResponse, WishlistItemCreate, WishlistItemResponse
from app.services import notifier, scanner
from app.services.cache import invalidate_dashboard_cache
from app.services.fx import convert_to_aud, format_orig_display, get_rate
from app.services.notifier import compute_typical_price
from app.services.shipping import get_shipping_cost

web_router = APIRouter(tags=["web"])
api_router = APIRouter(prefix="/api", tags=["api"])


async def _scan_in_background(item_id: int) -> None:
    db = SessionLocal()
    try:
        item = db.query(WishlistItem).filter_by(id=item_id).first()
        if item:
            new_listings = await scanner.scan_item(db, item)
            if item.notify_email and new_listings:
                await notifier.send_deal_email(item, new_listings)
    finally:
        invalidate_dashboard_cache()
        db.close()


async def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _landed(listing, fx_rates: dict | None = None) -> float:
    """Compute landed cost. If fx_rates provided, converts to AUD."""
    shipping = get_shipping_cost(listing.ships_from, settings.shipping_estimate_usd)
    base_total = listing.price + shipping
    if fx_rates and listing.currency != "AUD":
        rate = fx_rates.get(listing.currency)
        aud = convert_to_aud(base_total, listing.currency, rate)
        if aud is not None:
            return aud
    return base_total


def _enrich_item(item: WishlistItem, fx_rates: dict | None = None) -> dict:
    all_listings = list(item.listings or [])
    active_priced = [l for l in all_listings if l.is_active and l.price is not None]

    sorted_by_landed = sorted(active_priced, key=lambda l: _landed(l, fx_rates)) if active_priced else []
    best_listing = sorted_by_landed[0] if sorted_by_landed else None

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
        "artwork_url": item.artwork_url,
        "discogs_release_id": item.discogs_release_id,
        "best_price": _landed(best_listing, fx_rates) if best_listing else None,        # landed price (AUD if fx_rates)
        "best_price_raw": best_listing.price if best_listing else None,        # listing price only
        "best_ships_from": best_listing.ships_from if best_listing else None,
        "best_price_source": best_listing.source if best_listing else None,
        "listing_count": len(all_listings),
        "typical_price": compute_typical_price(active_priced),
        "top_listings": [
            {
                "title": l.title,
                "price": l.price,
                "landed_price": _landed(l, fx_rates),
                "ships_from": l.ships_from,
                "source": l.source,
                "url": l.url,
                "currency": l.currency,
            }
            for l in sorted_by_landed[:3]
        ],
    }


@web_router.post("/wishlist/add")
async def add_wishlist_item_web(
    background_tasks: BackgroundTasks,
    type: str = Form(...),
    query: str = Form(...),
    notes: str | None = Form(None),
    notify_below_pct: float = Form(20.0),
    notify_email: str = Form(""),
    discogs_release_id: str = Form(""),
    db: Session = Depends(get_db),
):
    release_id = int(discogs_release_id) if discogs_release_id else None
    notify_email_bool = notify_email.lower() in ("on", "true", "1", "yes")
    item = WishlistItem(
        type=type,
        query=query,
        notes=notes,
        notify_below_pct=notify_below_pct,
        notify_email=notify_email_bool,
        discogs_release_id=release_id,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    invalidate_dashboard_cache()
    background_tasks.add_task(_scan_in_background, item.id)

    return RedirectResponse(url="/", status_code=303)


@web_router.post("/wishlist/{item_id}/edit")
async def edit_wishlist_item_web(
    item_id: int,
    type: str = Form(...),
    query: str = Form(...),
    notes: str | None = Form(None),
    notify_below_pct: float = Form(20.0),
    notify_email: str = Form(""),
    discogs_release_id: str = Form(""),
    db: Session = Depends(get_db),
):
    release_id = int(discogs_release_id) if discogs_release_id else None
    notify_email_bool = notify_email.lower() in ("on", "true", "1", "yes")
    item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.type = type
    item.query = query
    item.notes = notes or None
    item.notify_below_pct = notify_below_pct
    item.notify_email = notify_email_bool
    item.discogs_release_id = release_id
    db.commit()
    invalidate_dashboard_cache()
    return RedirectResponse(url=f"/item/{item_id}?toast=Item+updated", status_code=303)


@web_router.post("/wishlist/{item_id}/delete")
async def delete_wishlist_item_web(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id).first()
    if item:
        db.delete(item)
        db.commit()
        invalidate_dashboard_cache()
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

    return RedirectResponse(url=f"/item/{item_id}?toast={len(new_listings)}+new+listings+found", status_code=303)


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

    return RedirectResponse(url=f"/?toast={summary['new_listings_found']}+new+listings+found", status_code=303)


@web_router.get("/wishlist/{item_id}/status")
async def item_scan_status(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    listing_count = db.query(Listing).filter_by(
        wishlist_item_id=item_id, is_active=True
    ).count()
    return {
        "id": item_id,
        "has_listings": listing_count > 0,
        "listing_count": listing_count,
        "last_scanned_at": item.last_scanned_at.isoformat() if item.last_scanned_at else None,
    }


@web_router.get("/api/discogs/search")
async def discogs_typeahead_search(q: str = "", type: str = "album"):
    if len(q.strip()) < 2:
        return []
    from app.services.discogs import typeahead_search
    results = await typeahead_search(q.strip(), item_type=type, max_results=5)
    return results


@web_router.get("/api/discogs/releases/search")
async def discogs_release_search(q: str = "", type: str = "album"):
    if len(q.strip()) < 2:
        return []
    from app.services.discogs import typeahead_search
    results = await typeahead_search(q.strip(), item_type=type, max_results=10)
    return results


@web_router.post("/wishlist/{item_id}/pin-release")
async def pin_release_web(
    item_id: int,
    release_id: str = Form(""),
    artwork_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if release_id:
        item.discogs_release_id = int(release_id)
        if artwork_url:
            item.artwork_url = artwork_url
        db.commit()
        invalidate_dashboard_cache()
        return RedirectResponse(url=f"/item/{item_id}?toast=Release+pinned", status_code=303)
    else:
        item.discogs_release_id = None
        db.commit()
        invalidate_dashboard_cache()
        return RedirectResponse(url=f"/item/{item_id}?toast=Pin+cleared", status_code=303)


@web_router.get("/api/artwork")
async def proxy_artwork(url: str = ""):
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, headers={"User-Agent": "VinylWishlist/1.0"})
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail="upstream error")
            return StreamingResponse(
                r.aiter_bytes(),
                media_type=r.headers.get("content-type", "image/jpeg"),
                headers={"Cache-Control": "public, max-age=86400"},
            )
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="artwork fetch failed")


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
async def create_wishlist_item_api(
    payload: WishlistItemCreate,
    background_tasks: BackgroundTasks,
    scan: bool = True,
    db: Session = Depends(get_db),
):
    item = WishlistItem(
        type=payload.type,
        query=payload.query,
        notes=payload.notes,
        notify_below_pct=payload.notify_below_pct,
        notify_email=payload.notify_email,
        discogs_release_id=payload.discogs_release_id,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    if scan:
        background_tasks.add_task(_scan_in_background, item.id)

    return _enrich_item(item)


@api_router.post("/wishlist/bulk", dependencies=[Depends(require_api_key)])
async def bulk_create_wishlist_items_api(payload: list[WishlistItemCreate], db: Session = Depends(get_db)):
    items = [
        WishlistItem(
            type=p.type,
            query=p.query,
            notes=p.notes,
            notify_below_pct=p.notify_below_pct,
            notify_email=p.notify_email,
            is_active=True,
        )
        for p in payload
    ]
    db.add_all(items)
    db.commit()
    return {"added": len(items)}


@api_router.delete("/wishlist/{item_id}", dependencies=[Depends(require_api_key)])
async def delete_wishlist_item_api(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    invalidate_dashboard_cache()
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


@api_router.post("/scan/start")
async def start_scan_api(item_id: int | None = None, db: Session = Depends(get_db)):
    from app.services import scan_status as _scan_status

    if _scan_status.get()["is_running"]:
        return {"started": False, "reason": "scan already in progress"}

    if item_id is not None:
        item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        async def _run_single():
            from app.database import SessionLocal
            _db = SessionLocal()
            try:
                _item = _db.query(WishlistItem).filter_by(id=item_id).first()
                if _item:
                    await scanner.scan_item(_db, _item, track=True)
            finally:
                _db.close()

        asyncio.create_task(_run_single())
    else:
        async def _run_all():
            from app.database import SessionLocal
            _db = SessionLocal()
            try:
                await scanner.scan_all_items(_db, track=True)
            finally:
                _db.close()

        asyncio.create_task(_run_all())

    return {"started": True}


@api_router.get("/scan/status")
async def scan_status_api():
    from app.services import scan_status as _scan_status
    return _scan_status.get()
