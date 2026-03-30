import asyncio
import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.models import Listing, WishlistItem


def should_notify(item: WishlistItem, listing: Listing) -> bool:
    if item.price_ceiling is not None:
        return listing.price is not None and listing.price <= item.price_ceiling
    return True


def _send_smtp(
    subject: str,
    html_body: str,
    from_addr: str,
    to_addr: str,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(from_addr, to_addr, msg.as_string())


async def send_deal_email(item: WishlistItem, new_listings: list[Listing]) -> bool:
    if not settings.smtp_user or not settings.smtp_password or not settings.notify_email:
        return False

    if not new_listings:
        return False

    notify_listings = [listing for listing in new_listings if should_notify(item, listing)]
    if not notify_listings:
        return False

    subject = f"[Vinyl Wishlist] New deal for: {item.query}"

    table_rows: list[str] = []
    for listing in notify_listings:
        price_text = f"{listing.price} {listing.currency}" if listing.price is not None else "—"
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(listing.title)}</td>"
            f"<td>{html.escape(price_text)}</td>"
            f"<td>{html.escape(listing.condition or 'Unknown')}</td>"
            f"<td>{html.escape(listing.source.title())}</td>"
            f"<td><a href=\"{html.escape(listing.url, quote=True)}\">View listing</a></td>"
            "</tr>"
        )

    price_ceiling_html = ""
    if item.price_ceiling is not None:
        price_ceiling_html = f"<p>Your price ceiling: ${item.price_ceiling:.2f}</p>"

    html_body = (
        f"<h2>New listing found for: {html.escape(item.query)}</h2>"
        f"<p>Type: {html.escape(item.type)} | {len(notify_listings)} new listing(s) found</p>"
        f"{price_ceiling_html}"
        '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">'
        "<tr><th>Title</th><th>Price</th><th>Condition</th><th>Source</th><th>Link</th></tr>"
        f"{''.join(table_rows)}"
        "</table>"
    )

    try:
        await asyncio.to_thread(
            _send_smtp,
            subject,
            html_body,
            settings.smtp_user,
            settings.notify_email,
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_user,
            settings.smtp_password,
        )
        return True
    except Exception as e:
        print(f"[Notifier] Failed to send email: {e}")
        return False
