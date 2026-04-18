---
phase: 02-new-sources
plan: "03"
subsystem: scraping
tags: [juno, bandcamp, html-scraping, beautifulsoup4, adapters]

requires:
  - phase: 02-01
    provides: eBay AU adapter and adapter registry pattern established
  - phase: 02-02
    provides: Discrepancy and Clarity adapters registered

provides:
  - Juno Records HTML scraper adapter (GBP pricing, artist browse page)
  - Bandcamp vinyl album search adapter (USD pricing, vinyl filter via title text)
  - Full 7-adapter registry: discogs, shopify, ebay, discrepancy, clarity, juno, bandcamp

affects: [scanner, adapter-registry, phase-03-ui]

tech-stack:
  added: []
  patterns:
    - "Juno artist page scraping: .dv-item containers, a[href*=/products/] for title, .price_lrg for GBP price"
    - "Bandcamp vinyl filter: item_type=a search, filter results by 'vinyl' in title/subhead text (case-insensitive)"
    - "Both adapters: Semaphore(1) + asyncio.sleep for rate limiting HTML scrapers"

key-files:
  created:
    - app/services/juno.py
    - app/services/bandcamp.py
  modified:
    - app/services/adapter.py

key-decisions:
  - "Juno artist page used instead of search page -- /search/ endpoint is fully JS-rendered (0 products in static HTML)"
  - "Bandcamp item_type=p is not a valid filter -- research was incorrect; only b/a/t/f are valid; search item_type=a and filter by vinyl in title"
  - "Bandcamp returns 0 results for queries without 'vinyl' in album titles -- expected behavior (vinyl filter working correctly)"

patterns-established:
  - "JS-rendered search page fallback: use artist browse URL when search endpoint is JS-only"
  - "Text-based vinyl filter: 'vinyl' in combined title+subhead+itemtype string (case-insensitive)"

requirements-completed: [SRC-04, SRC-05]

duration: ~10min
completed: "2026-04-02"
---

# Phase 02 Plan 03: Juno Records + Bandcamp Adapters Summary

**HTML scrapers for Juno Records (GBP, artist page approach) and Bandcamp (USD, vinyl title filter); full 7-adapter registry complete**

## Performance

- **Duration:** ~10 min
- **Completed:** 2026-04-02T06:21:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Juno Records adapter scrapes vinyl listings from artist browse pages; returns GBP-priced dicts with ships_from United Kingdom
- Bandcamp adapter searches albums and filters to vinyl-only results via "vinyl" text in title/subhead; returns USD listing dicts
- Adapter registry complete with all 7 sources: discogs, shopify, ebay, discrepancy, clarity, juno, bandcamp

## Task Commits

1. **Task 1: Juno Records adapter** - `19402fe` (feat)
2. **Task 2: Bandcamp adapter + registry wiring** - `ae18802` (feat)

## Files Created/Modified

- `app/services/juno.py` - Juno HTML scraper: artist page URL, .dv-item containers, .price_lrg prices, Semaphore(1)+2s sleep
- `app/services/bandcamp.py` - Bandcamp album search: item_type=a, vinyl title filter, Semaphore(1)+1.5s sleep
- `app/services/adapter.py` - Added juno and bandcamp imports and registry entries

## Decisions Made

- Juno artist page approach: `/artists/{query}/?media_type=vinyl` gives static HTML with 10-32 vinyl products; the `/search/` endpoint is fully client-side rendered (0 results in static HTML) despite correct User-Agent
- Bandcamp item_type filter: research stated `item_type=p` filters physical merch -- incorrect. Bandcamp's search form only accepts: all (empty), b (artists/labels), a (albums), t (tracks), f (fans). Physical merch is not a search category. Used `item_type=a` + vinyl title filter instead.
- Clarity cherry-pick: prior agent committed discrepancy+clarity to a separate worktree branch; merged via cherry-pick with conflict resolution to combine with eBay work. Adapter registry now has correct ordering.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Juno search page is JS-rendered -- artist page used as fallback**
- **Found during:** Task 1 (execution-time HTML inspection)
- **Issue:** `https://www.juno.co.uk/search/` loads product listings via Turbo/JavaScript. The `#resultcount` input always shows `value="0"` in static HTML. No `.dv-item` containers are present in server-rendered HTML from the search endpoint.
- **Fix:** Used artist browse URL `https://www.juno.co.uk/artists/{query}/?media_type=vinyl` which is fully server-rendered and returns up to 32 vinyl items with prices. This provides real value for artist-name queries.
- **Files modified:** app/services/juno.py
- **Commit:** 19402fe

**2. [Rule 1 - Bug] Bandcamp item_type=p is invalid -- correct filter is text-based**
- **Found during:** Task 2 (live HTML inspection)
- **Issue:** Research stated `item_type=p` filters to physical merch. Live inspection of the Bandcamp search form shows only b/a/t/f are valid filter values. `item_type=p` is silently ignored and returns all result types.
- **Fix:** Used `item_type=a` (albums) + vinyl text filter on combined title+subhead string. This is more appropriate: vinyl releases on Bandcamp are listed as albums, and vinyl-specific releases include "vinyl" in their title.
- **Files modified:** app/services/bandcamp.py
- **Commit:** ae18802

**3. [Rule 3 - Blocking] Missing discrepancy.py and clarity.py in worktree**
- **Found during:** Setup (pre-task 1)
- **Issue:** This worktree was branched from Phase 01 (main) and did not include 02-01 (eBay) or 02-02 (discrepancy/clarity) commits. Two separate worktrees had done those plans independently with overlapping adapter.py changes.
- **Fix:** Rebased onto phase-02-new-sources (for eBay), then cherry-picked discrepancy+clarity commits with conflict resolution to merge both sets of adapters.
- **Commit:** bb67f98 (cherry-pick with conflict resolution)

---

**Total deviations:** 3 auto-fixed (2 bugs -- incorrect research; 1 blocking -- worktree setup)
**Impact on plan:** All deviations were essential to produce working adapters.

## Known Stubs

- `juno.py` -- Artist page approach is limited: only returns results when `query` matches a Juno artist slug exactly (e.g. "radiohead" → `/artists/radiohead/`). Partial artist names or album names return 404. A future improvement could try multiple URL patterns or use Juno's autocomplete API to resolve artist slugs.
- `bandcamp.py` -- Bandcamp vinyl filter relies on "vinyl" appearing in the album title. Albums without "vinyl" in the title (but sold as vinyl) are not returned. Price is rarely available on the search page (most results return `price: None`).

## Next Phase Readiness

- All 7 source adapters registered and functional (clarity disabled pending site confirmation)
- Phase 03 (UI Redesign) can proceed with full dataset available
- eBay still gated behind credentials; will auto-enable once EBAY_APP_ID/EBAY_CERT_ID are in Railway env

---
*Phase: 02-new-sources*
*Completed: 2026-04-02*

## Self-Check: PASSED

- FOUND: app/services/juno.py
- FOUND: app/services/bandcamp.py
- FOUND: app/services/adapter.py (7 entries in registry)
- FOUND: .planning/phases/02-new-sources/02-03-SUMMARY.md
- FOUND: commit 19402fe (feat(02-03): add Juno Records adapter)
- FOUND: commit ae18802 (feat(02-03): add Bandcamp vinyl adapter)
