import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

scheduler = AsyncIOScheduler()


def setup_scheduler():
    from app.database import SessionLocal
    from app.models import WishlistItem
    from app.services import notifier, scanner
    from app.services.cache import invalidate_dashboard_cache
    from app.services.rate_limit import scan_semaphore

    async def scheduled_scan():
        db = SessionLocal()
        try:
            items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

            async def _scan_one(item):
                async with scan_semaphore:
                    new_listings = await scanner.scan_item(db, item)
                    if item.notify_email and new_listings:
                        notifiable = [l for l in new_listings if notifier.should_notify(item, l, list(item.listings or []))]
                        if notifiable:
                            await notifier.send_deal_email(item, notifiable)

            await asyncio.gather(*[_scan_one(item) for item in items], return_exceptions=True)
            invalidate_dashboard_cache()
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
