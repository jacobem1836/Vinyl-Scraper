---
phase: 01-infrastructure
plan: "01"
subsystem: infra
tags: [cachetools, asyncio, semaphore, selectinload, background-tasks, apscheduler]

requires: []

provides:
  - Dashboard TTL cache (cachetools TTLCache, 5-minute expiry)
  - Global scan semaphore (asyncio.Semaphore(3)) limiting concurrent scan requests
  - Scan decoupled from HTTP response via FastAPI BackgroundTasks
  - N+1 query fix via SQLAlchemy selectinload
  - Scheduler parallelized with asyncio.gather + max_instances=1

affects: [02-new-sources, 03-ui-redesign]

tech-stack:
  added:
    - cachetools>=5.5.0
  patterns:
    - BackgroundTasks for fire-and-forget scan after item add
    - Module-level asyncio.Semaphore for cross-request concurrency control
    - TTLCache keyed by single constant for page-level caching
    - selectinload for eager loading relationships (N+1 fix)
    - invalidate_dashboard_cache called on all mutations

key-files:
  created:
    - app/services/cache.py
    - app/services/rate_limit.py
  modified:
    - requirements.txt
    - app/routers/wishlist.py
    - app/main.py
    - app/services/scanner.py
    - app/scheduler.py

key-decisions:
  - "semaphore(3): Discogs 60/min limit; 3 concurrent items with 2-3 sources each stays well under"
  - "TTLCache maxsize=1: single dashboard endpoint; key='dashboard'"
  - "Cache invalidated on: edit, delete (web+api), and after every scan_item completion"
  - "API POST /api/wishlist now returns immediately (iOS Shortcut contract preserved, just faster)"
  - "Scheduler rebuilt from scratch: scan_all_items replaced with gather + per-item semaphore"

patterns-established:
  - "Background scan pattern: BackgroundTasks.add_task(_scan_in_background, item.id) with own SessionLocal"
  - "Cache invalidation: call invalidate_dashboard_cache() after any DB mutation affecting dashboard"

requirements-completed: [PERF-01, PERF-02, PERF-03, PERF-04]

duration: 3min
completed: 2026-04-02
---

# Phase 1 Plan 1: Backend Performance Summary

**Scan decoupled from HTTP via BackgroundTasks; dashboard N+1 fixed with selectinload; TTLCache added; scheduler parallelized with asyncio.gather + semaphore(3)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-02T07:51:41Z
- **Completed:** 2026-04-02T07:54:45Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Item add via web and iOS Shortcut API now returns immediately; scan runs in background
- Dashboard N+1 eliminated: single `SELECT ... WHERE wishlist_item_id IN (...)` via selectinload
- 5-minute TTL cache for dashboard enrichment; invalidated on all mutations + scan completions
- Scheduler rebuilt with `asyncio.gather` so all items scan in parallel, bounded by semaphore(3)
- `max_instances=1` added to scheduler job to prevent overlapping scheduled runs

## Task Commits

1. **Task 1: Add cachetools dependency and create cache module** - `231e10e` (feat)
2. **Task 2: Create global semaphore module** - `7599eba` (feat)
3. **Task 3: Decouple scan, fix N+1, wire cache, parallelize scheduler** - `ac15a93` (feat)

## Files Created/Modified

- `requirements.txt` - Added cachetools>=5.5.0
- `app/services/cache.py` - TTLCache(maxsize=1, ttl=300); get/set/invalidate functions
- `app/services/rate_limit.py` - Module-level asyncio.Semaphore(3) as scan_semaphore
- `app/routers/wishlist.py` - BackgroundTasks on add; semaphore on scan; cache invalidation on mutations
- `app/main.py` - selectinload for N+1 fix; dashboard cache check/set
- `app/services/scanner.py` - invalidate_dashboard_cache after scan_item completes
- `app/scheduler.py` - asyncio.gather + scan_semaphore + max_instances=1

## Decisions Made

- Semaphore at 3: Discogs caps at 60 req/min; 3 concurrent items with ~2 sources each = ~6 req/min peak during scan, well under limit
- iOS Shortcut API contract fully preserved (same URL, same X-API-Key header, same response model — just faster)
- Cache invalidated eagerly on every mutation to avoid stale dashboard state

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Performance foundation complete; scanner architecture is now source-agnostic and parallelized
- Ready to add new sources (Phase 2) — new adapters drop into the existing gather pattern in scan_all_items
- Dashboard cache means adding sources won't slow down the UI

## Self-Check: PASSED

- FOUND: app/services/cache.py
- FOUND: app/services/rate_limit.py
- FOUND: 01-01-SUMMARY.md
- FOUND commit: 231e10e (feat: add cachetools dependency and cache module)
- FOUND commit: 7599eba (feat: add global scan semaphore module)
- FOUND commit: ac15a93 (feat: decouple scan, fix N+1, wire cache, parallelize scheduler)
- FOUND commit: 0043716 (docs: complete plan metadata)

---
*Phase: 01-infrastructure*
*Completed: 2026-04-02*
