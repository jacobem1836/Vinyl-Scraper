# Research Summary

**Project:** Vinyl Wishlist Manager
**Domain:** Personal vinyl record price tracker with multi-source scraping
**Researched:** 2026-04-02
**Confidence:** MEDIUM-HIGH

## Executive Summary

This milestone adds four things to the existing FastAPI/PostgreSQL/Railway app: new scraping sources (Juno, Bandcamp, eBay AU, Clarity Records, Discrepancy Records), async scan decoupling for the iOS Shortcut, in-process caching for dashboard performance, and a Spotify-inspired UI redesign. The stack is already well-chosen for the use case and needs no replacement — only extension. The adapter pattern needs formalising via a registry so new sources can be added without touching the scanner. Both the caching and scan-decoupling changes must be implemented together in the same phase or the cache will serve stale results indefinitely after background scans complete.

The primary risk is scraping fragility: each new source has a different platform (HTML, official API, BigCommerce, Neto) and different anti-bot posture. eBay is the only source with a real API and must use it — attempting HTML scraping against Akamai bot protection is a dead end for a personal tool. Bandcamp has a structural limitation that prevents general search; it can only check known artist URLs, which fundamentally limits its value as a price discovery source. Juno and the AU stores are medium-difficulty HTML targets that require careful selector choice and per-domain rate limiting from the start.

The UI redesign is the highest complexity change relative to lines of code — removing Bootstrap and replacing with custom CSS risks silent visual regressions across all templates. The mitigation is a strict template audit first and a firm rule: all enrichment computation stays in Python, templates stay display-only. Album art sourcing is a hidden cost: Discogs CDN images cannot be hotlinked (rate-limited), so image proxying and local caching must be planned from the beginning, not retrofitted.

---

## Key Findings

### Stack Decisions

The existing stack (FastAPI, SQLAlchemy, PostgreSQL, APScheduler, httpx, Jinja2) requires no replacements. Extensions needed:

- **BeautifulSoup4** — HTML parsing for Juno, Bandcamp, Clarity, Discrepancy; not currently in project
- **ebay-oauth-python-client** — OAuth token management for eBay Browse API; keeps token refresh out of application logic
- **cachetools (TTLCache)** — in-process TTL caching with clean invalidation API; preferred over fastapi-cache2 (slower maintenance) and functools.lru_cache (no TTL)
- **FastAPI BackgroundTasks** — built-in, zero dependencies; correct tool for fire-and-forget scan-on-add; must open its own DB session (request-scoped session is closed before task runs)
- **asyncio.Semaphore** — per-source concurrency cap; must be added to all new adapters and to scan_all_items() before parallelising the item loop

**One dependency to defer:** aiolimiter/aiometer are not needed unless the simple semaphore + sleep approach proves insufficient in practice.

### Table Stakes Features

Must exist for this milestone to be considered complete:

- **Best price displayed per card** — AUD landed cost, prominently badged, not buried in a detail view
- **Source breakdown on every listing** — source name + ships-from region on every result row
- **Condition filter on alerts** — per-item condition gate; top Discogs complaint; non-negotiable
- **"Last checked" timestamp** — users need to know if prices are fresh given the 6-hour scan cycle
- **Remove / mark as purchased** — wishlist hygiene; frustrating if clunky
- **Async scan on add** — iOS Shortcut must get a response in under 2 seconds; scan must run in background
- **AUD as the default currency throughout** — apply FX at ingestion; never show USD/GBP/EUR to user
- **Price history / trend** — is $30 cheap? Context matters; popsike.com built a business on this gap

Should have (differentiators for this milestone):

- **Multi-source aggregation view** — single card showing Discogs + AU stores + Juno in one place; this is the core differentiator
- **"Ships from AU" filter / badge** — AU seller at $5 more is often cheaper landed than overseas at $5 less
- **Album artwork as card hero** — with graceful "no art" fallback for label/subject searches
- **Per-item manual rescan ("check now")** — power-user feature; low implementation cost once async decoupling exists

Defer to v2+:

