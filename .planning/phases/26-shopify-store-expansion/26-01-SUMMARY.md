---
phase: 26-shopify-store-expansion
plan: "01"
subsystem: shopify-scraper
tags: [shopify, stores, expansion, scraping]
dependency_graph:
  requires: []
  provides: [wax_museum, red_eye, rockaway, happy_valley, rare_records store entries]
  affects: [app/services/shopify.py, search_and_get_listings fan-out]
tech_stack:
  added: []
  patterns: [STORES list expansion, suggest.json path reuse]
key_files:
  created: []
  modified:
    - app/services/shopify.py
decisions:
  - "Used https://rockaway.com.au (not www.rockawayrecords.com.au which redirects there)"
  - "Used https://happyvalleyshop.com (not www.happyvalleyshop.com.au which redirects there)"
metrics:
  duration: "~2 minutes"
  completed: "2026-04-26T02:41:41Z"
  tasks_completed: 3
  files_modified: 1
---

# Phase 26 Plan 01: Shopify Store Expansion (Standard Stores) Summary

**One-liner:** Added 5 Australian vinyl record stores (Wax Museum, Red Eye, Rockaway, Happy Valley, Rare Records) to the Shopify STORES list, expanding scan coverage from 6 to 11 stores without any code changes beyond data.

## What Was Built

STORES list in `app/services/shopify.py` expanded from 6 to 11 entries. All 5 new stores use the existing `_search_store` suggest.json path with no code modifications needed.

## Task Results

### Task 1: Verify suggest.json availability

All 5 candidate stores verified as live Shopify storefronts:

| Store | Tested URL | HTTP | Products |
|---|---|---|---|
| Wax Museum Records | https://waxmuseumrecords.com.au | 200 | YES |
| Red Eye Records | https://www.redeye.com.au | 200 | YES |
| Rockaway Records | https://rockaway.com.au | 200 | YES |
| Happy Valley Shop | https://happyvalleyshop.com | 200 | YES |
| Rare Records | https://www.rarerecords.com.au | 200 | YES |

**Base URL corrections vs CONTEXT.md candidates:**
- Rockaway: CONTEXT.md listed `https://www.rockawayrecords.com.au` — this returns HTTP 301 redirecting to `https://rockaway.com.au`. Used `https://rockaway.com.au`.
- Happy Valley: CONTEXT.md listed `https://www.happyvalleyshop.com.au` — this returns HTTP 000 (connection failure). The actual site is `https://happyvalleyshop.com` (non-.au). Used `https://happyvalleyshop.com`.

### Task 2: Add 5 new entries to STORES list

File `app/services/shopify.py` edited. All 5 entries appended after `umusic` with exactly 3 keys each (`key`, `name`, `base_url`). No `search_type` field. Verification passed:

```
python3 -c "from app.services.shopify import STORES; ..." → OK
grep -c '"key":' app/services/shopify.py → 11
```

### Task 3: Live integration smoke test

Query: `"radiohead in rainbows"` — all 5 new stores returned results:

```
wax_museum: 1 listings
red_eye: 2 listings
rockaway: 1 listings
happy_valley: 1 listings
rare_records: 5 listings
TOTAL across all stores: 17
```

No `[Shopify] Error` lines. All stores reachable and functioning correctly.

## Decisions Made

1. **Used https://rockaway.com.au** — the `.rockawayrecords.com.au` domain redirects here; using the direct URL avoids an unnecessary redirect on every scan.
2. **Used https://happyvalleyshop.com** — the `.com.au` domain connection-fails; the store is hosted under `.com` instead of `.com.au`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected Rockaway Records base URL**
- **Found during:** Task 1 verification
- **Issue:** `https://www.rockawayrecords.com.au` returned HTTP 301 (redirect to `https://rockaway.com.au`)
- **Fix:** Used `https://rockaway.com.au` directly in STORES entry
- **Files modified:** app/services/shopify.py

**2. [Rule 1 - Bug] Corrected Happy Valley Shop base URL**
- **Found during:** Task 1 verification
- **Issue:** `https://www.happyvalleyshop.com.au` returned HTTP 000 (connection failure). `www.happyvalleyshop.com.au` follows HTTP redirect to `https://happyvalleyshop.com`
- **Fix:** Used `https://happyvalleyshop.com` directly in STORES entry
- **Files modified:** app/services/shopify.py

## Commits

- `b6e3355`: feat(26-01): expand STORES list from 6 to 11 entries

## Known Stubs

None — all 5 new stores were verified live with real results.

## Self-Check: PASSED

- app/services/shopify.py: modified with 11 STORES entries
- Commit b6e3355 exists
- Live smoke test: 5/5 new stores returned listings
