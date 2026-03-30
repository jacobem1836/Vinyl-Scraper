from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

scheduler = AsyncIOScheduler()


def setup_scheduler():
    from app.database import SessionLocal
    from app.models import WishlistItem
    from app.services import notifier, scanner

    async def scheduled_scan():
        db = SessionLocal()
        try:
            items = db.query(WishlistItem).filter_by(is_active=True).all()
            for item in items:
                new_listings = await scanner.scan_item(db, item)
                if item.notify_email and new_listings:
                    notifiable = [l for l in new_listings if notifier.should_notify(item, l)]
                    if notifiable:
                        await notifier.send_deal_email(item, notifiable)
        finally:
            db.close()

    scheduler.add_job(
        scheduled_scan,
        "interval",
        hours=settings.scan_interval_hours,
        id="scheduled_scan",
        replace_existing=True,
    )
