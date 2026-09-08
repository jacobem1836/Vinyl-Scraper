"""Wishlist pages and the JSON endpoints the dashboard's JavaScript calls. Everything is scoped to the signed-in user."""
import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session, selectinload

from app.auth import require_auth, require_auth_json, require_csrf, throttle
from app.config import settings
from app.database import SessionLocal, get_db
from app.models import Listing, User, WishlistItem
from app.services import scan_status, scanner
from app.services.http import USER_AGENT
from app.services.pricing import format_money, get_rates, listing_landed, shipping_aud, typical_price
from app.templating import templates

web_router = APIRouter(tags=["web"])
api_router = APIRouter(prefix="/api", tags=["api"])

ITEM_TYPES = {"album", "artist", "label", "subject"}


# --- helpers ---------------------------------------------------------------------

def _owned_item(db: Session, user: User, item_id: int, with_listings: bool = False) -> WishlistItem:
    q = db.query(WishlistItem).filter_by(id=item_id, user_id=user.id, is_active=True)
    if with_listings:
        q = q.options(selectinload(WishlistItem.listings))
    item = q.first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def enrich_item(item: WishlistItem, rates: dict) -> dict:
    live = [l for l in item.listings if l.is_active and l.is_in_stock and l.price is not None]
    ranked = sorted(live, key=lambda l: listing_landed(l, rates) or float("inf"))
    best = ranked[0] if ranked else None
    return {
        "id": item.id, "type": item.type, "query": item.query, "notes": item.notes,
        "notify_below_pct": item.notify_below_pct, "notify_email": item.notify_email,
        "created_at": item.created_at, "last_scanned_at": item.last_scanned_at,
        "artwork_url": item.artwork_url, "discogs_release_id": item.discogs_release_id,
        "best_price": listing_landed(best, rates) if best else None,
        "best_source": best.source if best else None,
        "best_ships_from": best.ships_from if best else None,
        "listing_count": len(live),
        "typical_price": typical_price(item.listings, rates),
        "top_listings": [
            {"title": l.title, "landed": listing_landed(l, rates), "price": l.price, "currency": l.currency,
             "price_display": format_money(l.price, l.currency), "ships_from": l.ships_from,
             "shipping": shipping_aud(l.ships_from), "source": l.source, "url": l.url}
            for l in ranked[:3]
        ],
    }


def _parse_form(type: str, query: str, notes: str | None, notify_below_pct: float, notify_email: str, discogs_release_id: str) -> dict:
    if type not in ITEM_TYPES:
        raise HTTPException(status_code=422, detail="Invalid item type")
    query = query.strip()
    if not 1 <= len(query) <= 200:
        raise HTTPException(status_code=422, detail="Query must be 1-200 characters")
    try:
        release_id = int(discogs_release_id) if discogs_release_id.strip() else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid Discogs release id")
    return {
        "type": type, "query": query, "notes": (notes or "").strip()[:500] or None,
        "notify_below_pct": min(max(float(notify_below_pct), 1.0), 90.0),
        "notify_email": notify_email.lower() in ("on", "true", "1", "yes"),
        "discogs_release_id": release_id,
    }


async def _scan_one_in_background(item_id: int) -> None:
    with SessionLocal() as db:
        item = db.get(WishlistItem, item_id, options=[selectinload(WishlistItem.listings)])
        if item is None:
            return
        try:
            await scanner.scan_item(db, item)
        except Exception as e:
            db.rollback()
            print(f"[Scanner] initial scan for item {item_id} failed: {e}")


# --- pages ------------------------------------------------------------------------

async def dashboard(request: Request, db: Session, user: User):
    rates = await get_rates()
    items = (
        db.query(WishlistItem)
        .filter_by(user_id=user.id, is_active=True)
        .options(selectinload(WishlistItem.listings))
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    enriched = [enrich_item(i, rates) for i in items]
    priced = [i for i in enriched if i["best_price"] is not None]
    return templates.TemplateResponse(request, "index.html", {
        "user": user,
        "items": enriched,
        "total_listings": sum(i["listing_count"] for i in enriched),
        "total_cost": round(sum(i["best_price"] for i in priced), 2) if priced else None,
        "cheapest": min(priced, key=lambda i: i["best_price"]) if priced else None,
        "scan_running": scan_status.is_running(user.id),
    })


@web_router.get("/item/{item_id}")
async def item_detail(item_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_auth)):
    item = _owned_item(db, user, item_id, with_listings=True)
    rates = await get_rates()
    rows = []
    for l in sorted(item.listings, key=lambda l: (not l.is_active, not l.is_in_stock, listing_landed(l, rates) or float("inf"))):
        rows.append({
            "id": l.id, "source": l.source, "title": l.title, "condition": l.condition, "seller": l.seller,
            "ships_from": l.ships_from, "url": l.url, "found_at": l.found_at, "last_seen_at": l.last_seen_at,
            "is_active": l.is_active, "is_in_stock": l.is_in_stock,
            "landed": listing_landed(l, rates), "price_display": format_money(l.price, l.currency) if l.price is not None else None,
            "shipping": shipping_aud(l.ships_from), "prev_price": l.prev_price,
            "prev_price_display": format_money(l.prev_price, l.currency) if l.prev_price is not None else None,
        })
    return templates.TemplateResponse(request, "item_detail.html", {
        "user": user, "item": enrich_item(item, rates), "listings": rows,
        "shipping_fallback": settings.shipping_estimate_aud,
    })


