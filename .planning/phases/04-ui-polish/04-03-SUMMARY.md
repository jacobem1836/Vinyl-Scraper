---
phase: 04-ui-polish
plan: 03
subsystem: database
tags: [sqlalchemy, postgresql, sqlite, migrations, scanner]

# Dependency graph
requires:
  - phase: 04-02
    provides: artwork_url column on WishlistItem, Discogs cover image capture
provides:
  - Composite unique constraint (wishlist_item_id, url) on listings table replacing broken global unique(url)
  - Migration to drop old ix_listings_url index and create uq_listing_item_url composite index
  - Scanner always overwrites artwork_url with latest Discogs high-res cover image on every scan
affects: [scanner, database, listings]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "UniqueConstraint in __table_args__ for composite DB constraints"
    - "run_migrations() try/except blocks for idempotent DDL changes"

key-files:
  created: []
  modified:
    - app/models.py
    - app/database.py
    - app/services/scanner.py

key-decisions:
  - "Composite unique (wishlist_item_id, url) — same store URL can appear for multiple wishlist items; scoped per-item deduplication is the correct semantic"
  - "artwork_url always overwritten — ensures thumbnails get replaced by high-res on next scan without manual intervention"

patterns-established:
  - "DB migrations use try/except pass blocks to be idempotent — safe to run on every startup"

requirements-completed: [POLISH-05, POLISH-06]

# Metrics
duration: 10min
completed: 2026-04-04
---

# Phase 04 Plan 03: Gap Closure — Scan Crash and Artwork Overwrite Summary

**Fixed IntegrityError on scan by changing listings unique constraint from global url to composite (wishlist_item_id, url), and removed artwork_url early-exit guard so every scan overwrites with latest Discogs high-res cover**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-04T00:00:00Z
- **Completed:** 2026-04-04T00:10:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Eliminated IntegrityError crash when two wishlist items share the same store listing URL
- Artwork now always updated to latest Discogs cover on every scan, replacing stale thumbnails
- Migration safely drops old global unique index and creates scoped composite index

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix UNIQUE constraint from global to per-item composite** - `26411b0` (fix)
2. **Task 2: Always overwrite artwork_url on scan** - `9236105` (fix)

## Files Created/Modified
- `app/models.py` — Removed `unique=True` from `url` column, added `__table_args__` with `UniqueConstraint("wishlist_item_id", "url", name="uq_listing_item_url")`, imported `UniqueConstraint`
- `app/database.py` — Added migration blocks to drop `ix_listings_url`, drop `uq_listings_url`, create composite `uq_listing_item_url` index
- `app/services/scanner.py` — Removed `if not item.artwork_url:` guard on extraction loop; changed `if cover_image and not item.artwork_url:` to `if cover_image:`

## Decisions Made
- Composite unique (wishlist_item_id, url): same URL can legitimately appear for multiple wishlist items (e.g., a store selling a record matching two different searches). Scoping the constraint per-item is the correct semantic.
- Always overwrite artwork_url: thumbnails stored from early scans should be superseded by the high-res release images Discogs returns. No user benefit to preserving the old value.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- UAT gap items (IntegrityError + low-res artwork) are resolved
- Phase 04 gap closure complete; all UAT must-haves should now pass on next manual verification

---
*Phase: 04-ui-polish*
*Completed: 2026-04-04*