- Pressing/edition awareness (complex metadata; no current source provides it consistently)
- Wishlist priority/ranking (simple to add but not blocking anything)
- Dynamic color extraction from cover art (hidden performance cost; use static palette)
- Egg Records scraping (Common Ground platform; no community precedent; defer)
- Price history charting (store the data now; build the UI later)

### Architecture Approach

The current architecture has two problems that must be fixed before adding sources: scanner.py hard-codes adapter imports (add a registry), and both add-item routes call scan synchronously (decouple with BackgroundTasks). These two changes interact — do them in the same phase. The adapter registry uses a simple list of callables (no class inheritance needed) with a TypedDict defining the expected return shape. The cache must invalidate on scan completion; wiring this in at the same time as scan decoupling prevents stale dashboard reads.

**Major components:**

1. **Adapter registry** (`app/services/registry.py`) — list of `search_and_get_listings(query, item_type)` callables; scanner iterates this list, never imports adapters directly
2. **Per-source adapters** (`app/services/juno.py`, `bandcamp.py`, `ebay.py`, etc.) — each implements the callable interface; contains its own semaphore and rate limiting
3. **Background scan runner** (`_scan_in_background`) — opens its own SessionLocal; called via BackgroundTasks after response is sent; invalidates cache on completion
4. **TTLCache layer** (`app/services/cache.py`) — whole-dashboard TTLCache(maxsize=1, ttl=300); invalidated on scan complete and wishlist mutations
5. **Frontend** — custom CSS (no Bootstrap), CSS Grid card layout, Jinja2 macros for card and listing row; all enrichment computed in Python route handlers

### Watch Out For

1. **asyncio.gather() on scan_all_items() without a Semaphore** — parallelising the item loop without a concurrency cap fires 20+ simultaneous Discogs requests, hits the 60 req/min rate limit immediately, and returns empty results for most items. Fix: wrap each scan_item() in Semaphore(3-5).

2. **BackgroundTasks using the request-scoped DB session** — the SQLAlchemy session from `Depends(get_db)` is closed when the request ends, which is before the background task runs. The task must open its own `SessionLocal()` and close it in a finally block.

3. **Hotlinking Discogs CDN images** — `api-img.discogs.com` has a separate rate limit from the API. A dashboard with 20-50 images fires 20-50 CDN requests per page load. Discogs returns 429 or broken images after a few loads. Fix: download and proxy images at scan time; never embed remote CDN URLs directly in templates.

4. **Cache invalidation timing** — adding TTLCache without wiring invalidation to scan completion means the dashboard shows pre-scan data until TTL expires. Users trigger a scan and see no change. Fix: call `invalidate_dashboard_cache()` at the end of the background scan task.

5. **APScheduler job overlap** — if scan_all_items() becomes faster via parallelism, but a large wishlist still takes longer than 6 hours, the scheduler fires a second run before the first completes. Both write listings concurrently, creating duplicates. Fix: set `max_instances=1` on the APScheduler job at the same time as adding parallelism.

6. **Removing Bootstrap without a template audit** — Bootstrap utility classes (mb-3, d-flex, text-muted) appear silently throughout templates. Removing Bootstrap before auditing produces a broken layout with no test to catch it. Fix: grep all templates for Bootstrap classes; migrate template-by-template; keep Bootstrap loaded alongside new CSS until all templates are converted.

---

## Source-by-Source Feasibility

