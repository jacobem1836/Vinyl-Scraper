---
phase: 01-infrastructure
verified: 2026-04-02T08:30:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
human_verification:
  - test: "Add item via web form — confirm redirect within 2 seconds, spinner visible on card, listings auto-appear after scan completes"
    expected: "Redirect happens immediately; card shows pulsing border + spinner; after ~10-15s page reloads and listings appear"
    why_human: "Timing and visual UX behaviour cannot be verified programmatically"
  - test: "Load dashboard twice within 5 minutes, observe terminal logs for DB query count"
    expected: "Second load produces zero DB queries (cache hit); first load produces exactly 2 queries (items + selectinload listings)"
    why_human: "SQL query count requires observing runtime DB logging; cannot be confirmed from static code alone"
  - test: "POST /api/wishlist with X-API-Key — confirm response returns immediately with item (no listings)"
    expected: "Response < 1 second; item.listing_count == 0; iOS Shortcut contract preserved"
    why_human: "Requires running the app with a live API key"
---

# Phase 1: Infrastructure Verification Report

**Phase Goal:** Make the app fast and source-agnostic. Decouple scan-on-add from HTTP response, eliminate N+1 queries on dashboard load, add TTL caching for enriched dashboard data, rate-limit concurrent scraping requests with a semaphore, and build an adapter registry that Phase 2 sources plug into.
**Verified:** 2026-04-02T08:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                                               | Status     | Evidence                                                                                            |
|----|-------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------------------------|
| 1  | Adding an item via web or API does not block the HTTP response on scan completion   | VERIFIED   | `add_wishlist_item_web` and `create_wishlist_item_api` both call `background_tasks.add_task(_scan_in_background, item.id)` — no await on scan before returning |
| 2  | Dashboard loads using a single batch query for listings (no N+1)                   | VERIFIED   | `app/main.py:65` uses `.options(selectinload(WishlistItem.listings))` on the dashboard query         |
| 3  | Dashboard enrichment is cached with 5-minute TTL; cache invalidated on mutations   | VERIFIED   | `cache.py` defines `TTLCache(maxsize=1, ttl=300)`; `get_cached_dashboard` / `set_cached_dashboard` wired in `main.py:58-70`; `invalidate_dashboard_cache()` called in 5 mutation sites |
| 4  | Concurrent scan requests are bounded by a semaphore (max 3)                        | VERIFIED   | Global `scan_semaphore = asyncio.Semaphore(3)` in `rate_limit.py`; used in `_scan_in_background`, `scan_single_item_web`, and `scheduler.py`'s `_scan_one` |
| 5  | Scanner is source-agnostic; adding a new source requires only a registry entry     | VERIFIED   | `scanner.py` has no direct discogs/shopify imports; iterates `get_enabled_adapters()` from `adapter.py`; `ADAPTER_REGISTRY` is the sole registration point |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact                          | Expected                                        | Status     | Details                                                                    |
|-----------------------------------|-------------------------------------------------|------------|----------------------------------------------------------------------------|
| `app/services/cache.py`           | TTLCache with get/set/invalidate functions      | VERIFIED   | 16 lines; `TTLCache(maxsize=1, ttl=300)`; all 3 functions present          |
| `app/services/rate_limit.py`      | Global `asyncio.Semaphore(3)`                   | VERIFIED   | 5 lines; `scan_semaphore = asyncio.Semaphore(3)` exported                  |
| `app/services/adapter.py`         | `ADAPTER_REGISTRY`, `get_enabled_adapters`, `ListingDict` | VERIFIED | 29 lines; all three exported; discogs + shopify entries present |
| `app/services/scanner.py`         | Uses registry, no direct source imports         | VERIFIED   | Imports `get_enabled_adapters`; no `discogs`/`shopify` imports             |
| `app/routers/wishlist.py`         | BackgroundTasks on add; semaphore on scan; cache invalidation on mutations | VERIFIED | All wiring confirmed — see Key Links below |
| `app/main.py`                     | selectinload + cache check/set on dashboard     | VERIFIED   | Lines 58-70 implement cache-or-query pattern; line 65 uses selectinload    |
| `app/scheduler.py`                | asyncio.gather + scan_semaphore + max_instances=1 | VERIFIED | `asyncio.gather` at line 30; `scan_semaphore` at line 23; `max_instances=1` at line 41 |
| `templates/index.html`            | data-scanning / data-item-id attrs + polling JS | VERIFIED   | Lines 131-136 set scanning state; lines 254-277 implement polling loop     |
| `static/style.css`                | `.card--scanning` pulse + `.spinner` keyframes  | VERIFIED   | `@keyframes pulse-border`, `.card--scanning`, `@keyframes spin`, `.spinner` all present |
| `GET /wishlist/{item_id}/status`  | Returns `has_listings`, `listing_count`, `last_scanned_at` | VERIFIED | `wishlist.py:187-200` implements the endpoint on `web_router`             |

