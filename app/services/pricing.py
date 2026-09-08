"""Landed cost in AUD: price converted to AUD plus an estimated shipping cost by origin country.

Single source of truth for money maths. Everything the user sees or is alerted on goes through here.
"""
import time

import httpx

from app.config import settings

# Estimated shipping to Australia in AUD by origin. Rough, deliberately conservative; the UI says "estimated".
SHIPPING_AUD: dict[str, float] = {
    "Australia": 12.0,
    "New Zealand": 18.0,
    "United Kingdom": 28.0,
    "United States": 35.0,
    "Canada": 35.0,
    "Germany": 30.0,
    "France": 30.0,
    "Netherlands": 30.0,
    "Belgium": 30.0,
    "Italy": 30.0,
    "Spain": 30.0,
    "Sweden": 30.0,
    "Denmark": 30.0,
    "Norway": 33.0,
    "Switzerland": 33.0,
    "Austria": 30.0,
    "Poland": 30.0,
    "Czech Republic": 30.0,
    "Finland": 30.0,
    "Portugal": 30.0,
    "Japan": 26.0,
    "South Korea": 26.0,
    "Hong Kong": 24.0,
    "Singapore": 24.0,
}

# Used only if the FX API has never answered in this process. Refreshed hourly when it does.
FALLBACK_RATES_TO_AUD: dict[str, float] = {"AUD": 1.0, "USD": 1.50, "GBP": 1.95, "EUR": 1.65, "NZD": 0.92, "JPY": 0.0105, "CAD": 1.10}

_FX_URL = "https://open.er-api.com/v6/latest/AUD"
_FX_TTL = 3600
_rates: dict[str, float] = {}
_rates_fetched_at = 0.0


async def get_rates() -> dict[str, float]:
    """Return {currency: AUD per one unit}. Cached for an hour; last good value survives API failures."""
    global _rates, _rates_fetched_at
    if _rates and time.monotonic() - _rates_fetched_at < _FX_TTL:
        return _rates
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            data = (await client.get(_FX_URL)).json()
        per_aud = data.get("rates") or {}
        if data.get("result") == "success" and per_aud:
            _rates = {code: 1.0 / v for code, v in per_aud.items() if v}
            _rates["AUD"] = 1.0
            _rates_fetched_at = time.monotonic()
    except Exception as e:
        print(f"[FX] rate fetch failed: {e}")
    return _rates or dict(FALLBACK_RATES_TO_AUD)


def to_aud(amount: float, currency: str | None, rates: dict[str, float]) -> float | None:
    currency = (currency or "AUD").upper()
    if currency == "AUD":
        return round(amount, 2)
    rate = rates.get(currency) or FALLBACK_RATES_TO_AUD.get(currency)
    if rate is None:
        return None
    return round(amount * rate, 2)


def shipping_aud(ships_from: str | None) -> float:
    if not ships_from:
        return settings.shipping_estimate_aud
    return SHIPPING_AUD.get(ships_from, settings.shipping_estimate_aud)


def landed_aud(price: float | None, currency: str | None, ships_from: str | None, rates: dict[str, float]) -> float | None:
    if price is None:
        return None
    base = to_aud(price, currency, rates)
    if base is None:
        return None
    return round(base + shipping_aud(ships_from), 2)


def listing_landed(listing, rates: dict[str, float]) -> float | None:
    return landed_aud(listing.price, listing.currency, listing.ships_from, rates)


def median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else round((s[mid - 1] + s[mid]) / 2, 2)


def typical_price(listings, rates: dict[str, float]) -> float | None:
    """Median landed AUD across active, in-stock, priced listings."""
    vals = [v for l in listings if l.is_active and l.is_in_stock and (v := listing_landed(l, rates)) is not None]
    return median(vals)


def format_money(amount: float | None, currency: str = "AUD") -> str:
    if amount is None:
        return "—"
    symbols = {"AUD": "A$", "USD": "US$", "GBP": "£", "EUR": "€", "NZD": "NZ$", "JPY": "¥"}
    return f"{symbols.get(currency, currency + ' ')}{amount:,.2f}"
