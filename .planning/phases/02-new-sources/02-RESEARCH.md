# Phase 2: New Sources - Research

**Researched:** 2026-04-02
**Domain:** Web scraping, REST API integration, async Python adapters
**Confidence:** HIGH (core patterns) / MEDIUM (HTML selectors for Juno/Discrepancy/Clarity/Bandcamp — selectors require live inspection at execution time)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**eBay AU Adapter (SRC-01)**
- D-01: Use the eBay Browse API (not HTML scraping). Filter to buy-it-now listings only. Target `EBAY_AU` marketplace. Return standard listing dicts with AUD prices.
- D-02: Adapter requires `EBAY_APP_ID` and `EBAY_CERT_ID` env vars. If unset, return `[]` immediately (config guard). Credentials not yet available.
- D-03: OAuth app token (client credentials flow) is cached at module level with TTL ~7000s. Fetch once, reuse across scans.

**AU Store Adapters — Discrepancy Records (SRC-02) and Clarity Records (SRC-03)**
- D-04: Both stores price in AUD. Set `ships_from: "Australia"` — shipping table already has `Australia: 8.0`.
- D-05: Both require HTML scraping. Discrepancy = Neto platform. Clarity = BigCommerce. Return standard listing dicts.

**Juno Records Adapter (SRC-04)**
- D-06: HTML scraping of Juno search results. Must set correct `User-Agent` header to avoid being blocked.
- D-07: Juno prices in GBP. Return `currency: "GBP"`, `ships_from: "United Kingdom"`. No FX conversion in Phase 2.

**Bandcamp Adapter (SRC-05)**
- D-08: Scrape `bandcamp.com/search?q={query}&item_type=p`. Filter results to vinyl-only.
- D-09: If no physical vinyl found, return `[]` silently. No digital results.
- D-10: Search-based scope only. Works for all item_type values.

**Currency Handling**
- D-11: Adapters return native currency in `currency` field. No FX conversion in Phase 2.
- D-12: Phase 3 will add AUD-equivalent display (out of scope here).
- D-13: `_landed()` continues to use raw price + shipping estimate in native currency.

**Per-Source Rate Limiting**
- Claude's Discretion: Module-level semaphores per adapter, not a registry schema extension.
  - eBay: `asyncio.Semaphore(5)` — Browse API allows high concurrency
  - Discogs (existing): leave at global `Semaphore(3)` inside scanner
  - HTML scrapers (Juno, Discrepancy, Clarity, Bandcamp): `asyncio.Semaphore(1)` + `asyncio.sleep(1–2s)`
  - Remove global `scan_semaphore` from `rate_limit.py` — each adapter self-limits
  - Scanner's `asyncio.gather()` across adapters remains unchanged

### Claude's Discretion
- Exact semaphore concurrency values per adapter (within ranges above)
- Sleep duration per HTML scraper (1–2s range)

### Deferred Ideas (OUT OF SCOPE)
- AUD display / FX conversion — Phase 3
- Per-item condition filtering (DATA-01) — v2
- Historical price tracking (DATA-02) — v2
- Egg Records (SRC-07) and international stores beyond Juno (SRC-08) — explicitly deferred
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SRC-01 | eBay AU adapter queries Browse API (not HTML), filters buy-it-now, targets `EBAY_AU`, returns standard listing dict | eBay Browse API confirmed: `filter=buyingOptions:{FIXED_PRICE}`, `X-EBAY-C-MARKETPLACE-ID: EBAY_AU`, scope `https://api.ebay.com/oauth/api_scope` |
| SRC-02 | Discrepancy Records adapter scrapes Neto storefront, returns AUD listing dicts | Neto confirmed. HTML scraping required. JSON endpoint not available from public search URL. BeautifulSoup + lxml pattern confirmed. |
| SRC-03 | Clarity Records adapter scrapes BigCommerce storefront, returns AUD listing dicts | BigCommerce confirmed. Search at `/search.php?q=`. BeautifulSoup + lxml pattern confirmed. |
| SRC-04 | Juno Records adapter scrapes HTML search (with correct User-Agent), returns listing dicts | Juno returns 403 without correct User-Agent. URL: `juno.co.uk/search/?q={query}&ob=dd&facet_id=47`. HTML selectors require live execution-phase inspection. |
| SRC-05 | Bandcamp adapter performs physical vinyl search, returns listing dicts | Bandcamp search confirmed at `bandcamp.com/search?q={query}&item_type=p`. `item_type=p` filters to physical merch. HTML structure inspected. |
</phase_requirements>

