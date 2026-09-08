"""Deal detection and digest emails.

Events per item after a scan:
  deal_alerts   new listings whose landed price is >= notify_below_pct below the item's typical price
  price_drops   existing listings whose price fell >= NOTIFY_DROP_PCT since the previous scan
  back_in_stock existing listings that went out-of-stock -> in-stock
One digest email per user per scan run; per-item cooldown suppresses repeats.
"""
from datetime import datetime, timedelta

from jinja2 import Environment, FileSystemLoader

from app.config import settings
from app.models import Listing, User, WishlistItem
from app.services import mailer
from app.services.pricing import format_money, listing_landed, typical_price

NOTIFY_DROP_PCT = 10.0

_env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


def is_deal(item: WishlistItem, listing: Listing, rates: dict) -> bool:
    landed = listing_landed(listing, rates)
    if landed is None or not listing.is_in_stock:
        return False
    others = [l for l in item.listings if l.id != listing.id]
    typical = typical_price(others, rates)
    if typical is None:
        return False  # nothing to compare against yet
    return landed <= typical * (1 - item.notify_below_pct / 100)


def price_dropped(listing: Listing) -> bool:
    if listing.prev_price is None or listing.price is None or not listing.is_in_stock:
        return False
    if listing.prev_price <= listing.price:
        return False
    return (listing.prev_price - listing.price) / listing.prev_price * 100 >= NOTIFY_DROP_PCT


def back_in_stock(listing: Listing) -> bool:
    return listing.prev_is_in_stock is False and listing.is_in_stock is True and listing.is_active


def within_cooldown(item: WishlistItem) -> bool:
    if item.last_notified_at is None:
        return False
    return datetime.utcnow() - item.last_notified_at < timedelta(hours=settings.notify_cooldown_hours)


def collect_events(item: WishlistItem, new_listings: list[Listing], rates: dict) -> dict | None:
    new_ids = {l.id for l in new_listings}
    deals = [l for l in new_listings if is_deal(item, l, rates)]
    drops = [l for l in item.listings if l.id not in new_ids and price_dropped(l)]
    restocked = [l for l in item.listings if l.id not in new_ids and back_in_stock(l)]
    if not (deals or drops or restocked):
        return None
    return {"deal_alerts": deals, "price_drops": drops, "back_in_stock": restocked}


def _row(l: Listing, rates: dict) -> dict:
    return {
        "title": l.title,
        "source": l.source.replace("_", " ").title(),
        "url": l.url,
        "ships_from": l.ships_from or "Unknown origin",
        "landed": format_money(listing_landed(l, rates)),
        "price": format_money(l.price, l.currency),
        "prev_price": format_money(l.prev_price, l.currency),
    }


def render_digest(user: User, digest: list[tuple[WishlistItem, dict]], rates: dict) -> tuple[str, str]:
    items = []
    total = 0
    for item, ev in digest:
        rows = {k: [_row(l, rates) for l in ev.get(k, [])] for k in ("deal_alerts", "price_drops", "back_in_stock")}
        total += sum(len(v) for v in rows.values())
        items.append({"query": item.query, "url": f"{settings.app_url}/item/{item.id}", **rows})
    subject = f"[CRATE] {total} update{'s' if total != 1 else ''} on your wishlist"
    html = _env.get_template("email/digest.html").render(items=items, total=total, app_url=settings.app_url)
    return subject, html


async def send_digest(user: User, digest: list[tuple[WishlistItem, dict]], rates: dict) -> bool:
    if not digest or not user.is_verified:
        return False
    subject, html = render_digest(user, digest, rates)
    return await mailer.send_email(user.email, subject, html)
