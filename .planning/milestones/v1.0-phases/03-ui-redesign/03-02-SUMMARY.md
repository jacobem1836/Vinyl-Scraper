---
phase: 03-ui-redesign
plan: 02
subsystem: ui
tags: [discogs, sqlalchemy, migration, artwork, proxy, streaming, fastapi, svg]

requires:
  - phase: 01-infrastructure
    provides: adapter registry, scan_item, run_migrations pattern, _enrich_item dict

provides:
  - WishlistItem.artwork_url column (nullable, persists Discogs thumb URL)
  - run_migrations() migration guard for artwork_url column
  - Discogs adapter captures thumb URL as _cover_image on first listing per search function
  - scanner.scan_item writes artwork_url to WishlistItem on first successful scan
  - GET /api/artwork proxy endpoint (web_router, no auth) streams Discogs CDN images with Cache-Control
  - _enrich_item dict includes artwork_url for template use
  - WishlistItemResponse.artwork_url Optional[str] (non-breaking schema addition)
  - static/vinyl-placeholder.svg dark vinyl record SVG

affects: [03-03-PLAN, 03-04-PLAN, templates]

tech-stack:
  added: []
  patterns:
    - "_cover_image sentinel key on listing dict for cross-layer metadata passing without interface change"
    - "artwork_url guard: if not item.artwork_url prevents overwriting on subsequent scans"
    - "StreamingResponse with Cache-Control max-age=86400 for proxied CDN images"
    - "web_router.get /api/artwork pattern — no API key for image serving"

key-files:
  created:
    - static/vinyl-placeholder.svg
  modified:
    - app/models.py
    - app/database.py
    - app/services/discogs.py
    - app/services/scanner.py
    - app/routers/wishlist.py
    - app/schemas.py

key-decisions:
  - "_cover_image key on first listing dict avoids changing adapter interface signature (all adapters still return list[dict])"
  - "Use thumb (150px) not cover_image (full-res) from Discogs search results for performance"
  - "Proxy endpoint on web_router (not api_router) — image serving needs no API key"
  - "artwork_url guard (if not item.artwork_url) prevents overwriting on subsequent scans — first-scan-wins"

patterns-established:
  - "Sentinel key pattern: _cover_image on listing dict passed through gather() results, extracted before Listing creation loop"
  - "Migration guard pattern: ALTER TABLE inside try/except — established in database.py run_migrations()"

requirements-completed: [UI-03, UI-06]

duration: 12min
completed: 2026-04-03
---

# Phase 03 Plan 02: Artwork Pipeline Summary

**Discogs thumb URL capture pipeline: artwork_url column + migration, _cover_image sentinel key, scanner write-back, /api/artwork streaming proxy, and vinyl placeholder SVG**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-04-03T00:00:00Z
- **Completed:** 2026-04-03T00:12:00Z
- **Tasks:** 2
- **Files modified:** 6 (+ 1 created)

## Accomplishments

- artwork_url column added to WishlistItem with safe ALTER TABLE migration guard
- Discogs adapter captures thumb URL from first search result via _cover_image sentinel key on listing dict (no interface change)
- scanner.scan_item extracts _cover_image before listing loop and writes to item.artwork_url on first scan
- /api/artwork GET endpoint on web_router streams Discogs CDN images with Cache-Control: public, max-age=86400
- WishlistItemResponse.artwork_url Optional[str] = None added (additive, iOS Shortcut contract unchanged)
- static/vinyl-placeholder.svg dark vinyl record SVG ready for template fallback

## Task Commits

1. **Task 1: Add artwork_url column, migration, and Discogs capture** - `67e2920` (feat)
2. **Task 2: Artwork proxy endpoint, _enrich_item update, schema update, placeholder SVG** - `70a61db` (feat)

## Files Created/Modified

- `app/models.py` - artwork_url = Column(String, nullable=True) after is_active column
- `app/database.py` - migration block adding artwork_url VARCHAR via try/except
- `app/services/discogs.py` - first_thumb captured from results, _cover_image set on first listing in all three search functions
- `app/services/scanner.py` - _cover_image extracted from all_results before listing loop, written to item.artwork_url after last_scanned_at
- `app/routers/wishlist.py` - import httpx + StreamingResponse, artwork_url in _enrich_item, proxy_artwork endpoint on web_router
- `app/schemas.py` - artwork_url: Optional[str] = None added to WishlistItemResponse
- `static/vinyl-placeholder.svg` - dark vinyl record SVG (200x200, #1e293b background, #334155 grooves, #64748b spindle)

## Decisions Made

- Used `thumb` field (150px) not `cover_image` field (full-res) from Discogs search results — reduces proxy bandwidth
- _cover_image sentinel key pattern chosen over changing adapter return type (all adapters still return `list[dict]`) — minimal diff, no interface breakage
- artwork_url guard (`if not item.artwork_url`) ensures first-scan-wins — avoids overwriting once set
- Proxy on web_router (not api_router) — image serving should not require X-API-Key header

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- artwork_url is available on WishlistItem and in _enrich_item dict for all templates
- /api/artwork proxy ready for template use: `<img src="/api/artwork?url={{ item.artwork_url }}">`
- vinyl-placeholder.svg at /static/vinyl-placeholder.svg for fallback: `<img src="/static/vinyl-placeholder.svg">`
- Plan 03-03 (CSS token system + card layout) can now build artwork-forward card grid

---
*Phase: 03-ui-redesign*
*Completed: 2026-04-03*