---

## Summary

Phase 2 adds five new source adapters. Three adapters (Discrepancy, Clarity, Juno, Bandcamp) require HTML scraping using the existing `httpx` + `beautifulsoup4` + `lxml` stack already available in the project. One adapter (eBay) uses a documented REST API with OAuth 2.0 client credentials flow.

All adapters follow the existing interface: `async def search_and_get_listings(query: str, item_type: str) -> list[dict]`. They are registered in `app/services/adapter.py:ADAPTER_REGISTRY`. The scanner in `app/services/scanner.py` already calls these via `asyncio.gather()` and isolates exceptions with `return_exceptions=True` — no scanner changes needed for new adapters.

The key operational risk in this phase is HTML selector stability for the scraped sources. Juno, Discrepancy, Clarity, and Bandcamp HTML structures must be confirmed at execution time using browser dev tools — this research captures known patterns but cannot guarantee current selector names. All scrapers should fail gracefully and return `[]` on any parse error, consistent with the existing Discogs error pattern.

**Primary recommendation:** Build all five adapters as independent modules in `app/services/`. Register each in `ADAPTER_REGISTRY`. Move global semaphore from `rate_limit.py` into per-adapter module-level semaphores. eBay adapter must be gated behind config guard and can be merged before credentials arrive.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28.0 | Async HTTP requests for all adapters | Already in project; used by all existing adapters |
| beautifulsoup4 | 4.12.3 | HTML parsing for scraped sources | Already installed in venv (`pip show beautifulsoup4`); standard for Python scraping |
| lxml | 5.3.0 | HTML parser backend for BeautifulSoup | Already installed; fastest parser, better malformed HTML handling than `html.parser` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asyncio (stdlib) | built-in | Semaphores, sleep between requests | Each HTML scraper module |
| base64 (stdlib) | built-in | Encode eBay API credentials | eBay adapter only |

**No new pip installs required.** All dependencies already present in `requirements.txt` or stdlib.

---

## Architecture Patterns

### Recommended Project Structure
```
app/services/
├── adapter.py          # Registry — add 5 new entries
├── discogs.py          # Reference implementation (existing)
├── shopify.py          # Reference implementation (existing)
├── ebay.py             # NEW: eBay Browse API adapter
├── discrepancy.py      # NEW: Discrepancy Records HTML scraper
├── clarity.py          # NEW: Clarity Records HTML scraper
├── juno.py             # NEW: Juno Records HTML scraper
├── bandcamp.py         # NEW: Bandcamp HTML scraper
├── scanner.py          # Unchanged (no scanner modifications needed)
├── rate_limit.py       # Remove global semaphore (replaced by per-adapter)
└── shipping.py         # Unchanged (Australia + United Kingdom already present)
app/config.py           # Add ebay_app_id, ebay_cert_id settings
```

### Pattern 1: HTML Scraper Adapter (Discrepancy, Clarity, Juno, Bandcamp)
**What:** Module-level semaphore + `asyncio.sleep()` to pace requests, httpx to fetch, BeautifulSoup to parse.
**When to use:** For any source without a public JSON API.
**Example:**
```python
# Source: existing shopify.py + discogs.py patterns
import asyncio
import httpx
from bs4 import BeautifulSoup

_semaphore = asyncio.Semaphore(1)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    async with _semaphore:
        try:
            async with httpx.AsyncClient(timeout=20.0, headers=_HEADERS, follow_redirects=True) as client:
                resp = await client.get(SEARCH_URL, params={"q": query})
                resp.raise_for_status()
            await asyncio.sleep(1.5)
            soup = BeautifulSoup(resp.text, "lxml")
            # ... parse listings ...
            return listings
        except Exception as e:
            print(f"[Source] Error scanning '{query}': {e}")
            return []
```

