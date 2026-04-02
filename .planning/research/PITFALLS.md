# Pitfalls Research

**Project:** Vinyl Wishlist Manager
**Researched:** 2026-04-02
**Scope:** Milestone additions — new scraping sources, performance improvements, UI redesign

---

## Scraping Risks by Source

### Juno Records

**What breaks:**
Juno Records (junorecords.com) is a large specialist electronic/dance retailer. No confirmed public API exists. HTML scraping is the only viable path.

Key risks:
- The site is JavaScript-heavy in places (cart, filters). Product listing pages for search results typically render server-side but category/filter state can rely on JS-driven URL params.
- CSS class names on Juno are not semantic — they change without notice as the site updates. Scraping by class name will break; prefer scraping by structural position or data attributes where present.
- No confirmed rate limiting behavior is documented publicly, but the standard pattern applies: more than ~30 requests/minute from a single IP risks a soft block.
- Juno uses a custom CDN. Response time varies — timeout at 20s (current default in the codebase) may be insufficient on slow days.

**Mitigation:**
- Scrape by URL structure, not class names. Juno search URLs follow a predictable pattern (`/search/?q=artist+title`).
- Add explicit `User-Agent` header mimicking a browser. Scraping with Python's default httpx agent will be identified quickly.
- Keep per-domain concurrency to 1-2 requests max. Add 1-2s jitter between requests.
- Parse price from text content, not structured data — Juno does not expose JSON-LD or schema.org markup on listing pages.
- Confidence: LOW (no official documentation; based on community scrapers and general pattern analysis).

---

### eBay AU

**What breaks:**
eBay is the highest-risk source to scrape. It uses Akamai Bot Manager, which performs TLS fingerprinting, browser fingerprinting, and behavioral analysis. A plain `httpx` GET will be detected and return a challenge page or 403 within a few requests.

**The right approach is the eBay Browse API, not HTML scraping.** The Browse API:
- Is free with a developer account
- Allows 5,000 calls/day by default (sufficient for personal use)
- Returns structured JSON with price, condition, shipping, listing type, and location
- Supports `filter=itemLocationCountry:AU` and `filter=buyingOptions:{FIXED_PRICE}` to isolate AU buy-it-now listings
- Does not require OAuth for read-only search (Client Credentials flow only)

Key risks even with the API:
- **Auction vs Buy-It-Now:** The Browse API returns both by default. Auctions have `currentBidPrice` not `price`, and their ended-auction prices are not accessible. Filter with `buyingOptions:{FIXED_PRICE}` to exclude auctions, or handle both price fields.
- **Shipping cost to AU:** eBay does not return a computed landed cost. The `shippingOptions` array may be empty for international listings that require contacting the seller. Do not assume a shipping cost is always present — fall back to the existing `shipping.py` table.
- **AU vs international listings:** `itemLocationCountry` in the response tells you where the item is, but AU sellers may list on eBay.com (US) rather than eBay.com.au. Searching `ebay.com.au` via the marketplace header returns AU-biased results but not exclusively AU stock.
- **Title-only matching:** eBay search is keyword-based. There is no structured "artist" or "label" field. Searching `"Artist Name" "Album Title" vinyl` returns noisy results — you will need a post-filter to reject false positives (e.g., listings mentioning the artist in context of a different item).
- **API key expiry:** eBay OAuth Client Credentials tokens expire after 2 hours. The integration must refresh them automatically or requests will silently return 401.

**HTML scraping as fallback:** Do not attempt. Akamai protection makes it unreliable without residential proxies, which are out of scope for a personal tool.

- Confidence: MEDIUM (API structure confirmed via eBay developer docs; rate limits confirmed).

---

### Bandcamp

**What breaks:**
Bandcamp has no public API for catalog search. Their official developer page (bandcamp.com/developer) only exposes oEmbed/embed player endpoints — not inventory or search.

Physical vinyl on Bandcamp is sold as **merch items**, not as releases. This has structural consequences:
- A vinyl record may have no associated album page at all (it's a standalone merch item on the artist's page).
- Alternatively, it may be attached to a release page as a "package" (merch variant of the release).
- There is no cross-artist search API. You cannot query "show me all Bandcamp vinyl listings for Artist X."