| Source | Feasibility | Approach | Key Risk |
|--------|-------------|----------|----------|
| **Juno Records** | MEDIUM | httpx + BeautifulSoup4; search URL `/search/?q={query}&cat=vinyl`; set browser User-Agent | CSS class names change without notice; scrape by structural position not class names; 403 without correct headers |
| **Bandcamp** | LOW-MEDIUM (limited scope) | httpx + BeautifulSoup4; but only useful for known artist URLs, not general search | No cross-artist search API exists; physical vinyl is merch not releases; must check `quantity_available` to avoid sold-out results; general price discovery is not possible |
| **eBay AU** | MEDIUM-HIGH | Browse API (`/item_summary/search`); OAuth Client Credentials; filter `marketplace_id=EBAY_AU` + `buyingOptions:{FIXED_PRICE}` | Token expires every 2 hours — must auto-refresh; auctions vs buy-it-now handling; shipping cost not always returned in API response |
| **Clarity Records** | HIGH | httpx + BeautifulSoup4; BigCommerce platform; search at `/search.php?search_query={query}`; predictable HTML structure | Low risk; class names are BigCommerce-standard; primary uncertainty is confirming current selectors via live inspection |
| **Discrepancy Records** | MEDIUM | httpx + BeautifulSoup4; Neto platform; search URL `?rf=kw&kw={query}`; less community precedent than Shopify/BigCommerce | Neto HTML is less predictable; selector identification requires more live inspection time; highest-value AU target (800k titles, free domestic delivery) |
| **Egg Records** | DEFER | Common Ground platform; no prior scrapers found | Unknown platform structure; small catalogue relative to effort; recommend deferring to a later iteration |

**Recommended build order for sources:** eBay AU (API, highest data quality) → Discrepancy Records (highest AU value) → Clarity Records (low friction BigCommerce) → Juno Records (medium effort, high value) → Bandcamp (scope-limited, build last with clear constraints on what it can do).

---

## Recommended Phase Order

### Phase 1: Infrastructure — Adapter Registry + Scan Decoupling + Cache

**Rationale:** These three changes are tightly coupled and create the foundation everything else depends on. The adapter registry must exist before any new source can be added. Scan decoupling must happen before the iOS Shortcut UX is acceptable. Cache invalidation must be wired to scan completion at the same time the background scan is introduced — retrofitting it later is error-prone.

**Delivers:** Source-agnostic scanner; async add-item response; 5-minute dashboard cache with correct invalidation; APScheduler max_instances=1 guard.

**Addresses:** iOS Shortcut timeout; dashboard performance; N+1 query fix (use selectinload before joinedload); listing cleanup job before adding indexes.

**Avoids:** Cache invalidation bug; background task DB session pitfall; APScheduler overlap.

### Phase 2: New Scraping Sources

**Rationale:** The adapter registry from Phase 1 makes this additive — each source is a new file and one line in registry.py. eBay first because it returns structured JSON with no HTML parsing risk. AU stores next because they are the core differentiator. Juno last because of selector fragility.

**Delivers:** eBay AU listings; Discrepancy Records; Clarity Records; Juno Records. Each with per-source semaphore and rate limiting baked in from day one.

**Avoids:** Unguarded asyncio.gather(); missing User-Agent headers; robots.txt violations.

**Defers:** Bandcamp (limited to known-URL mode; lower priority); Egg Records (platform too opaque).

### Phase 3: UI Redesign

**Rationale:** UI comes after data is correct and fast. The redesign depends on the enrichment data (best price, source breakdown, condition) being reliable — which Phase 1 and 2 deliver. Album art sourcing is non-trivial and must be scoped carefully.

**Delivers:** Custom CSS replacing Bootstrap; CSS Grid card layout; album art with local proxy/cache; "no art" placeholder for label/subject items; all enrichment logic in Python (templates display-only).

**Avoids:** Bootstrap removal before template audit; hotlinked Discogs CDN images; dynamic color extraction at render time; HTMX unless a concrete interaction demands it.

**Phase ordering rationale:**

- Phase 1 before Phase 2 because the adapter registry must exist before new sources can be added cleanly.
- Phase 1 before Phase 3 because the UI depends on enriched data that is correct and fast.
- Phase 3 last because visual changes have the highest regression risk and lowest dependency on being first.
- Bandcamp deferred within Phase 2 because its limited scope (known URLs only) means it should be scoped as an explicit constraint before implementation starts.

### Research Flags

Needs deeper investigation during planning:
- **Phase 2 / Bandcamp:** Scope must be explicitly bounded — is "check known artist URLs" enough value to build at all? Decide before planning the task.
- **Phase 2 / eBay token refresh:** The auto-refresh mechanism for 2-hour OAuth tokens needs a concrete implementation plan before the adapter is built.
- **Phase 3 / image proxy:** Decide on storage mechanism (filesystem, DB bytea, or object store) before building the art pipeline. Each has different Railway deployment implications.

