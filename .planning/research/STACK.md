# Stack Research

**Project:** Vinyl Wishlist Manager — scraping expansion + performance
**Researched:** 2026-04-02
**Scope:** New scraping sources, caching, async scan decoupling, rate limiting

---

## New Scraping Sources

### Juno Records (juno.co.uk)

**API availability:** None. No public developer API exists for Juno Records' vinyl catalogue.

**Scraping approach:** Direct HTML scraping with httpx + BeautifulSoup. The site's search URL pattern is `https://www.juno.co.uk/search/?q={query}&cat=vinyl` — standard query string, no JS required to render initial results. Community MP3tag scripts confirm the HTML varies between product pages and search results, so two parser functions will be needed.

**Anti-scraping:** No confirmed Cloudflare or heavy bot detection found in community discussion or tooling (the MP3tag scripts work via direct HTTP). A 403 was returned during research when fetching without appropriate headers — setting a realistic `User-Agent` and `Accept` header is required. Treat as medium friction, not high.

**Difficulty:** Medium. HTML parsing is straightforward but requires inspecting the live site to confirm current class names. The HTML structure reportedly differs between product pages and search results listings.

**Rate limit concern:** No documented limits. Apply a 1–2 second delay between requests as a courtesy; Juno is a small retailer and aggressive scraping would be inconsiderate.

**Library:** httpx (already in project) + BeautifulSoup4 (add as dependency). No need for Playwright or Selenium.

---

### Bandcamp (bandcamp.com)

**API availability:** None. Bandcamp shut down their public API and has no plans to reopen it (confirmed by Musicfetch.io and multiple community sources).

**Scraping approach:** httpx + BeautifulSoup. Bandcamp search URL: `https://bandcamp.com/search?q={query}&item_type=a` (item_type=a filters to albums). The search results page returns static HTML — no JS rendering required. Album/artist data is also embedded in a `TralbumData` JavaScript object on individual album pages, which is reliable structured data that can be extracted with a regex rather than fighting the DOM.

**Anti-scraping:** No Cloudflare observed. The search page serves standard HTML without bot challenges (confirmed by direct fetch during research). Bandcamp is rated "Very Easy" to scrape as of March 2026 by Scraperly.

**Rate limit concern:** Community reports 1–5 requests/minute before throttling. Apply a 2–3 second inter-request delay. Bandcamp is explicitly used by independent artists to sell physical records, so it's a valuable source — but its search is album-level, not listing-level. You won't get "this copy costs $X" the way Discogs provides; you get "this album is available on Bandcamp for $Y directly from artist." Appropriate for price discovery but different data shape from Discogs.

**Difficulty:** Low. Standard static HTML, no auth, well-understood scraping target. The main gotcha is that prices are not on the search results page — a second request per result is needed to get price from the album page.

**Library:** httpx + BeautifulSoup4.

---

### eBay AU (ebay.com.au)

**API availability:** Yes — the Browse API (RESTful). The legacy Finding API was decommissioned in February 2025 and is no longer available. The Browse API is the current replacement and supports keyword search, category filtering, and site-specific searches (AU marketplace).

**Authentication:** OAuth 2.0 Client Credentials flow. Requires registering a free developer account at developer.ebay.com. Tokens expire every 2 hours; your code needs to refresh automatically. eBay provides an official `ebay-oauth-python-client` SDK for this.

