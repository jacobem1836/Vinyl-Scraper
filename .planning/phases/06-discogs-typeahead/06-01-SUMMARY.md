---
phase: 06-discogs-typeahead
plan: "01"
subsystem: backend
tags: [discogs, typeahead, api, schema, migration]
dependency_graph:
  requires: []
  provides: [discogs_release_id column, GET /api/discogs/search endpoint, pinned-release scanner path]
  affects: [app/models.py, app/schemas.py, app/database.py, app/services/discogs.py, app/routers/wishlist.py, app/services/scanner.py]
tech_stack:
  added: []
  patterns: [nullable FK column via ALTER TABLE migration, typeahead 1-call search, pinned-release scanner path]
key_files:
  created: []
  modified:
    - app/models.py
    - app/schemas.py
    - app/database.py
    - app/services/discogs.py
    - app/routers/wishlist.py
    - app/services/scanner.py
decisions:
  - typeahead_search makes exactly 1 Discogs API call (no detail fetches) to stay well under 60 req/min
  - scanner conditionally passes discogs_release_id only to discogs adapter by name check (cleaner than **kwargs on all adapters)
  - typeahead endpoint on web_router (no API key) — public Discogs catalog data, no auth needed for single-user tool
  - _get_release_listings returns single listing dict; cover image attached as _cover_image key following existing pattern
metrics:
  duration_minutes: 15
  completed_date: "2026-04-07"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 6
---

# Phase 06 Plan 01: Discogs Typeahead Backend Infrastructure Summary

**One-liner:** Discogs typeahead backend with `discogs_release_id` column, `GET /api/discogs/search` returning 5-result release matches in one API call, and pinned-release scanner path that bypasses text search.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Add discogs_release_id to model, schemas, migration, handlers | d73d290 | app/models.py, app/schemas.py, app/database.py, app/routers/wishlist.py |
| 2 | Typeahead search endpoint and pinned-release scanner logic | 6b4e4e9 | app/services/discogs.py, app/services/scanner.py, app/routers/wishlist.py |

## What Was Built

**Task 1 — Data layer:**
- `discogs_release_id = Column(Integer, nullable=True)` added to `WishlistItem` after `artwork_url`
- `Optional[int] = None` added to `WishlistItemCreate`, `WishlistItemUpdate`, `WishlistItemResponse` — iOS Shortcut API preserved (field absent = None)
- `run_migrations()` extended with `ALTER TABLE wishlist_items ADD COLUMN discogs_release_id INTEGER`
- Web add/edit form handlers accept `discogs_release_id: int | None = Form(None)`
- API create handler passes `payload.discogs_release_id` to `WishlistItem` constructor
- `_enrich_item` includes `"discogs_release_id": item.discogs_release_id` in output dict

**Task 2 — Search and scanner:**
- `typeahead_search(query, max_results=5)` — single `GET /database/search` call, parses "Artist - Title" format, returns `[{release_id, title, artist, year, thumb}]`
- `_get_release_listings(release_id)` — fetches `GET /releases/{id}`, returns listing via `_build_listing()` with cover image if available
- `search_and_get_listings()` updated with `discogs_release_id: int | None = None` param; routes to `_get_release_listings` for album/subject types when set
- `scanner.scan_item()` builds coroutine list manually, passing `discogs_release_id=item.discogs_release_id` only to the discogs adapter by name
- `GET /api/discogs/search?q=...` endpoint on `web_router` (no API key); returns `[]` for queries under 2 chars, caps at 5 results

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. The typeahead endpoint returns real Discogs API data. The `discogs_release_id` column is wired end-to-end (model → schema → migration → form handlers → scanner). Plan 02 will add the frontend modal/JS that calls this endpoint.

## Threat Flags

No new threat surface beyond what was documented in the plan's threat model. The `/api/discogs/search` endpoint is intentionally unauthenticated (T-06-04: accepted). Query injection is not possible (T-06-01: httpx URL-encodes params automatically, 2-char minimum enforced).

## Self-Check: PASSED

- [x] app/models.py — discogs_release_id column present
- [x] app/schemas.py — field in Create, Update, Response
- [x] app/database.py — migration block added
- [x] app/services/discogs.py — typeahead_search, _get_release_listings, updated search_and_get_listings
- [x] app/routers/wishlist.py — GET /api/discogs/search endpoint, updated handlers, _enrich_item
- [x] app/services/scanner.py — conditional discogs_release_id kwarg passing
- [x] Commit d73d290 exists (Task 1)
- [x] Commit 6b4e4e9 exists (Task 2)
