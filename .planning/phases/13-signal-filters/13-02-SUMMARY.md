---
phase: 13-signal-filters
plan: "02"
subsystem: discogs-scraper
tags: [discogs, ships_from, marketplace-api, rate-limiting]
dependency_graph:
  requires: []
  provides: [ships_from populated on all Discogs listings]
  affects: [app/services/discogs.py]
tech_stack:
  added: []
  patterns: [marketplace API enrichment, rate-limit-safe single lookup per release]
key_files:
  created: []
  modified:
    - app/services/discogs.py
decisions:
  - Used /marketplace/search?release_id=&sort=price,asc&per_page=1 (single call per release, cheapest listing)
  - Kept _build_listing unchanged (ships_from=None preserved as contract baseline)
  - Added extra 0.5s sleep before each marketplace fetch to stay under Discogs rate limit
  - No retry logic; None is a valid outcome per D-12
metrics:
  duration: "~10 min"
  completed: "2026-04-13"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
---

# Phase 13 Plan 02: Discogs ships_from Enrichment Summary

**One-liner:** Fetch cheapest Discogs marketplace listing per release via `/marketplace/search` and populate `ships_from` on every newly-scraped Discogs listing dict.

## What Was Built

Added `_fetch_ships_from(client, release_id) -> str | None` helper that calls the Discogs marketplace search API for a given release and returns the seller location from the cheapest listing. Applied this enrichment at all four `_build_listing` call sites: `_get_release_listings`, `_get_album_listings`, `_get_artist_listings`, `_get_label_listings`. Each site adds a 0.5s sleep before the marketplace fetch to preserve the existing rate-limit posture.

## Acceptance Criteria Met

- `_fetch_ships_from` defined as async function: yes
- `grep -c "_fetch_ships_from" app/services/discogs.py` = 5 (1 def + 4 call sites): yes
- `grep -n "marketplace/search"` = exactly 1 line: yes
- `ships_from` key preserved in `_build_listing`: yes
- 4 assignment lines enriching ships_from before append: yes (lines 136, 204, 279, 354)
- No retry loops: yes (`grep -c "retry"` = 0)
- `from app.services import discogs` imports without error: yes

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1    | 6d1083a | feat(13-02): populate ships_from from Discogs marketplace API |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. `ships_from` is now populated from a live API call. Existing DB rows retain their old `None` value and will be updated naturally on the next rescan that produces a new listing row (out of scope per plan).

## Threat Flags

None. No new trust boundary introduced — same Discogs API, same auth header, same client. `release_id` is server-generated (integer), not user-supplied. Response parsing is exception-wrapped.

## Self-Check: PASSED

- `app/services/discogs.py` exists and was modified: confirmed
- Commit `6d1083a` exists: confirmed