### Pattern 2: eBay Browse API Adapter (OAuth + Cached Token)
**What:** Client-credentials OAuth token fetched once and cached at module level. Token refreshed when within 60s of expiry.
**When to use:** For API sources with short-lived app tokens.
**Example:**
```python
# Source: eBay Developer Program docs
import asyncio
import base64
import time
import httpx

from app.config import settings

_token: str | None = None
_token_expiry: float = 0.0
_token_lock = asyncio.Lock()

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
SCOPE = "https://api.ebay.com/oauth/api_scope"
_semaphore = asyncio.Semaphore(5)

async def _get_token() -> str:
    global _token, _token_expiry
    async with _token_lock:
        if _token and time.time() < _token_expiry - 60:
            return _token
        creds = base64.b64encode(f"{settings.ebay_app_id}:{settings.ebay_cert_id}".encode()).decode()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                TOKEN_URL,
                headers={"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials", "scope": SCOPE},
            )
            resp.raise_for_status()
            data = resp.json()
        _token = data["access_token"]
        _token_expiry = time.time() + data["expires_in"]  # 7200s
        return _token

async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    if not settings.ebay_app_id or not settings.ebay_cert_id:
        return []
    async with _semaphore:
        try:
            token = await _get_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    SEARCH_URL,
                    params={"q": query, "filter": "buyingOptions:{FIXED_PRICE}", "limit": 10},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-EBAY-C-MARKETPLACE-ID": "EBAY_AU",
                        "X-EBAY-C-ENDUSERCTX": "contextualLocation=country%3DAU",
                    },
                )
                resp.raise_for_status()
            # ... parse resp.json()["itemSummaries"] ...
            return listings
        except Exception as e:
            print(f"[eBay] Error scanning '{query}': {e}")
            return []
```

### Pattern 3: Config Guard
**What:** Return `[]` immediately if required credentials are missing.
**When to use:** For any adapter that requires API keys.
**Example:**
```python
async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    if not settings.ebay_app_id or not settings.ebay_cert_id:
        return []
    # ... rest of implementation
```

### Pattern 4: Per-Adapter Module-Level Semaphore (Replaces rate_limit.py)
**What:** Each adapter owns its concurrency policy as a module-level `asyncio.Semaphore`.
**Why:** The global semaphore in `rate_limit.py` was designed for Discogs (3 concurrent). With 7 sources, it bottlenecks fast sources (eBay can handle 5) while still allowing slow HTML scrapers to run unconstrained relative to their own rate limits.
**Migration:** Remove `from app.services.rate_limit import scan_semaphore` usage from scanner. The scanner's own semaphore (currently hardcoded as `asyncio.Semaphore(3)` in `scan_all_items`) limits _items_ scanned concurrently and is separate from per-adapter limits — keep it.

### Anti-Patterns to Avoid
- **Sharing one httpx.AsyncClient across semaphored calls:** Creates connection pool contention between adapters. Each adapter should create its own `AsyncClient` per call (as discogs.py does) or maintain a module-level client that is properly limited.
- **Parsing HTML without fallback:** Always wrap selector access in `try/except` — Juno and BigCommerce have been known to change class names without notice.
- **Surfacing digital-only Bandcamp results:** The `item_type=p` URL param filters to physical merch, but HTML parsing should still check for vinyl indicators — Bandcamp physical merch includes t-shirts, cassettes, etc.
- **Assuming eBay token is always valid:** The `asyncio.Lock()` around token refresh is essential to prevent multiple simultaneous refresh calls when the token expires mid-scan.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML parsing | Custom regex string extraction | `BeautifulSoup(html, "lxml")` | Handles malformed HTML, attribute extraction, CSS selectors |
| OAuth token caching | Time-checked dict | Module-level `_token` + `_token_expiry` float (simple, works for single process) | No external library needed; process-scoped is sufficient for Railway single-instance |
| Rate limiting | Custom token bucket | `asyncio.Semaphore(N)` + `asyncio.sleep()` | Already used in discogs.py; adequate for 1-5 concurrent scrapers |