**What you can do:**
- If you already know an artist's Bandcamp URL (e.g., `artistname.bandcamp.com`), you can scrape their `/merch` or release pages to extract physical items.
- The embedded `TralbumData` JavaScript object on release pages contains structured JSON with pricing, stock quantity (`quantity_available`), and package type. This is the most reliable extraction point.
- The `/merch` page on a Bandcamp artist site lists physical items with stock status.

**Key risks:**
- **Discoverability is broken:** There is no way to search Bandcamp for vinyl by artist/title without knowing the URL. This makes Bandcamp unsuitable as a general search source. It only works as a "check this specific artist's Bandcamp page" addon.
- **Sold-out items stay listed:** Bandcamp shows sold-out items with "Sold Out" status rather than removing them. Scrapers must check `quantity_available` (from `TralbumData`) or the presence of "Sold Out" text — do not treat a listing as available without this check.
- **Artist Cloudflare protection:** Many Bandcamp-hosted pages on custom domains (e.g., `label.com`) are behind Cloudflare. The canonical `*.bandcamp.com` subdomain URLs are more scraper-friendly.
- **No canonical URL pattern for search:** Unlike Discogs or Juno, there is no URL you can construct for "search Bandcamp for [artist] [album] vinyl." The feature scope for Bandcamp must be limited to checking known URLs, not general discovery.

- Confidence: MEDIUM (Bandcamp developer page confirmed; TralbumData extraction pattern confirmed via community scrapers).

---

### Australian Vinyl Stores (Clarity, Egg, etc.)

**What breaks:**
Most independent AU vinyl stores run on Shopify. The existing `shopify.py` adapter already handles Shopify stores. Adding new AU stores is low-risk — it is primarily a configuration exercise (add new store URLs to the store list).

Key risks:
- **Not all AU stores are on Shopify.** Clarity Records (Melbourne) uses a custom platform. Egg Records (Melbourne) uses Shopify. Verify per store before assuming the existing adapter works.
- **Shopify storefront search:** The existing adapter likely hits `/search?q=...&type=product`. This works but returns HTML. Some Shopify stores disable storefront search or restrict it. The Shopify Storefront API (JSON) is more reliable but requires a store-specific API key that you would not have for a third-party store.
- **Pagination:** Shopify search results paginate. If the existing adapter only fetches the first page, it will miss results for common search terms (e.g., a well-known artist with many listings).

- Confidence: MEDIUM (based on existing working Shopify adapter and knowledge of AU store landscape).

---

### General Anti-Bot Risks Across All New Sources

- **Missing `User-Agent`:** Python httpx sends `python-httpx/x.x.x` by default. Every new scraper must set a realistic browser User-Agent.
- **Missing `Accept-Language` / `Accept` headers:** Sites fingerprint incomplete header sets. Send a full browser-like header block.
- **No delay between requests:** The existing Discogs adapter has known issues with 429 errors (noted in CONCERNS.md). New adapters must build in per-request delays from day one, not as a retrofit.
- **robots.txt:** The codebase notes a constraint to respect robots.txt. Verify robots.txt for each new source before building the adapter. Juno and eBay (HTML) may disallow scraping paths.

---

## Performance Fix Traps

### Trap 1: asyncio.gather() on scan_all_items() without a semaphore

The obvious fix for the sequential item scan loop (flagged in CONCERNS.md) is to replace it with `asyncio.gather(*[scan_item(db, i) for i in items])`. This will break immediately.

**What goes wrong:** With 20 wishlist items, gather launches 20 concurrent scan tasks. Each task hits Discogs and Shopify concurrently. Discogs rate limit is 60 requests/minute. 20 items x 3 Discogs requests = 60 requests fired simultaneously. Every one after the first few gets a 429. The scan returns empty results for most items.

**Prevention:** Use `asyncio.Semaphore(N)` wrapping each `scan_item()` call. A concurrency limit of 3-5 items scanning in parallel is sufficient and safe. Do not use `gather()` without a semaphore.

---

### Trap 2: APScheduler overlapping scan runs

If `scan_all_items()` is made faster (via parallelism), the job completes faster — but if it is still slow and the scheduler fires again before the previous run completes, two scan jobs run concurrently. Both write to the database simultaneously, creating duplicate listings.

**What goes wrong:** APScheduler's `AsyncIOScheduler` does not prevent job overlap by default. A slow run on a large wishlist overlapping with the next 6-hour trigger creates duplicate listing rows and inflated "best price" calculations.

**Prevention:** Set `misfire_grace_time` and use `max_instances=1` on the scheduled job. This is a one-line fix but is easy to miss.

