from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db, run_migrations
from app.models import Listing, WishlistItem
from app.routers.wishlist import api_router, web_router
from app.scheduler import scheduler, setup_scheduler

app = FastAPI(title="Vinyl Wishlist")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(web_router)
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    run_migrations()
    Base.metadata.create_all(bind=engine)
    setup_scheduler()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


# Web page routes (GET)

@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    from app.routers.wishlist import _enrich_item

    items = (
        db.query(WishlistItem)
        .filter_by(is_active=True)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    enriched = [_enrich_item(item) for item in items]
    shipping = settings.shipping_estimate_usd
    priced = [i for i in enriched if i["best_price"] is not None]
    total_cost = round(sum(i["best_price"] + shipping for i in priced), 2) if priced else None
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
            "shipping_estimate": shipping,
        },
    )


@app.get("/item/{item_id}")
async def item_detail(item_id: int, request: Request, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    from app.routers.wishlist import _enrich_item

    item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    listings = (
        db.query(Listing)
        .filter_by(wishlist_item_id=item_id, is_active=True)
        .order_by(Listing.price.asc().nullslast())
        .all()
    )
    return templates.TemplateResponse(
        "item_detail.html",
        {
            "request": request,
            "item": _enrich_item(item),
            "listings": listings,
        },
    )