---

## Source-Specific Technical Notes

### eBay Browse API

**OAuth endpoint (production):** `https://api.ebay.com/identity/v1/oauth2/token`
- Method: POST
- `Authorization: Basic {base64(appId:certId)}`
- `Content-Type: application/x-www-form-urlencoded`
- Body: `grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope`
- Returns: `{"access_token": "...", "expires_in": 7200, "token_type": "Application Access Token"}`

**Search endpoint (production):** `https://api.ebay.com/buy/browse/v1/item_summary/search`
- Method: GET
- Required headers: `Authorization: Bearer {token}`, `X-EBAY-C-MARKETPLACE-ID: EBAY_AU`
- Key params: `q={query}`, `filter=buyingOptions:{FIXED_PRICE}`, `limit=10`
- Default behaviour: Returns only FIXED_PRICE (Buy It Now) listings — filter param may be redundant but explicit is safer.
- Response field: `itemSummaries[].price.value` (AUD on EBAY_AU), `itemSummaries[].title`, `itemSummaries[].itemWebUrl`
- Confidence: HIGH (official docs verified)

**Note:** eBay Developer Program approval is pending. Adapter should be fully implemented but gated behind config check. `enabled: True` in registry once credentials are available in Railway env.

### Discrepancy Records (Neto Platform)

**Search URL:** `https://www.discrepancy-records.com.au/search?q={query}`
- The search page renders HTML (not JSON from public URL). Neto's backend API requires API key — not available for public scraping.
- HTML contains embedded analytics data attributes (`data-name`, `data-price`, `data-url`) on product elements as confirmed by page inspection.
- Likely structure: product containers with class `.product-tile` or `.thumbnail` containing title, price, and link elements.
- **Confidence: LOW** — Actual CSS selectors must be confirmed via browser dev tools at execution time. The implementation note in CONTEXT.md references this as standard HTML scraping.
- `ships_from: "Australia"`, `currency: "AUD"`, `is_in_stock: True` (assume in-stock unless page shows otherwise)

### Clarity Records (BigCommerce Platform)

**Search URL:** `https://www.clarityrecords.com.au/search.php?q={query}`
- BigCommerce standard search page URL confirmed as `/search.php` (per BigCommerce developer docs).
- Site was ECONNREFUSED during research — may be intermittently down or geo-blocked. Structure should follow BigCommerce standard patterns.
- BigCommerce product cards typically use class `.productGrid` or `.product` with child `.card-title`, `.price--withTax`/`.price--withoutTax`.
- **Confidence: LOW** — Selectors require live inspection at execution time.
- `ships_from: "Australia"`, `currency: "AUD"`

### Juno Records

**Search URL:** `https://www.juno.co.uk/search/?q={query}&ob=dd&facet_id=47`
- `facet_id=47` restricts to vinyl format (confirmed via URL exploration).
- `ob=dd` = order by date descending.
- Juno returns HTTP 403 for requests without a browser-like User-Agent — MUST set User-Agent mimicking Chrome/Firefox.
- Historical Scrapy crawler (github.com/mattmurray/juno_crawler) confirms scraping is feasible.
- REQUIREMENTS.md out-of-scope note: "Juno selectors (if blocked) — Requires live browser inspection; defer to execution phase — may fall back to v2."
- Typical Juno product listing structure: each item in a container (historically `.juno-product` or product card wrapper), with title in an anchor element, price in a `.price` or `.juno-price` element.
- **Confidence: LOW** — Selectors must be confirmed at execution time via browser dev tools. Juno has changed their HTML multiple times.
- `currency: "GBP"`, `ships_from: "United Kingdom"`