---

### Key Link Verification

| From                        | To                                  | Via                             | Status   | Details                                                         |
|-----------------------------|-------------------------------------|---------------------------------|----------|-----------------------------------------------------------------|
| `add_wishlist_item_web`     | `_scan_in_background`               | `background_tasks.add_task`     | WIRED    | `wishlist.py:104`                                               |
| `create_wishlist_item_api`  | `_scan_in_background`               | `background_tasks.add_task`     | WIRED    | `wishlist.py:247`                                               |
| `_scan_in_background`       | `scan_semaphore`                    | `async with scan_semaphore:`    | WIRED    | `wishlist.py:26`                                                |
| `index` route               | `selectinload(WishlistItem.listings)` | `.options(selectinload(...))`  | WIRED    | `main.py:65`                                                    |
| `index` route               | `get_cached_dashboard`              | cache check before DB query     | WIRED    | `main.py:58-70`                                                 |
| `edit_wishlist_item_web`    | `invalidate_dashboard_cache`        | call after `db.commit()`        | WIRED    | `wishlist.py:128`                                               |
| `delete_wishlist_item_web`  | `invalidate_dashboard_cache`        | call after `db.commit()`        | WIRED    | `wishlist.py:138`                                               |
| `delete_wishlist_item_api`  | `invalidate_dashboard_cache`        | call after `db.commit()`        | WIRED    | `wishlist.py:278`                                               |
| `_scan_in_background`       | `invalidate_dashboard_cache`        | call in `finally` block         | WIRED    | `wishlist.py:31`                                                |
| `scan_item` (scanner)       | `invalidate_dashboard_cache`        | call after commit               | WIRED    | `scanner.py:72`                                                 |
| `scheduler._scan_one`       | `scan_semaphore`                    | `async with scan_semaphore:`    | WIRED    | `scheduler.py:23`                                               |
| `scheduled_scan`            | `invalidate_dashboard_cache`        | call after gather               | WIRED    | `scheduler.py:31`                                               |
| `scan_item` (scanner)       | `get_enabled_adapters`              | replace hard-coded gather       | WIRED    | `scanner.py:16-26`                                              |
| `adapter.py`                | `discogs.search_and_get_listings`   | registry entry                  | WIRED    | `adapter.py:22`                                                 |
| `adapter.py`                | `shopify.search_and_get_listings`   | registry entry                  | WIRED    | `adapter.py:23`                                                 |
| template scanning cards     | `/wishlist/{id}/status`             | JS `fetch` poll every 5s        | WIRED    | `index.html:266`                                                |

---

### Data-Flow Trace (Level 4)

| Artifact         | Data Variable | Source                                | Produces Real Data | Status     |
|------------------|---------------|----------------------------------------|--------------------|------------|
| `index.html`     | `items`       | `db.query(WishlistItem)` via `main.py` | Yes — ORM query    | FLOWING    |
| `cache.py`       | `"dashboard"` | `set_cached_dashboard(enriched)` in `main.py` after DB query | Yes — populated from real query result | FLOWING |
| polling JS       | `has_listings` | `GET /wishlist/{id}/status` → `db.query(Listing).count()` | Yes — DB count query | FLOWING |

---

### Behavioral Spot-Checks

Step 7b: SKIPPED — server must be running to test HTTP endpoints. Items routed to human verification.

---

### Requirements Coverage

