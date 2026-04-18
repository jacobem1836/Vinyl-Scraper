---
phase: 01-infrastructure
plan: "03"
subsystem: ui
tags: [jinja2, javascript, css, polling, fastapi]

# Dependency graph
requires:
  - phase: 01-infrastructure
    provides: Scan decoupling — items appear on dashboard before scan completes (Plan 01)

provides:
  - GET /wishlist/{item_id}/status endpoint returning has_listings, listing_count, last_scanned_at
  - CSS-only scanning spinner on cards with listing_count == 0 and no last_scanned_at
  - JS polling loop that auto-reloads dashboard when listings appear (5s interval, 2min timeout)

affects: [02-new-sources, 03-ui-redesign]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Status endpoint on web_router (no API key) for dashboard JS polling"
    - "data-scanning/data-item-id attributes on Jinja2 cards for JS targeting"
    - "setInterval polling with wall-clock timeout guard (clearInterval after 2min)"

key-files:
  created: []
  modified:
    - app/routers/wishlist.py
    - templates/index.html
    - static/style.css

key-decisions:
  - "Status endpoint on web_router (not api_router) — no API key needed for dashboard JS"
  - "Reload full page on listing arrival — simpler than partial DOM replacement, acceptable UX"
  - "2-minute polling timeout — scan should complete well within this window; avoids infinite requests"

patterns-established:
  - "Scanning state derived from template: listing_count == 0 and last_scanned_at is None — no extra backend field needed"

requirements-completed: [PERF-01]

# Metrics
duration: 2min
completed: 2026-04-02
---

# Phase 1 Plan 3: Frontend Polling UX Summary

**CSS spinner + JS polling on dashboard cards auto-refreshes when background scan produces listings, completing the PERF-01 scan-decoupling UX loop**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-02T04:37:59Z
- **Completed:** 2026-04-02T04:39:06Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added `GET /wishlist/{item_id}/status` lightweight count endpoint for polling
- Dashboard cards in scanning state show pulsing border + CSS spinner (no image assets)
- JavaScript polls every 5 seconds and reloads page when `has_listings` becomes true; stops after 2 minutes

## Task Commits

Each task was committed atomically:

1. **Task 1: Add scanning status API endpoint** - `5d732bb` (feat)
2. **Task 2: Add scanning spinner and polling JS to dashboard** - `652e551` (feat)

## Files Created/Modified

- `app/routers/wishlist.py` - Added `GET /wishlist/{item_id}/status` route on web_router
- `templates/index.html` - Added data-scanning/data-item-id attributes, spinner element, polling JS
- `static/style.css` - Added `.card--scanning` pulsing border and `.spinner` keyframes

## Decisions Made

- Status endpoint placed on `web_router` (not `api_router`) so no API key header is needed for dashboard JS polling
- Full page reload on listing arrival chosen over partial DOM replacement — simpler, no risk of stale state
- 2-minute polling timeout stops runaway intervals if a scan stalls

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 1-03 completes all three Phase 1 infrastructure plans
- Phase 1 is ready for transition to Phase 2 (New Sources) or Phase 3 (UI Redesign)
- No blockers

---
*Phase: 01-infrastructure*
*Completed: 2026-04-02*