---

### Trap 3: Response caching returning stale listing data

Adding a cache (e.g., `functools.lru_cache`, Redis, or in-memory dict) to the dashboard query will cause `_enrich_item()` to return old listings after a scan completes.

**What goes wrong:** A scan runs and updates listings. The cached dashboard query still holds the pre-scan snapshot. The user sees no change. If the cache TTL is long (e.g., 5 minutes), the dashboard appears broken.

**Prevention:** Cache at the right granularity. Cache the per-item enriched dict with a short TTL (30-60 seconds), not the full item list. Invalidate the cache entry for a specific item after `scan_item()` completes for that item. Never cache the full wishlist response.

---

### Trap 4: Fixing N+1 with joinedload() but fetching too much data

The N+1 fix (adding `joinedload(WishlistItem.listings)` to the query) eliminates separate per-item listing queries. But joinedload on listings can return hundreds of rows per item if listing history has accumulated (unbounded listing growth is flagged in CONCERNS.md).

**What goes wrong:** The join produces a cartesian product in result rows. A 50-item wishlist with 200 old listings per item returns 10,000 rows in one query. Memory spikes on both the DB and app side.

**Prevention:** Use `selectinload` instead of `joinedload` for one-to-many relationships (listings). `selectinload` fires a second query with an `IN (item_ids)` clause rather than a join, avoiding row explosion. Also add the listing cleanup job (CONCERNS.md) before applying the joinedload fix — otherwise it will be immediately painful.

---

### Trap 5: Email still blocking after "fixing" it

The CONCERNS.md notes that email sends block the HTTP request. A naive fix is to fire-and-forget with `asyncio.create_task(send_deal_email(...))`. This is slightly better but introduces a new bug.

**What goes wrong:** FastAPI's lifespan ends before the orphaned task completes if the server restarts or the request context closes. The task gets garbage-collected mid-send. Emails silently drop.

**Prevention:** Do not fire-and-forget email tasks without a reference. Either queue to a background task via APScheduler (add a one-off job), or use `asyncio.shield()` if the send is expected to complete quickly. For this project's scale, the simplest safe fix is an APScheduler one-off job for the email send.

---

### Trap 6: Adding DB indexes after data already exists

Adding indexes on `Listing.wishlist_item_id`, `Listing.url`, and `WishlistItem.is_active` (recommended in CONCERNS.md) is correct. But adding them via the existing custom migration system (`ALTER TABLE IF COLUMN NOT EXISTS`) is fragile for index creation.

**What goes wrong:** `CREATE INDEX` on a large `listings` table locks the table on PostgreSQL (by default). If done during a deployment with live traffic, scans and dashboard loads will stall until the index build completes.

**Prevention:** Use `CREATE INDEX CONCURRENTLY` in migrations. This is PostgreSQL-specific and does not block reads/writes. The custom migration system will need to be extended to support this, or migrate to Alembic before adding indexes.

---

## UI Redesign Risks

### Risk 1: Global CSS replacing Bootstrap without an audit

If Bootstrap is removed and replaced with Tailwind (or plain CSS), any Jinja2 template that uses Bootstrap utility classes (e.g., `mb-3`, `d-flex`, `text-muted`) will break silently — the page renders but looks broken.

**What goes wrong:** There are no tests for rendered HTML output. Visual regressions are invisible until manually reviewed. The scale of the change is easy to underestimate — Bootstrap classes may appear in base templates, macros, and individual route templates.

**Prevention:** Before switching CSS frameworks, grep the templates for Bootstrap-specific classes and count them. Do the migration template-by-template, not all at once. Keep Bootstrap loaded alongside the new CSS until every template has been converted.

---

### Risk 2: Record art as hero requires image dimensions you may not have

The Spotify-like aesthetic (record art as the dominant visual element) assumes a square cover image is always available. This is not true for all wishlist items.

**What goes wrong:** A wishlist item added by label (e.g., "Sub Pop Records") has no single cover image. An item added by artist may match releases with no Discogs image. Rendering a hero layout with a missing image shows a broken image placeholder or a large empty box.

**Prevention:** Design the layout with a graceful fallback state. A "no art" state should still be visually intentional — a placeholder with the label/artist initials on a colored background, not a broken img tag. Implement this before wiring up real images so the fallback is never an afterthought.

---

### Risk 3: Jinja2 macros becoming too complex

