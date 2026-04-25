import asyncio

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import Base, engine, get_db, run_migrations
from app.models import Listing, WishlistItem
from app.routers.wishlist import api_router, web_router
from app.services.cache import get_cached_dashboard, invalidate_dashboard_cache, set_cached_dashboard
from app.services.fx import convert_to_aud, format_orig_display, get_rate
from app.scheduler import scheduler, setup_scheduler
from app.services.shipping import get_shipping_cost

app = FastAPI(title="Vinyl Wishlist")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(web_router)
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    async def _init_db_with_retries():
        for attempt in range(1, 6):
            try:
                await asyncio.to_thread(run_migrations)
                await asyncio.to_thread(Base.metadata.create_all, bind=engine)
                print("[startup] DB init complete")
                return
            except Exception as e:
                print(f"[startup] DB init attempt {attempt}/5 failed: {e}")
                await asyncio.sleep(min(30, 2 ** attempt))

        print("[startup] DB init failed after retries; app will continue and retry on demand")

    if not settings.ebay_app_id or not settings.ebay_cert_id:
        print("[startup] WARNING: eBay credentials missing (EBAY_APP_ID and/or EBAY_CERT_ID); eBay adapter will return no results until configured")
    asyncio.create_task(_init_db_with_retries())
    setup_scheduler()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


# Web page routes (GET)

@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    from app.routers.wishlist import _enrich_item

    cached = get_cached_dashboard()
    if cached is not None:
        enriched = cached
    else:
        # Pre-resolve FX rates for this request
        fx_rates = {}
        for currency in ("USD", "GBP"):
            rate = await get_rate(currency)
            if rate:
                fx_rates[currency] = rate

        items = (
            db.query(WishlistItem)
            .filter_by(is_active=True)
            .options(selectinload(WishlistItem.listings))
            .order_by(WishlistItem.created_at.desc())
            .all()
        )
        enriched = [_enrich_item(item, fx_rates=fx_rates) for item in items]
        set_cached_dashboard(enriched)
    shipping_estimate = settings.shipping_estimate_usd
    priced = [i for i in enriched if i["best_price"] is not None]
    total_cost = round(sum(i["best_price"] for i in priced), 2) if priced else None
    cheapest = min(priced, key=lambda i: i["best_price"]) if priced else None
    most_expensive = max(priced, key=lambda i: i["best_price"]) if priced else None
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": enriched,
            "total_listings": sum(i["listing_count"] for i in enriched),
            "total_cost": total_cost,
            "cheapest": cheapest,
            "most_expensive": most_expensive,
            "shipping_estimate": shipping_estimate,
        },
    )


@app.get("/item/{item_id}")
async def item_detail(item_id: int, request: Request, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    from app.routers.wishlist import _enrich_item

    item = (
        db.query(WishlistItem)
        .filter_by(id=item_id, is_active=True)
        .options(selectinload(WishlistItem.listings))
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    raw_listings = (
        db.query(Listing)
        .filter_by(wishlist_item_id=item_id, is_active=True)
        .order_by(Listing.price.asc().nullslast())
        .all()
    )
    fallback = settings.shipping_estimate_usd

    # Pre-resolve FX rates for this request
    fx_rates = {}
    for currency in ("USD", "GBP"):
        rate = await get_rate(currency)
        if rate:
            fx_rates[currency] = rate

    listings = [
        {
            "id": l.id,
            "source": l.source,
            "title": l.title,
            "price": l.price,
            "currency": l.currency,
            "condition": l.condition,
            "seller": l.seller,
            "ships_from": l.ships_from,
            "url": l.url,
            "found_at": l.found_at,
            "is_active": l.is_active,
            "landed_price": (l.price + get_shipping_cost(l.ships_from, fallback)) if l.price is not None else None,
            "is_in_stock": l.is_in_stock,
            # FX conversion fields
            "aud_total": convert_to_aud(
                l.price + get_shipping_cost(l.ships_from, fallback),
                l.currency,
                fx_rates.get(l.currency) if l.currency != "AUD" else 1.0,
            ) if l.price is not None else None,
            "orig_display": format_orig_display(
                l.price, get_shipping_cost(l.ships_from, fallback), l.currency
            ) if l.price is not None else None,
        }
        for l in raw_listings
    ]
    return templates.TemplateResponse(
        "item_detail.html",
        {
            "request": request,
            "item": _enrich_item(item, fx_rates=fx_rates),
            "listings": listings,
        },
    )
