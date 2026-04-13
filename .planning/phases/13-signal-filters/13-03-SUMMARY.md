---
phase: 13-signal-filters
plan: "03"
subsystem: scanner+router
tags: [relevance, digital-filter, query-time-filter, observability]
dependency_graph:
  requires: [13-01, 13-02]
  provides: [digital-drop at scan time, relevance_score on Listing rows, query-time relevance filter]
  affects: [app/services/scanner.py, app/routers/wishlist.py]
tech_stack:
  added: []
  patterns: [scan-time-drop, query-time-filter, legacy-passthrough]
key_files:
  created: []
  modified:
    - app/services/scanner.py
    - app/routers/wishlist.py
decisions:
  - "relevance_below counter counts listings below threshold at current threshold — logged even though they are stored (query-time filter, not scan-time drop)"
  - "_passes_relevance passes listings with relevance_score=None (legacy rows scraped before scoring) — prevents blanket hiding of existing data"
  - "Notifiable filter in both scan routes also applies _passes_relevance so sub-threshold listings never trigger email alerts"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-13"
  tasks_completed: 2
  tasks_total: 2
  files_created: 0
  files_modified: 2
---

# Phase 13 Plan 03: Filter Wiring Summary

**One-liner:** Wire digital-drop (FILTER-02) and relevance scoring (FILTER-01) into scanner.scan_item, and apply query-time threshold filtering in all dashboard, detail, and listings API routes.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add digital-drop + relevance-scoring + observability log to scanner.scan_item | 5d89989 | app/services/scanner.py |
| 2 | Apply relevance threshold at query time in dashboard + detail routes | 9874408 | app/routers/wishlist.py |

## What Was Built

**Task 1 — Scanner wiring:**
- Added imports: `is_digital`, `score_listing`, `settings` at the top of `scanner.py`
- Digital-drop loop runs immediately after all adapter results are collected — `is_digital(r)` drops listings before any DB work; counter `digital_dropped` tracks how many were removed
- Relevance scoring: `score_listing(item.query, "", result["title"])` runs per listing before the `existing` dedup check; score stored as `result["_relevance_score"]` and persisted to `Listing.relevance_score`
- Counters `relevance_below` and `location_missing` accumulated during the persistence loop
- Observability log line emitted at end of each `scan_item` call: `[filter] item=<id> kept=N/M (relevance<thr: a, digital: b, location_missing: c)` per D-13

**Task 2 — Router query-time filter:**
- Added `_effective_threshold(item)`: returns `item.relevance_threshold` if set, else `settings.relevance_threshold_default` (D-06)
- Added `_passes_relevance(listing, threshold)`: listings with `relevance_score=None` pass through (legacy rows); otherwise must be `>= threshold` (D-07)
- `_enrich_item`: `all_listings` now filtered by `_passes_relevance` before computing best price, top_listings, and listing_count
- `scan_single_item_web`: notifiable list filtered — new listings below threshold never trigger email
- `scan_all_items_web`: same notifiable filter applied
- `list_item_listings_api`: Python-level filter applied after DB fetch — threshold changes take effect immediately without rescan
- `POST /api/wishlist` (iOS Shortcut contract) untouched

## Acceptance Criteria

- `grep -n "from app.services.digital_filter import is_digital" app/services/scanner.py` — line 11 ✓
- `grep -n "from app.services.relevance import score_listing" app/services/scanner.py` — line 12 ✓
- `grep -n "from app.config import settings" app/services/scanner.py` — line 6 ✓
- `grep -c "is_digital(r)" app/services/scanner.py` = 1 ✓
- `grep -c "relevance_score=" app/services/scanner.py` = 1 ✓
- `grep -n "[filter] item=" app/services/scanner.py` — line 133, contains `relevance<thr`, `digital:`, `location_missing:` ✓
- `grep -c "_effective_threshold" app/routers/wishlist.py` = 5 ✓
- `grep -c "_passes_relevance" app/routers/wishlist.py` = 7 ✓
- `from app.services.scanner import scan_item; from app.routers.wishlist import _effective_threshold, _passes_relevance` — imports OK ✓

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all filter logic is fully wired. Digital listings are dropped at scan time, relevance scores are persisted, and query-time filtering is active on all display routes.

## Threat Flags

None. No new trust boundaries. All inputs flow through the same trusted scanner path; relevance scoring and digital filtering are pure computation on already-trusted data.

## Self-Check: PASSED

- [x] `app/services/scanner.py` modified with digital-drop, scoring, and log line
- [x] `app/routers/wishlist.py` modified with `_effective_threshold`, `_passes_relevance`, and 4 filter sites
- [x] Commit `5d89989` exists
- [x] Commit `9874408` exists
- [x] All imports succeed: `from app.services.scanner import scan_item; from app.routers.wishlist import _effective_threshold, _passes_relevance`