A Spotify-like card layout for each wishlist item (art, title, best price, sources) is more complex than the current list row. The temptation is to put all the logic in the Jinja2 macro.

**What goes wrong:** Jinja2 macros cannot be unit-tested. Complex price comparison logic, conditional display of "deal" badges, and listing source icons embedded in macros become invisible to debugging. When a price display bug occurs, there is no way to isolate it without rendering the full page.

**Prevention:** Keep Jinja2 templates dumb. All computation (best price, deal threshold, listing count) should be done in the Python route handler or `_enrich_item()` and passed as pre-computed values to the template. Templates should only choose which pre-computed value to display, not compute it.

---

### Risk 4: HTMX as a "quick win" that creates a new maintenance surface

The current stack has no JavaScript framework. Adding HTMX for partial page updates (search-as-you-type, scan status polling) is commonly recommended for this stack in 2025. However, HTMX introduces a new dependency and a new mental model.

**What goes wrong:** HTMX partial responses require new route variants that return HTML fragments (not full pages). These fragment routes are easy to forget to update when the main template changes. The "dumb template" principle above becomes harder to enforce when some routes return full pages and others return fragments of the same data.

**Prevention:** Only add HTMX if a specific interaction genuinely cannot be done with a full page reload (e.g., real-time scan progress). Do not add it for cosmetic reasons. If adopted, keep fragment routes co-located with their parent route, not scattered across different files.

---

### Risk 5: Inline styles for "quick" art background colors

When record art is used as a background or color source, there is a temptation to use inline Python color extraction (e.g., `colorthief`) to generate dynamic accent colors per card.

**What goes wrong:** Color extraction from an image URL requires either fetching the image server-side (adding latency to every page load) or doing it client-side (adding JavaScript). It is a hidden performance cost disguised as a visual feature.

**Prevention:** Defer dynamic color extraction entirely. Use a static color palette (e.g., map the first letter of the artist name to a fixed color) for the MVP redesign. If dynamic colors are wanted later, compute and store them at scan time, not at render time.

---

## Album Art Pitfalls

### Pitfall 1: Hotlinking Discogs images will get rate-limited or blocked

The existing Discogs adapter likely returns image URLs from the Discogs CDN (`i.discogs.com` or `api-img.discogs.com`). Serving these URLs directly to end users (by embedding them in `<img src="...">` in the dashboard) counts as hotlinking.

**What goes wrong:** Discogs rate-limits image requests. Forum posts confirm that `api-img.discogs.com` applies its own rate limit separate from the API rate limit. With a dashboard that loads 20-50 images per page, each page load fires 20-50 CDN requests. Discogs may return 429 or redirect to a placeholder. Images appear broken after a few page loads.

**Prevention:** Proxy and cache images locally. When a listing is created with a Discogs image URL, download the image and store it (either on disk, in the DB as bytea, or on a simple object store). Serve the local copy. Never hotlink CDN images in a production dashboard.

---

### Pitfall 2: Cover Art Archive reliability is good but lookup requires a MusicBrainz ID

The Cover Art Archive (coverartarchive.org) has no rate limit and is a strong fallback for cover images. However, the API requires a MusicBrainz Release ID (MBID), not a free-text artist/title search.

**What goes wrong:** You cannot query Cover Art Archive directly with "Artist Name + Album Title." You first need to resolve the MBID via the MusicBrainz search API, which has a rate limit of 1 request/second. For a wishlist of 50 items, MBID resolution takes ~50 seconds at the rate limit.

**Prevention:** Resolve and store the MBID at scan time, not at render time. Do not do MBID lookup on page load. Cache the resolved MBID in the database against the wishlist item so it is only looked up once.

---

### Pitfall 3: Bandcamp and Juno do not have centralized art APIs

Bandcamp releases include art embedded in the page (the `TralbumData` object contains image URLs). Juno listing pages include a product image in the HTML. But neither provides a stable, versioned image URL that can be treated as a permanent link.

**What goes wrong:** Image URLs on both platforms are CDN-hosted with path patterns that include content hashes or version numbers. A URL that works today may return 404 after a re-upload by the seller.

**Prevention:** Download and cache at scrape time. Treat scraped image URLs as temporary. Always store a local copy, not a reference to the remote URL.

---

### Pitfall 4: Missing art for label and subject searches

Wishlist items added as a label (e.g., "Warp Records") or subject ("German Techno 1992") have no single canonical cover image. The current Discogs adapter fetches multiple releases for these item types.