### Bandcamp

**Search URL:** `https://bandcamp.com/search?q={query}&item_type=p`
- `item_type=p` restricts to physical merch items (confirmed via page inspection).
- HTML structure confirmed: results use `<div class="searchresult">` as container. Each result has a title link and metadata.
- Physical merch types on Bandcamp include vinyl, cassette, t-shirt, etc. The search results page shows result type (e.g., "album", "merch"). Need to filter for vinyl specifically.
- Vinyl identification: Check result subheader/type text for "vinyl" (case-insensitive) OR check that item type is not "digital" / "album" (digital).
- Price is not always present on the search results page — individual product pages may be needed for price, or it may appear in the result card.
- **Confidence: MEDIUM** — The search URL and container structure are confirmed. Vinyl-specific filtering logic must be validated at execution time.
- `currency: "USD"` (Bandcamp prices in USD), `ships_from: None` (varies by artist/label)

---

## Common Pitfalls

### Pitfall 1: Juno 403 Without Correct User-Agent
**What goes wrong:** Juno returns 403 Forbidden for all requests without a browser User-Agent.
**Why it happens:** Juno uses server-side bot detection on the search endpoint.
**How to avoid:** Always set `User-Agent` header to a realistic Chrome/Firefox string (as in shopify.py: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...`).
**Warning signs:** `httpx.HTTPStatusError` with status 403 on first request.

### Pitfall 2: asyncio.Semaphore Created at Module Level Before Event Loop
**What goes wrong:** `asyncio.Semaphore(N)` created at module import time can fail in Python 3.10+ if no event loop is running when the module is imported.
**Why it happens:** Semaphore internally checks `asyncio.get_event_loop()` in older patterns.
**How to avoid:** Create semaphore at module level — this is safe in Python 3.10+ when using asyncio properly. The existing `rate_limit.py` does exactly this (confirmed working). Mirror that pattern.
**Warning signs:** `DeprecationWarning: There is no current event loop` at import time.

### Pitfall 3: Bandcamp Returns Non-Vinyl Physical Merch
**What goes wrong:** `item_type=p` returns all physical merch (t-shirts, cassettes, posters) not only vinyl.
**Why it happens:** Bandcamp's search physical filter is not vinyl-specific.
**How to avoid:** After fetching results, filter to only items where the result type/description contains "vinyl" (case-insensitive). Silently skip non-vinyl physical items.
**Warning signs:** Listings appear for records searches that link to t-shirts or posters.

### Pitfall 4: eBay Token Race Condition
**What goes wrong:** Multiple concurrent scan calls all see an expired token and simultaneously try to refresh, making multiple token requests.
**Why it happens:** Without locking, the TTL check and token fetch are not atomic.
**How to avoid:** Use `asyncio.Lock()` around the token fetch block (pattern shown in Architecture Patterns section).
**Warning signs:** Intermittent eBay `401 Unauthorized` errors mid-scan.

### Pitfall 5: Scanner Semaphore Conflict with Adapter Semaphores
**What goes wrong:** Adding per-adapter semaphores while keeping the global `rate_limit.scan_semaphore` creates double-throttling.
**Why it happens:** The old global semaphore wraps the whole scan, while per-adapter semaphores wrap individual adapter calls.
**How to avoid:** Remove the `scan_semaphore` from `rate_limit.py` and any imports of it. The scanner's own `asyncio.Semaphore(3)` in `scan_all_items()` limits item-level concurrency (how many wishlist items scan simultaneously) and should be kept — it is separate from per-adapter limits.
**Warning signs:** Full scan takes much longer than expected; requests are effectively single-threaded.

### Pitfall 6: HTML Selectors Break After Store Redesign
**What goes wrong:** Scraper returns `[]` silently after a store updates their frontend.
**Why it happens:** BeautifulSoup `find()` returns `None` if selector doesn't match; without logging, failures are silent.
**How to avoid:** Log a warning when zero results are parsed from a non-empty page (i.e., response was 200 but no products found). Pattern: `print(f"[Discrepancy] Parsed 0 results for '{query}' — selectors may need updating")`

---

## Code Examples

### Adding an Adapter to the Registry
```python
# Source: app/services/adapter.py (existing pattern)
from app.services import discogs, shopify, ebay, discrepancy, clarity, juno, bandcamp

ADAPTER_REGISTRY: list[dict] = [
    {"name": "discogs",     "fn": discogs.search_and_get_listings,     "enabled": True},
    {"name": "shopify",     "fn": shopify.search_and_get_listings,     "enabled": True},
    {"name": "ebay",        "fn": ebay.search_and_get_listings,        "enabled": True},
    {"name": "discrepancy", "fn": discrepancy.search_and_get_listings, "enabled": True},
    {"name": "clarity",     "fn": clarity.search_and_get_listings,     "enabled": True},
    {"name": "juno",        "fn": juno.search_and_get_listings,        "enabled": True},
    {"name": "bandcamp",    "fn": bandcamp.search_and_get_listings,    "enabled": True},
]
```

### Adding eBay Credentials to config.py
```python
# Source: app/config.py (existing pattern; ebay_cert_id is the OAuth "client secret")
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing fields ...
    ebay_app_id: Optional[str] = None   # eBay App ID (client_id)
    ebay_cert_id: Optional[str] = None  # eBay Cert ID (client_secret)
```

### BeautifulSoup Parse Pattern (lxml)
```python
# Source: beautifulsoup4 docs; consistent with lxml already in venv
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "lxml")
products = soup.select(".product-card")  # selector confirmed at execution time
for product in products:
    title_el = product.select_one(".product-title a")
    price_el = product.select_one(".product-price")
    if not title_el or not price_el:
        continue
    title = title_el.get_text(strip=True)
    url = title_el.get("href", "")
    price_text = price_el.get_text(strip=True).replace("$", "").replace(",", "")
    try:
        price = float(price_text)
    except ValueError:
        continue
