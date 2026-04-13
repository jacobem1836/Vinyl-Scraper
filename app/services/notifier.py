import asyncio
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from app.config import settings
from app.models import Listing, WishlistItem
from app.services.shipping import get_shipping_cost

_email_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
)


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


def _html_to_plaintext(html_body: str) -> str:
    """Strip HTML tags and collapse whitespace to produce a plain-text email fallback."""
    text = re.sub(r"<br\s*/?>", "\n", html_body)
    text = re.sub(r"</tr>", "\n", text)
    text = re.sub(r"</td>", " | ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#8209;", "-", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


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

    plain_body = _html_to_plaintext(html_body)
    msg.attach(MIMEText(plain_body, "plain"))
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

    # Compute best landed price
    landed_prices = [_landed(l) for l in notify_listings if l.price is not None]
    best_landed = min(landed_prices) if landed_prices else None

    # Compute percentage below typical
    typical = compute_typical_price(list(item.listings or []))
    has_typical = typical is not None and best_landed is not None
    if has_typical:
        pct_below = ((typical - best_landed) / typical) * 100
        pct_below_str = f"{pct_below:.0f}%"
    else:
        pct_below_str = ""

    # Build listing dicts for template
    template_listings = []
    for listing in notify_listings:
        if listing.price is not None:
            landed = _landed(listing)
            landed_str = f"${landed:.2f}"
        else:
            landed_str = "\u2014"
        template_listings.append({
            "title": listing.title,
            "landed_price": landed_str,
            "source": listing.source.title(),
            "ships_from": listing.ships_from or "Unknown",
        })

    # Render template
    template = _email_env.get_template("deal_alert.html")
    html_body = template.render(
        item_name=item.query,
        item_type=item.type,
        best_landed_price=f"${best_landed:.2f}" if best_landed is not None else "\u2014",
        pct_below_typical=pct_below_str,
        has_typical_price=has_typical,
        listings=template_listings,
        item_url=f"/item/{item.id}",
        notify_below_pct=f"{item.notify_below_pct:.0f}%",
    )

    subject = f"[CRATE] Deal alert: {item.query}"

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