@web_router.post("/wishlist/add", dependencies=[Depends(require_csrf)])
async def add_item(
    type: str = Form(...), query: str = Form(...), notes: str | None = Form(None), notify_below_pct: float = Form(20.0),
    notify_email: str = Form(""), discogs_release_id: str = Form(""),
    db: Session = Depends(get_db), user: User = Depends(require_auth),
):
    item = WishlistItem(user_id=user.id, is_active=True, **_parse_form(type, query, notes, notify_below_pct, notify_email, discogs_release_id))
    db.add(item)
    db.commit()
    db.refresh(item)
    asyncio.create_task(_scan_one_in_background(item.id))
    return RedirectResponse(url="/", status_code=303)


@web_router.post("/wishlist/{item_id}/edit", dependencies=[Depends(require_csrf)])
async def edit_item(
    item_id: int, type: str = Form(...), query: str = Form(...), notes: str | None = Form(None), notify_below_pct: float = Form(20.0),
    notify_email: str = Form(""), discogs_release_id: str = Form(""),
    db: Session = Depends(get_db), user: User = Depends(require_auth),
):
    item = _owned_item(db, user, item_id)
    for k, v in _parse_form(type, query, notes, notify_below_pct, notify_email, discogs_release_id).items():
        setattr(item, k, v)
    db.commit()
    return RedirectResponse(url=f"/item/{item_id}?toast=Item+updated", status_code=303)


@web_router.post("/wishlist/{item_id}/delete", dependencies=[Depends(require_csrf)])
async def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(require_auth)):
    item = _owned_item(db, user, item_id)
    db.delete(item)
    db.commit()
    return RedirectResponse(url="/?toast=Removed+from+your+crate", status_code=303)


@web_router.get("/wishlist/{item_id}/status")
async def item_status(item_id: int, db: Session = Depends(get_db), user: User = Depends(require_auth_json)):
    item = _owned_item(db, user, item_id)
    count = db.query(Listing).filter_by(wishlist_item_id=item.id, is_active=True).count()
    return {"id": item.id, "has_listings": count > 0, "listing_count": count,
            "last_scanned_at": item.last_scanned_at.isoformat() if item.last_scanned_at else None,
            "artwork_url": item.artwork_url}


# --- JSON endpoints used by the dashboard JS --------------------------------------------

@api_router.post("/scan/start", dependencies=[Depends(require_csrf)])
async def start_scan(request: Request, item_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(require_auth_json)):
    throttle(request, "scan", limit=12, window_seconds=3600, extra_key=str(user.id))
    if scan_status.is_running(user.id):
        return {"started": False, "reason": "A scan is already running"}
    ids = [_owned_item(db, user, item_id).id] if item_id is not None else None
    asyncio.create_task(scanner.scan_user(user.id, ids, notify=True))
    return {"started": True}


@api_router.get("/scan/status")
async def get_scan_status(user: User = Depends(require_auth_json)):
    return scan_status.get(user.id)


@api_router.get("/discogs/search")
async def discogs_typeahead(request: Request, q: str = "", type: str = "album", user: User = Depends(require_auth_json)):
    if len(q.strip()) < 2:
        return []
    throttle(request, "typeahead", limit=60, window_seconds=60, extra_key=str(user.id))
    from app.services.discogs import typeahead_search
    return await typeahead_search(q.strip()[:100], item_type=type if type in ITEM_TYPES else "album", max_results=5)


def _is_public_host(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    return all(ipaddress.ip_address(info[4][0]).is_global for info in infos)


@api_router.get("/artwork")
async def proxy_artwork(url: str = "", user: User = Depends(require_auth_json)):
    """Image proxy so store/Discogs artwork loads with our User-Agent. Public https hosts only (no SSRF)."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.port not in (None, 443):
        raise HTTPException(status_code=400, detail="https image URL required")
    if not await asyncio.to_thread(_is_public_host, parsed.hostname):
        raise HTTPException(status_code=400, detail="host not allowed")
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            r = await client.get(url, headers={"User-Agent": USER_AGENT})
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="artwork fetch failed")
    ctype = r.headers.get("content-type", "")
    if r.status_code != 200 or not ctype.startswith("image/") or len(r.content) > 5_000_000:
        raise HTTPException(status_code=502, detail="upstream did not return an image")
    return Response(content=r.content, media_type=ctype, headers={"Cache-Control": "public, max-age=86400"})