**What goes wrong:** Picking the "first" image from the first result looks arbitrary and often shows an unrelated release. The UI will look noisy or wrong if art is forced into a hero layout for these item types.

**Prevention:** Do not attempt to show release art for label/subject items. Use a genre or label-specific placeholder (a text-based avatar or a neutral graphic). Only show release art for album/artist item types where a specific release match is available.

---

## Mitigation Strategies

### Per-Source Scraping

| Source | Mitigation |
|--------|------------|
| Juno Records | Set browser User-Agent + full Accept headers; scrape by URL/structural position not class names; 1-2s jitter between requests; 1-2 max concurrent requests |
| eBay | Use Browse API, not HTML scraping; filter `buyingOptions:{FIXED_PRICE}` to exclude auctions; handle missing `shippingOptions` gracefully; auto-refresh OAuth token every 2h |
| Bandcamp | Limit scope to known artist URLs (not general search); check `quantity_available` in TralbumData; use canonical `*.bandcamp.com` URLs not custom domains |
| AU Shopify stores | Verify each store is actually Shopify before assuming adapter works; handle paginated search results |

### Performance Fix Order

Fix in this order to avoid cascading problems:
1. Add `selectinload` for listings (eliminates N+1 without data explosion) — safe to do first
2. Add listing cleanup job (prunes old data before index/join work is done)
3. Add `CREATE INDEX CONCURRENTLY` migrations via Alembic (not the custom migration system)
4. Add `Semaphore(3)` to `scan_all_items()` parallelism fix — safe only after Discogs rate limiting is confirmed working
5. Add `max_instances=1` to the APScheduler scan job — do this at the same time as the parallelism fix

### UI Redesign Order

1. Audit Bootstrap class usage in all templates before removing Bootstrap
2. Define a "no art" placeholder state in CSS before wiring any real images
3. Move all enrichment computation to Python route handlers; keep Jinja2 templates display-only
4. Do not add HTMX until a concrete interaction requirement demands it
5. Proxy and cache all external images at scan time; never hotlink CDN images

### Album Art Sourcing

Recommended fallback chain per item type:
- **Album/Artist item:** Discogs image (proxied/cached) → Cover Art Archive (if MBID resolved at scan time) → text-based placeholder
- **Label/Subject item:** text-based placeholder only (no release art)
- **Bandcamp/Juno listings:** cache image from TralbumData / product page at scrape time; treat remote URL as temporary

---

## Sources

- [eBay Browse API Overview](https://developer.ebay.com/api-docs/buy/browse/overview.html) — MEDIUM confidence (fetch timed out; rate limits confirmed via developer docs search)
- [eBay API Call Limits](https://developer.ebay.com/develop/get-started/api-call-limits) — MEDIUM confidence
- [Discogs API Terms of Use](https://support.discogs.com/hc/en-us/articles/360009334593-API-Terms-of-Use) — HIGH confidence
- [Discogs image rate limiting community thread](https://www.discogs.com/forum/thread/1033204) — MEDIUM confidence
- [Cover Art Archive API](https://musicbrainz.org/doc/Cover_Art_Archive/API) — HIGH confidence (no rate limit, requires MBID)
- [Bandcamp Developer page](https://bandcamp.com/developer) — HIGH confidence (only oEmbed/embed endpoints are public)
- [Bandcamp TralbumData extraction — community documentation](https://github.com/michaelherger/Bandcamp-API) — LOW confidence (undocumented internal API, may change)
- [asyncio Semaphore pattern for rate-limited scraping](https://rednafi.com/python/limit-concurrency-with-semaphore/) — HIGH confidence
- [Web scraping anti-bot detection 2025/2026](https://www.scrapingbee.com/blog/web-scraping-without-getting-blocked/) — MEDIUM confidence
- [eBay scraping via API vs HTML — 2026 guide](https://dev.to/agenthustler/how-to-scrape-ebay-in-2026-listings-prices-sellers-and-auction-data-gk2) — MEDIUM confidence
- [SQLAlchemy stale data / cache pitfalls](https://www.pythontutorials.net/blog/how-to-avoid-caching-in-sqlalchemy/) — MEDIUM confidence
- [Juno Records Scrapy crawler (historical reference)](https://github.com/mattmurray/juno_crawler) — LOW confidence (old project, confirms URL structure exists)