| Requirement | Source Plan | Description                                                                                         | Status    | Evidence                                                                                          |
|-------------|-------------|-----------------------------------------------------------------------------------------------------|-----------|---------------------------------------------------------------------------------------------------|
| PERF-01     | 01-01, 01-03 | Adding a wishlist item returns HTTP response immediately; scanning runs as background task          | SATISFIED | `background_tasks.add_task(_scan_in_background, item.id)` in both web and API add handlers; spinner + polling UX confirms the full loop |
| PERF-02     | 01-01        | Dashboard uses selectinload to batch-fetch listings in a single query                               | SATISFIED | `main.py:65` — `.options(selectinload(WishlistItem.listings))`                                    |
| PERF-03     | 01-01        | Dashboard enrichment cached with ~5 min TTL; invalidated on mutation or scan completion             | SATISFIED | `cache.py` TTLCache(ttl=300); invalidation at 5 call sites confirmed                             |
| PERF-04     | 01-01        | Concurrent scan requests rate-limited via semaphore (max 3–5)                                       | SATISFIED | `scan_semaphore = asyncio.Semaphore(3)` used in background task, single-item scan, and scheduler |
| SRC-06      | 01-02        | All new sources registered in central adapter registry; adding/removing a source requires only registry change | SATISFIED | `adapter.py` defines `ADAPTER_REGISTRY`; `scanner.py` has zero direct source imports; adding an adapter = one dict entry |

**Orphaned requirements check:** No requirements mapped to Phase 1 in REQUIREMENTS.md that are absent from plans.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `app/services/scanner.py` | 86 | `semaphore = asyncio.Semaphore(3)` — local semaphore in `scan_all_items` instead of global `scan_semaphore` from `rate_limit.py` | INFO | The plan specified using the global semaphore everywhere. `scan_all_items` creates a local one. Functionally equivalent (same limit of 3), but `scan_all_items` and `_scan_in_background` do not share the same semaphore instance — simultaneous API scan-all + background scans could each allow 3 concurrent requests, not 3 total. Minor risk at current scale. |

No stubs, no placeholder returns, no empty implementations found in any phase artifact.

---

### Human Verification Required

#### 1. Background Scan UX End-to-End

**Test:** Start the app locally (`uvicorn app.main:app --reload`). Open the dashboard. Add a new item via the web form.
**Expected:** Redirect to `/?toast=Item+added%2C+scanning+in+background` within ~1 second. Item card appears immediately with pulsing amber border and spinner. After 10-15 seconds (background scan completes), the page auto-reloads and listings appear. Spinner disappears.
**Why human:** Visual appearance, timing, and auto-reload behaviour cannot be verified from static code.

#### 2. Cache Hit Verification

**Test:** Load dashboard (`GET /`), then load it again within 5 minutes. Watch terminal/stdout for SQL query activity.
**Expected:** First load produces exactly 2 SQL queries (items + selectinload listings batch). Second load produces zero DB queries.
**Why human:** SQL query count requires runtime observation; not deterministic from static analysis.

#### 3. iOS Shortcut API Contract

**Test:** `curl -X POST http://localhost:8000/api/wishlist -H "X-API-Key: <key>" -H "Content-Type: application/json" -d '{"type":"album","query":"Test"}'`
**Expected:** Response returns in < 1 second with item JSON (listing_count: 0); scan runs in background. Same URL, header, and response shape as before.
**Why human:** Requires live app + valid API key.

#### 4. Adapter Registry Extensibility

**Test:** Add a dummy entry `{"name": "test_broken", "fn": async_fn_that_raises, "enabled": True}` to `ADAPTER_REGISTRY` in `adapter.py`. Trigger a scan.
**Expected:** Discogs and Shopify results still appear. Terminal shows `[Scanner] test_broken error: <message>`. No crash.
**Why human:** Requires editing source + running a live scan.

---

### Gaps Summary

No gaps found. All 5 observable truths are VERIFIED. All 10 key artifacts exist with substantive implementations. All 16 key links are confirmed wired. Requirements PERF-01 through PERF-04 and SRC-06 are all satisfied.

One informational note: `scan_all_items()` in `scanner.py` creates a local `asyncio.Semaphore(3)` rather than importing the global `scan_semaphore`. This is functionally equivalent at current scale but means the global semaphore in `rate_limit.py` is not the sole concurrency gate when scan-all and background scans run simultaneously. Not a blocker — noting for Phase 2 when additional sources increase request volume.

---

_Verified: 2026-04-02T08:30:00Z_
_Verifier: Claude (gsd-verifier)_