Standard patterns (no additional research needed):
- **Phase 1 / BackgroundTasks + SessionLocal:** FastAPI-documented pattern; implementation is clear.
- **Phase 1 / cachetools TTLCache:** Well-established library; invalidation strategy is straightforward.
- **Phase 1 / adapter registry:** Simple list of callables; no framework needed.
- **Phase 2 / BigCommerce (Clarity):** Structurally identical to existing Shopify adapter.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack is correct; new dependencies (BS4, cachetools, ebay-oauth-python-client) are well-established |
| Features | MEDIUM-HIGH | AU-specific shipping estimates are approximations; GST handling intentionally excluded from landed cost model |
| Architecture | HIGH | Adapter registry and BackgroundTasks patterns are FastAPI-native and verified against official docs; DB session pitfall confirmed from community discussion |
| Pitfalls | MEDIUM-HIGH | Discogs CDN rate limiting confirmed via forum posts (MEDIUM); eBay Akamai protection confirmed (HIGH); Bandcamp scope limitation confirmed via developer page (HIGH) |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Juno HTML selectors:** Cannot be confirmed without live inspection. A 403 was returned during research without browser headers. First implementation task must be a selector audit with correct User-Agent set.
- **Bandcamp scope decision:** Research confirms Bandcamp cannot do general search. The decision of whether to include it at all (and in what form) needs an explicit call before Phase 2 planning.
- **Image proxy storage:** Three options (filesystem, DB bytea, object store) have different Railway deployment tradeoffs. Decide during Phase 3 planning, not during implementation.
- **eBay call limit:** The ~5,000 calls/day figure is community-reported; official docs require a developer login to confirm exact limits. Not a practical concern for personal use regardless.
- **Discrepancy Records selectors:** Neto is less-scraped than Shopify/BigCommerce. Expect more time on selector identification than for Clarity Records.

---

## Sources

### Primary (HIGH confidence)
- [FastAPI BackgroundTasks docs](https://fastapi.tiangolo.com/tutorial/background-tasks/) — scan decoupling pattern, DB session lifecycle
- [eBay Browse API Overview](https://developer.ebay.com/api-docs/buy/browse/overview.html) — API structure, filtering, marketplace parameters
- [eBay Finding API Decommission](https://community.ebay.com/t5/Traditional-APIs-Search/Alert-Finding-API-and-Shopping-API-to-be-decommissioned-in-2025/td-p/34222062) — confirmed decommissioned February 2025
- [cachetools documentation](https://cachetools.readthedocs.io/en/stable/) — TTLCache API and invalidation
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/) — adapter protocol pattern
- [Bandcamp Developer page](https://bandcamp.com/developer) — confirmed no public search API
- [Cover Art Archive API](https://musicbrainz.org/doc/Cover_Art_Archive/API) — MBID requirement, no rate limit

### Secondary (MEDIUM confidence)
- [Scraperly — Bandcamp difficulty (March 2026)](https://scraperly.com/scrape/bandcamp-music) — "Very Easy" rating, static HTML confirmed
- [Discogs image rate limiting community thread](https://www.discogs.com/forum/thread/1033204) — CDN rate limit confirmed via community
- [asyncio Semaphore rate limiting](https://rednafi.com/python/limit-concurrency-with-semaphore/) — pattern validation
- [eBay scraping 2026 guide](https://dev.to/agenthustler/how-to-scrape-ebay-in-2026-listings-prices-sellers-and-auction-data-gk2) — Akamai protection confirmed

### Tertiary (LOW confidence)
- [Bandcamp TralbumData extraction](https://github.com/michaelherger/Bandcamp-API) — undocumented internal API; community-confirmed but may change
- [Juno Records MP3tag thread](https://community.mp3tag.de/t/juno-records/3960) — confirms HTML scraping works; old reference
- [Juno Records Scrapy crawler](https://github.com/mattmurray/juno_crawler) — historical; confirms URL structure but selectors likely stale

---

*Research completed: 2026-04-02*
*Ready for roadmap: yes*
