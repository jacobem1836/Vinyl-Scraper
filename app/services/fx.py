"""FX rate service — fetches and caches currency conversion rates.

Uses exchangerate-api.com free tier (no auth). Caches rates for 1 hour.
Per D-12: only GBP->AUD and USD->AUD conversions are needed.
Per D-15: all conversion happens in service layer, not templates.
"""

import httpx
from cachetools import TTLCache

_fx_cache: TTLCache = TTLCache(maxsize=4, ttl=3600)

_API_BASE = "https://open.er-api.com/v6/latest"


async def get_rate(from_currency: str, to_currency: str = "AUD") -> float | None:
    """Fetch exchange rate from from_currency to to_currency.

    Returns cached rate if available (TTL=1 hour).
    Returns None on any failure — caller must handle fallback.
    """
    if from_currency == to_currency:
        return 1.0

    key = f"{from_currency}-{to_currency}"
    if key in _fx_cache:
        return _fx_cache[key]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{_API_BASE}/{from_currency}")
            data = r.json()
            if data.get("result") != "success":
                print(f"[FX] API error for {from_currency}: {data.get('error-type', 'unknown')}")
                return None
            rate = data.get("rates", {}).get(to_currency)
            if rate:
                _fx_cache[key] = rate
            return rate
    except Exception as e:
        print(f"[FX] Rate fetch failed for {from_currency}->{to_currency}: {e}")
        return None


def convert_to_aud(amount: float, currency: str, rate: float | None) -> float | None:
    """Convert amount from currency to AUD using the given rate.

    Returns None if rate is None (FX fetch failed).
    AUD amounts pass through unchanged.
    """
    if currency == "AUD":
        return round(amount, 2)
    if rate is None:
        return None
    return round(amount * rate, 2)


def format_orig_display(price: float, shipping_cost: float, currency: str) -> str:
    """Format original-currency display string per D-11.

    Examples: "GBP 22.00 + GBP 8.00 shipping", "USD 15.00 + USD 5.00 shipping"
    AUD listings: "AUD 30.00 + AUD 5.00 shipping"
    """
    symbols = {"USD": "$", "GBP": "\u00a3", "AUD": "A$", "EUR": "\u20ac"}
    sym = symbols.get(currency, currency + " ")
    return f"{sym}{price:.2f} + {sym}{shipping_cost:.2f} shipping"
