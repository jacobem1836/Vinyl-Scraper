import asyncio
import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.models import Listing, WishlistItem
from app.services.shipping import get_shipping_cost


def _landed(listing: Listing) -> float:
    """Return listing price + estimated shipping to Australia."""
    return listing.price + get_shipping_cost(listing.ships_from, settings.shipping_estimate_usd)


def compute_typical_price(listings: list[Listing]) -> float | None:
    """Compute the median landed price (price + AU shipping) across active priced listings."""
    prices = sorted(_landed(l) for l in listings if l.price is not None and l.is_active)
    if not prices:
        return None
    mid = len(prices) // 2
    if len(prices) % 2 == 1:
        return prices[mid]
    return (prices[mid - 1] + prices[mid]) / 2


def should_notify(item: WishlistItem, listing: Listing, all_listings: list[Listing] | None = None) -> bool:
    """Return True if landed price is at least notify_below_pct% below the median landed price."""
    if listing.price is None:
        return False
    if not all_listings:
        return True  # no history yet — always notify
    typical = compute_typical_price(all_listings)
    if typical is None:
        return True  # can't compute median — notify
    threshold = typical * (1 - item.notify_below_pct / 100)
    return _landed(listing) <= threshold


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
        if listing.price is not None:
            landed = _landed(listing)
            price_text = f"${listing.price:.2f} + ${landed - listing.price:.0f} shipping = ${landed:.2f} AU"
        else:
            price_text = "—"
        ships_from_text = listing.ships_from or "Unknown"
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(listing.title)}</td>"
            f"<td>{html.escape(price_text)}</td>"
            f"<td>{html.escape(ships_from_text)}</td>"
            f"<td>{html.escape(listing.condition or 'Unknown')}</td>"
            f"<td>{html.escape(listing.source.title())}</td>"
            f"<td><a href=\"{html.escape(listing.url, quote=True)}\">View listing</a></td>"
            "</tr>"
        )

    notify_info_html = f"<p>Notifying on listings ≥ {item.notify_below_pct:.0f}% below typical price</p>"

    html_body = (
        f"<h2>New listing found for: {html.escape(item.query)}</h2>"
        f"<p>Type: {html.escape(item.type)} | {len(notify_listings)} new listing(s) found</p>"
        f"{notify_info_html}"
        '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">'
        "<tr><th>Title</th><th>Landed Price (AU)</th><th>Ships From</th><th>Condition</th><th>Source</th><th>Link</th></tr>"
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
