import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

scheduler = AsyncIOScheduler()


def setup_scheduler():
    from app.database import SessionLocal
    from app.models import WishlistItem
    from app.services import scanner
    from app.services.cache import invalidate_dashboard_cache
    from app.services.notifier import (
        _back_in_stock,
        _price_dropped,
        _within_cooldown,
        send_digest_email,
        should_notify,
    )

    def _collect_events(item, new_listings: list) -> dict | None:
        """Collect qualifying notification events for a single item after its scan.

        deal_alerts: new listings that pass should_notify() (preserves existing deal alert behaviour).
        price_drops: all item listings where _price_dropped() is True.
        back_in_stock: all item listings where _back_in_stock() is True.

        Returns None if no events qualify.
        """
        deal_alerts = [
            l for l in new_listings
            if should_notify(item, l, list(item.listings or []))
        ]
        all_listings = list(item.listings or [])
        price_drops = [
            (l, l.prev_price, l.price)
            for l in all_listings
            if _price_dropped(l, item)
        ]
        back_in_stock_listings = [
            l for l in all_listings
            if _back_in_stock(l)
        ]

        if not deal_alerts and not price_drops and not back_in_stock_listings:
            return None

        return {
            "deal_alerts": deal_alerts,
            "price_drops": price_drops,
            "back_in_stock": back_in_stock_listings,
        }

    async def scheduled_scan():
        db = SessionLocal()
        try:
            items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

            async def _scan_one(item):
                return await scanner.scan_item(db, item)

            results = await asyncio.gather(
                *[_scan_one(item) for item in items], return_exceptions=True
            )
            invalidate_dashboard_cache()

            digest_items = []
            for item, result in zip(items, results):
                if isinstance(result, Exception):
                    continue
                if not item.notify_email:
                    continue
                if _within_cooldown(item.last_notified_at):
                    continue
                events = _collect_events(item, result or [])
                if events:
                    digest_items.append((item, events))

            if digest_items:
                sent = await send_digest_email(digest_items)
                if sent:
                    now = datetime.utcnow()
                    for item, _ in digest_items:
                        item.last_notified_at = now
                    try:
                        db.commit()
                    except Exception as e:
                        print(f"[Scheduler] Failed to commit last_notified_at: {e}")
        finally:
            db.close()

    scheduler.add_job(
        scheduled_scan,
        "interval",
        hours=settings.scan_interval_hours,
        id="scheduled_scan",
        replace_existing=True,
        max_instances=1,
    )
