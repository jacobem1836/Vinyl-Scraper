from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

scheduler = AsyncIOScheduler()


def setup_scheduler():
    from app.database import SessionLocal
    from app.models import Listing, WishlistItem
    from app.services import notifier, scanner

    async def scheduled_scan():
        db = SessionLocal()
        try:
            summary = await scanner.scan_all_items(db, track=False)
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
        finally:
            db.close()

    scheduler.add_job(
        scheduled_scan,
        "interval",
        hours=settings.scan_interval_hours,
        id="scheduled_scan",
        replace_existing=True,
    )
