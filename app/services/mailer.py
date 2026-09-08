"""Outbound email via Resend. Unconfigured (no RESEND_API_KEY) logs the message instead of sending."""
import asyncio

import resend

from app.config import settings


def is_configured() -> bool:
    return bool(settings.resend_api_key and settings.resend_from)


def _send(to: str, subject: str, html: str) -> None:
    resend.api_key = settings.resend_api_key
    resend.Emails.send({"from": settings.resend_from, "to": [to], "subject": subject, "html": html})


async def send_email(to: str, subject: str, html: str) -> bool:
    if not is_configured():
        print(f"[Mailer] not configured; would send to {to}: {subject}")
        return False
    try:
        await asyncio.to_thread(_send, to, subject, html)
        return True
    except Exception as e:
        print(f"[Mailer] send to {to} failed: {e}")
        return False