```

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All adapters | ✓ | 3.11+ (Railway) | — |
| httpx | All adapters | ✓ | 0.28.0 | — |
| beautifulsoup4 | HTML scrapers | ✓ | 4.12.3 | — |
| lxml | HTML scrapers | ✓ | 5.3.0 | Fall back to `html.parser` (slower but built-in) |
| eBay API credentials | SRC-01 | ✗ | — | Adapter returns `[]` via config guard — not blocking |

**Missing dependencies with no fallback:** None — all blocking dependencies are available.

**Missing dependencies with fallback:**
- eBay API credentials: Adapter gated behind config guard; returns `[]` until `EBAY_APP_ID` and `EBAY_CERT_ID` are set in Railway environment. Does not block the phase from merging.

---

## Open Questions

1. **Discrepancy Records exact HTML selectors**
   - What we know: Neto platform, search at `/search?q=`, product data embedded in page as analytics attributes.
   - What's unclear: Exact CSS class names for product container, title, price, stock status.
   - Recommendation: Inspect `https://www.discrepancy-records.com.au/search?q=radiohead` in browser dev tools at execution time. Target `data-name`, `data-price`, `data-url` attributes on analytics events as fallback if rendered markup is insufficient.

2. **Clarity Records site availability**
   - What we know: BigCommerce platform, search at `/search.php?q=`. Standard BigCommerce markup patterns are documented.
   - What's unclear: Site returned `ECONNREFUSED` during research — may be geo-blocked, intermittently down, or have changed domain.
   - Recommendation: Confirm site is accessible from Railway deployment region (Australia) before implementing. If consistently unavailable, mark `enabled: False` in registry.

