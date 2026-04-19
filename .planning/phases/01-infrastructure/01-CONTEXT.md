# Phase 1: Infrastructure - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the app fast and source-agnostic. Decouple scan-on-add from HTTP response, eliminate N+1 queries on dashboard load, add TTL caching for enriched dashboard data, rate-limit concurrent scraping requests with a semaphore, and build an adapter registry that Phase 2 sources plug into.

This phase delivers backend changes only — no visual redesign (Phase 3). The adapter registry is the key deliverable that unblocks Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Scan Decoupling (PERF-01)
- **D-01:** Use FastAPI `BackgroundTasks` to decouple scan from HTTP response. The add endpoint commits the item and returns a redirect immediately; scan fires after the response is sent.
- **D-02:** The background task must open its own `SessionLocal()` DB session (request session is closed before task runs) and close it in a `finally` block.
- **D-03:** After adding an item, user is redirected to the dashboard immediately — item appears with no listings yet.
- **D-04:** Dashboard polls (auto-refreshes the new item card) every few seconds until listings appear. Polling stops when listings are populated or after a reasonable timeout.
- **D-05:** While a scan is in progress, the item card shows a subtle spinner indicator.

### Dashboard Performance (PERF-02, PERF-03)
- **D-06:** Fix N+1 queries by using `selectinload` (not `joinedload`) to batch-fetch listings for all items in a single IN query. `joinedload` risks row explosion with many listings per item.
- **D-07:** Cache the full enriched dashboard as a single cache entry (`maxsize=1, ttl=300`) using `cachetools.TTLCache`. One key for the whole dashboard — simple invalidation.
- **D-08:** Cache is invalidated (cleared) on any wishlist mutation (add, edit, delete) and on scan completion (both on-demand and scheduled).

### Scan Rate Limiting (PERF-04)
- **D-09:** Use `asyncio.Semaphore` to cap concurrent requests. Semaphore is global across all sources (not per-source) — simpler for Phase 1. Max concurrency: 3–5 (planner to tune based on Discogs rate limits).

### Adapter Registry (SRC-06)
- **D-10:** Registry lives in `app/services/scanner.py` (co-located with the scanner that uses it).
- **D-11:** Each registry entry is a dict with `name` (str), `fn` (async callable), and `enabled` (bool). Example: `{"name": "discogs", "fn": discogs.search_and_get_listings, "enabled": True}`. This allows disabling a source without removing it — important if sources get blocked or for future paid-tier differentiation.
- **D-12:** Scanner iterates the registry and calls only entries where `enabled=True`. Adding a new source in Phase 2 = create `app/services/{source}.py` + one dict entry in the registry.

### Scheduler Parallelism
- **D-13:** Parallelize the background scheduled scan using `asyncio.gather()` across all items simultaneously, controlled by the global semaphore (same one used for on-demand scans).
- **D-14:** Set `APScheduler max_instances=1` to prevent overlapping scan jobs if Railway restarts mid-scan.
- **D-15:** Keep the 6-hour scan interval. Claude to pick a sensible default if adjustments are warranted based on source rate limits once Phase 2 adapters are added.

### Future Context (paid app potential)
- **D-16:** The enabled flag on registry entries is intentional forward-thinking — if the app becomes multi-tenant or paid, sources can be toggled per deployment. Keep this extensibility in mind but don't over-engineer now.

### Claude's Discretion
- Exact semaphore concurrency value (3 or 5) — tune based on Discogs API rate limit headers
- Polling interval and timeout for the dashboard card refresh
- Whether polling uses a lightweight `/api/wishlist/{id}` endpoint or full page reload
- Scan interval adjustment if Discogs rate limits are tighter than expected with Phase 2 sources

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, constraints, iOS Shortcut API contract (must not break)
- `.planning/REQUIREMENTS.md` — PERF-01 through PERF-04, SRC-06 acceptance criteria

### Codebase
- `.planning/codebase/ARCHITECTURE.md` — Layered architecture, data flow, service layer patterns
- `.planning/codebase/CONCERNS.md` — N+1 query details (line refs), blocking email send issue, scan sequential bottleneck
- `.planning/codebase/CONVENTIONS.md` — Existing code style and patterns to follow

### Key Existing Files
- `app/routers/wishlist.py` — Current scan-on-add pattern (synchronous call before redirect), `_enrich_item()` N+1 source
- `app/services/scanner.py` — Current scanner; where registry will be added
- `app/services/discogs.py` — Existing adapter pattern to replicate in registry
- `app/scheduler.py` — Background scheduler; needs parallelization and `max_instances=1`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/services/discogs.py` and `app/services/shopify.py`: Existing adapter functions matching `async def search_and_get_listings(query, item_type) -> list[dict]` — this is the interface new adapters must implement
- `app/database.py:get_db()` / `SessionLocal`: Session factory to use in background tasks

### Established Patterns
- Route handlers use `Depends(get_db)` for DB sessions — background tasks cannot use this, must call `SessionLocal()` directly
- Services return standardized listing dicts (title, price, url, ships_from, source, currency) — registry must preserve this contract
- `_enrich_item()` in `wishlist.py:26` is the N+1 source — needs `selectinload` in the query that fetches items

### Integration Points
- `web_router.post("/wishlist/add")` — where `BackgroundTasks` parameter is added and scan is moved to background
- `api_router.post("/wishlist")` — iOS Shortcut endpoint; same decoupling needed, API contract (`POST /api/wishlist`, `X-API-Key`) must not change
- `scheduler.py:scan_all_items()` — where `asyncio.gather()` + semaphore replaces the sequential loop
- Dashboard route `GET /` — where `selectinload` is added to the item query and cache is checked before enrichment

</code_context>

<specifics>
## Specific Ideas

- User noted this may become a paid app in the future — the `enabled` flag on registry entries is the key design decision that accommodates this without overengineering now
- Polling UX: item card should show a spinner while scan is running, disappear when listings appear — keep it subtle, not intrusive

</specifics>

<deferred>
## Deferred Ideas

- Per-source rate limit concurrency in the registry (e.g., Discogs=3, eBay=10) — deferred to Phase 2 when we know the actual limits of each new source
- Disabling/enabling sources via environment variable or admin UI — deferred until paid-app scope is clearer
- Structured logging (replacing `print()`) — noted in CONCERNS.md, out of scope for Phase 1 unless planner includes it as a low-effort add

</deferred>

---

*Phase: 01-infrastructure*
*Context gathered: 2026-04-02*
