from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.scanner import scan_everyone

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    scheduler.add_job(
        scan_everyone,
        "interval",
        hours=settings.scan_interval_hours,
        id="scheduled_scan",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