3. **Juno HTML selector stability**
   - What we know: Juno search URL confirmed (`/search/?q=&ob=dd&facet_id=47`). 403 without User-Agent. Historical scraper (juno_crawler on GitHub) confirms feasibility.
   - What's unclear: Current CSS class names — Juno has redesigned their frontend. REQUIREMENTS.md explicitly notes "Juno selectors may need live browser inspection; may fall back to v2."
   - Recommendation: Treat Juno selector finding as an execution-time discovery task. Implement wrapper first, then fill in selectors from live inspection.

4. **Bandcamp vinyl-vs-other physical merch filtering**
   - What we know: `item_type=p` returns all physical merch. Search results page uses `<div class="searchresult">`. Result type label is present in HTML.
   - What's unclear: Exact CSS class/text for the "type" field that identifies vinyl vs. cassette vs. t-shirt.
   - Recommendation: During execution, check for text "vinyl" in the result card (case-insensitive). Also check if result has `item_type` class or attribute.

5. **rate_limit.py removal side-effects**
   - What we know: `scan_semaphore` is defined in `rate_limit.py`. `scanner.py` uses a local `asyncio.Semaphore(3)` in `scan_all_items()` — this does NOT import from `rate_limit.py` (confirmed by reading scanner.py).
   - What's unclear: Whether any other module imports from `rate_limit.py`.
   - Recommendation: Grep for `rate_limit` imports before removing. If only the old `scan_semaphore` is there and nothing imports it, the file can be deleted safely.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Global semaphore for all sources | Per-adapter semaphores | Phase 2 (this phase) | Each source can tune its own concurrency without affecting others |
| Blocking `requests` library | Async `httpx` | Phase 1 (already done) | Non-blocking I/O across all adapters |

---

## Sources

### Primary (HIGH confidence)
- eBay Developer Program — client credentials grant flow: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html
- eBay Browse API search endpoint: https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search
- eBay Browse API overview (marketplace ID header, FIXED_PRICE default): https://developer.ebay.com/api-docs/buy/browse/overview.html
- apitut.com eBay OAuth guide (confirmed token endpoint + request format): https://apitut.com/ebay/api/oauth-application-token.html
- BeautifulSoup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Existing project code: `app/services/discogs.py`, `app/services/shopify.py`, `app/services/adapter.py`, `app/services/scanner.py`

### Secondary (MEDIUM confidence)
- Bandcamp search URL `item_type=p` physical merch filter — verified via WebFetch page inspection
- BigCommerce search URL `/search.php` pattern — verified via BigCommerce developer docs and WebSearch
- Juno search URL and `facet_id=47` vinyl filter — inferred from URL exploration; site returned 403 during direct fetch
- Neto platform confirmed for Discrepancy Records — ZoomInfo and eScraper sources agree

### Tertiary (LOW confidence)
- Discrepancy Records HTML selectors (data attributes for analytics events) — inferred from partial page source, not confirmed by full DOM inspection
- Clarity Records HTML structure — site was unreachable during research; BigCommerce standard patterns assumed
- Juno HTML CSS classes for product title/price — site returned 403; historical patterns from juno_crawler repo not verified against current site

---

## Metadata

**Confidence breakdown:**
- eBay adapter (API integration): HIGH — official docs confirm endpoint, auth flow, filter params
- HTML scraper pattern (httpx + bs4 + lxml): HIGH — all libraries confirmed present, existing shopify.py is a working reference
- Discrepancy selectors: LOW — page partially fetched but DOM not fully rendered; execute-time inspection required
- Clarity selectors: LOW — site unreachable during research; BigCommerce patterns assumed
- Juno selectors: LOW — 403 blocked; historical patterns unverified against current site
- Bandcamp structure: MEDIUM — container class confirmed, vinyl filtering logic requires execution validation
- Per-adapter semaphore pattern: HIGH — mirrors existing working pattern in rate_limit.py and discogs.py

**Research date:** 2026-04-02
**Valid until:** 2026-05-02 (HTML scrapers degrade faster — re-verify Juno/Clarity/Discrepancy before execution if >2 weeks)