**Rate limits:** Approximately 5,000 calls/day on the free tier (community-reported; eBay's official call limits page confirms per-day quotas exist but the number can vary by API and application status). For a personal scraper scanning a wishlist every 6 hours, this is not a constraint.

**Scraping approach:** Use the Browse API's `/item_summary/search` endpoint with `q={query}`, `category_ids=` (vinyl records = category 306 on eBay), and `marketplace_id=EBAY_AU` to restrict to Australian listings. Returns JSON — no HTML parsing needed.

**Difficulty:** Low-Medium. The API is clean and well-documented. The friction is registration (a few minutes) and token management (write a small refresh helper). Worth it — eBay AU has a large secondhand vinyl market and returns structured data.

**Library:** httpx directly (the official Python SDK is for OAuth only; REST calls are just HTTP). Add `ebay-oauth-python-client` for token management.

**Key concern:** eBay AU listing prices include shipping from seller, not shipping to buyer. You'll need to flag these listings as "shipping unknown" or use a fixed AU-to-AU shipping estimate, rather than landed cost calculation.

---

### Australian Stores: Clarity Records (clarityrecords.net)

**Platform:** BigCommerce (confirmed via page source — assets served from `cdn11.bigcommerce.com`, Stencil framework).

**Scraping approach:** BigCommerce storefronts expose a standard search at `/search.php?search_query={query}`. The existing Shopify adapter is structurally similar — product cards in a predictable HTML grid. httpx + BeautifulSoup is sufficient.

**Difficulty:** Low. BigCommerce uses predictable class names (`productGrid`, `card-title`, `price--main` or similar). Inspect once to confirm, then write a targeted adapter. No anti-scraping observed.

**Note:** Clarity is Adelaide-based, not Melbourne. The store name may have caused confusion — worth including regardless as it's one of Australia's more established independent vinyl retailers with an online catalogue.

---

### Australian Stores: Discrepancy Records (discrepancy-records.com.au)

**Platform:** Neto — an Australian e-commerce platform. This is confirmed in their privacy policy ("We use Neto to power our online store").

**Search URL:** `https://www.discrepancy-records.com.au/?rf=kw&kw={query}`

**Scraping approach:** httpx + BeautifulSoup. Neto is less predictable than Shopify/BigCommerce in its HTML class naming, but the search results page follows a standard product grid layout. Requires inspection to identify current selectors.

**Difficulty:** Medium. Neto is less widely scraped than Shopify/BigCommerce, meaning fewer reference examples exist. Expect to spend more time on selector identification.

**Why include:** Discrepancy Records is Australia's largest online vinyl store (~800k titles) with Melbourne headquarters. High value target despite the custom platform.

---

### Australian Stores: Egg Records (eggrecords.com)

**Location correction:** Egg Records is in Newtown, Sydney — not Melbourne. Their primary store is at eggrecords.com; they also maintain a secondary storefront at eggrecords.bigcartel.com.

**Platform:** Common Ground (confirmed — footer states "Built with Common Ground", assets from `static.common-ground.io`). Common Ground is a niche independent music retail platform.

**Scraping approach:** Common Ground appears to have a standard product listing structure, but it is a less-common platform with minimal scraping community precedent. Requires live inspection.

**Difficulty:** Medium-High. Common Ground is not Shopify. No prior scrapers exist that I found. Treat as a stretch target.

**Recommendation:** Defer Egg Records to a later iteration. Focus Bandcamp + Discrepancy + eBay first. Egg Records' catalogue is smaller and the platform is harder to scrape reliably.

---

### Summary Table

| Source | Has API | Library | Difficulty | Priority |
|--------|---------|---------|------------|----------|
| Juno Records | No | httpx + BS4 | Medium | High |
| Bandcamp | No (shut down) | httpx + BS4 | Low | High |
| eBay AU | Yes (Browse API) | httpx + ebay-oauth-python-client | Low-Medium | High |
| Clarity Records | No (BigCommerce) | httpx + BS4 | Low | Medium |
| Discrepancy Records | No (Neto) | httpx + BS4 | Medium | High |
| Egg Records | No (Common Ground) | httpx + BS4 | Medium-High | Defer |

---

## Performance: Caching

### Problem

Every dashboard load calls `_enrich_item()` per wishlist item — this hits the database and may recompute listings on each request. No query result caching exists. With even 20–30 wishlist items, this compounds quickly.

### Recommended Approach: fastapi-cache2 with InMemoryBackend

For a single-process Railway deployment (one Uvicorn worker), `fastapi-cache2` with `InMemoryBackend` is the correct choice. It requires zero new infrastructure and integrates as a decorator.

```python
# requirements.txt addition
fastapi-cache2==0.2.2
```

The `@cache(expire=300)` decorator on dashboard and API endpoints caches the response in process memory for N seconds. The InMemoryBackend only evicts on access (lazy deletion), which is fine for a personal tool — the cache will be small.

**TTL recommendation:**
- Dashboard HTML: 5 minutes (300s) — stale data is acceptable; scans run every 6 hours
- Per-item listing data: 10 minutes (600s)
- Wishlist list endpoint: 30 seconds (short, changes on add/delete)

**Cache invalidation:** When an item is added or deleted, manually call `FastAPICache.clear()` or use key-based invalidation to flush stale dashboard cache.

**Caveats:**
- `fastapi-cache2` maintenance has slowed (no PyPI releases in ~12 months as of early 2026). The package still works for the use case here.
- An alternative is `functools.lru_cache` for pure functions, but it lacks TTL support natively and doesn't integrate with async FastAPI endpoints cleanly.
- If Railway ever scales to multiple workers/replicas, in-memory caching breaks (each worker has its own cache). Not a concern today, but worth noting.

**Alternative — manual dict cache:** For maximum simplicity and no dependency, a module-level `dict` with a timestamp check is viable:
```python
_cache: dict = {}  # {key: (value, expires_at)}
```
This is ~10 lines and works identically for a single-process app. Prefer fastapi-cache2 for the decorator ergonomics.

### Query Optimisation (prerequisite to caching)

Before adding caching, verify that the dashboard's DB queries use `JOIN` to fetch listings eagerly with items, rather than N+1 queries. If `_enrich_item()` issues one query per wishlist item, fixing that to a single query will likely produce more speedup than caching.

---

## Performance: Async Scan Decoupling

### Problem

When a wishlist item is added via `POST /api/wishlist`, a scan runs synchronously before the HTTP response is returned. This blocks the Shortcut/web form for 5–30 seconds depending on how many sources are scraped.

### Recommended Pattern: FastAPI BackgroundTasks

FastAPI's built-in `BackgroundTasks` is the correct solution here. It requires no new dependencies, runs in the same process (so it can access the same DB session and config), and executes after the HTTP response is already sent to the client.

```python
from fastapi import BackgroundTasks

@router.post("/api/wishlist")
async def add_item(item: ItemCreate, background_tasks: BackgroundTasks, ...):
    db_item = create_wishlist_item(db, item)
    background_tasks.add_task(scan_item, db_item.id)  # runs after response
    return {"id": db_item.id, "status": "queued"}
```

The iOS Shortcut receives the response immediately (HTTP 201 or 200 with the new item ID), and the scan runs in the background.

**Why not asyncio.Queue with a worker loop:** This pattern is commonly described but adds complexity — a persistent worker coroutine started at app startup, a queue object, and error handling. It's appropriate if you need task status tracking or task deduplication. For fire-and-forget scan-on-add, BackgroundTasks is simpler and sufficient.

**Why not Celery/ARQ/Redis:** The app already uses APScheduler for periodic scans. Adding a message broker for a single background task (scan-on-add) is overengineering for a personal single-user tool. The official FastAPI docs explicitly say BackgroundTasks is the right tool for "small tasks like sending an email notification after a response."

**Limitation to acknowledge:** If the Uvicorn worker process restarts while a background scan is in progress, the scan is lost. For a personal tool this is acceptable — the next APScheduler run (every 6 hours) will catch it. If this were a production system with SLAs, a persistent queue (ARQ + Redis) would be warranted.

**APScheduler coexistence:** BackgroundTasks and APScheduler coexist cleanly — they are independent. APScheduler handles periodic full-list scans; BackgroundTasks handles the per-add immediate scan.

---

## Rate Limiting Patterns for Scrapers

### Recommended: asyncio.Semaphore + per-domain delay

The project already uses `httpx.AsyncClient` for concurrent scraping. The right pattern is:

1. **Semaphore per source** to cap concurrency — e.g., `asyncio.Semaphore(3)` means at most 3 concurrent requests to a given source at once.
2. **`asyncio.sleep()` between requests** to respect per-source rate limits.
3. **Exponential backoff on 429/503** — if a source rate-limits you, wait 2^n seconds and retry up to 3 times.

```python
# Per-source semaphore pattern (already fits httpx adapter architecture)
_juno_sem = asyncio.Semaphore(2)

async def fetch_juno(query: str):
    async with _juno_sem:
        await asyncio.sleep(1.5)  # courtesy delay
        resp = await client.get(...)
```

**aiolimiter package** is worth adding if you need token-bucket rate limiting (e.g., "no more than 5 requests per 10 seconds"). It's a lightweight package that integrates cleanly with httpx async. Add if the simple semaphore + sleep approach proves insufficient.

**aiometer** is another option (mentioned in Scrapfly's 2025 guide) — it wraps `asyncio.gather` with rate limiting built in. Slightly more ergonomic than semaphores but adds a dependency. Prefer semaphores unless the per-source config becomes complex.

### Per-Source Guidance

| Source | Max concurrency | Inter-request delay | Notes |
|--------|----------------|---------------------|-------|
| Juno Records | 1 | 2s | Small retailer; be conservative |
| Bandcamp | 2 | 2–3s | 1–5 req/min documented threshold |
| eBay Browse API | 5 | 0.5s | API with documented quota; generous |
| Clarity Records | 1 | 2s | Small retailer |
| Discrepancy Records | 2 | 1s | Larger site, likely more resilient |
| Discogs | (existing) | (existing) | Already tuned |

---

## Confidence Levels

| Topic | Confidence | Rationale |
|-------|------------|-----------|
| Juno Records — no API, HTML scraping | MEDIUM | No official statement found; confirmed by absence of API docs and community tooling relying on HTML. 403 during live fetch suggests headers needed. |
| Bandcamp — no API, static HTML, easy | HIGH | Multiple sources confirm API is shut down. Scraperly March 2026 "Very Easy" rating. Direct fetch during research confirmed static HTML with no bot protection. |
| eBay Browse API replacing Finding API | HIGH | Official eBay developer announcement confirmed Finding API decommissioned February 2025. Browse API documentation is current. |
| eBay Browse API ~5000 calls/day free | MEDIUM | Community-reported figure; official page requires login to see exact limits. Sufficient for this use case regardless. |
| Clarity Records on BigCommerce | HIGH | Confirmed via live page source — CDN URLs and Stencil framework references are unambiguous. |
| Discrepancy Records on Neto | HIGH | Confirmed via live page source — privacy policy text and Neto-specific URL patterns are unambiguous. |
| Egg Records on Common Ground | HIGH | Confirmed via live page source — "Built with Common Ground" footer. |
| FastAPI BackgroundTasks for scan decoupling | HIGH | Official FastAPI docs confirm execution after response. Pattern is well-established in the community. |
| fastapi-cache2 InMemoryBackend for caching | MEDIUM | Library works but maintenance has slowed. Alternative (manual dict cache) is equally valid for this use case. |
| asyncio.Semaphore rate limiting pattern | HIGH | Well-established Python async pattern; fits existing httpx architecture directly. |

---

## Open Questions

- **Juno HTML selectors:** Requires live inspection of `juno.co.uk/search/` to confirm current CSS classes for product title, artist, price, and URL. The 403 during research means headers must be set before this can be scripted.
- **Bandcamp price shape:** Prices are not on the search results page — only on individual album pages. A second HTTP request per result is needed to retrieve price. This changes the data model slightly (Bandcamp listings are artist-direct sales, not marketplace listings). Decide upfront whether to include Bandcamp or treat it as a lower-priority "buy direct" source.
- **eBay OAuth token refresh:** The 2-hour token expiry means the app needs a token cache + refresh mechanism. This is a small but necessary implementation detail before eBay scraping works reliably.
- **Common Ground (Egg Records) API:** Worth a brief investigation — Common Ground is a platform and may expose a product API via `common-ground.io`. Not researched here due to low priority.

---

## Sources

- [eBay Browse API Overview](https://developer.ebay.com/api-docs/buy/browse/overview.html)
- [eBay Finding API Decommission Alert](https://community.ebay.com/t5/Traditional-APIs-Search/Alert-Finding-API-and-Shopping-API-to-be-decommissioned-in-2025/td-p/34222062)
- [FastAPI BackgroundTasks docs](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [fastapi-cache2 PyPI](https://pypi.org/project/fastapi-cache2/)
- [Scraperly — Bandcamp difficulty rating (March 2026)](https://scraperly.com/scrape/bandcamp-music)
- [Musicfetch — Bandcamp API status](https://musicfetch.io/services/bandcamp/api)
- [Scrapfly — Rate limiting async Python](https://scrapfly.io/blog/posts/how-to-rate-limit-asynchronous-python-requests)
- [Juno Records MP3tag community thread](https://community.mp3tag.de/t/juno-records/3960)
- [Medium — Why not Redis immediately for FastAPI caching](https://medium.com/@deepeshkalura/why-you-shouldnt-jump-straight-to-redis-for-caching-in-fastapi-c19f8541ad39)
- [eBay OAuth Python client](https://github.com/eBay/ebay-oauth-python-client)
