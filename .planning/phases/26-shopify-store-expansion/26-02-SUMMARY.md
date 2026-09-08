---
phase: 26-shopify-store-expansion
plan: "02"
subsystem: shopify-adapter
tags: [shopify, scraping, sources, heartland]
dependency_graph:
  requires: [26-01]
  provides: [SRC-12]
  affects: [app/services/shopify.py]
tech_stack:
  added: []
  patterns: [products_json-fallback, search_type-dispatch, client-side-substring-filter]
key_files:
  modified: [app/services/shopify.py]
  created: []
decisions:
  - "Used products.json with limit=250 + client-side substring filter for Heartland — suggest.json endpoint is disabled on their Shopify store"
  - "_search_store left byte-identical to pre-plan state; only _dispatch wrapper added in search_and_get_listings"
  - "search_type field on STORES entry used as routing flag — only heartland has it, keeping all 11 others unchanged"
metrics:
  duration_seconds: 131
  completed_date: "2026-04-26"
  tasks_completed: 3
  files_modified: 1
---

# Phase 26 Plan 02: Heartland Records via products.json Summary

Heartland Records added as the 12th store using a separate `_search_store_products_json` code path. Heartland's suggest.json endpoint is disabled; we use Shopify's public `/products.json?limit=250` and filter client-side by substring match on title.

## What Was Built

- **Heartland entry in STORES** with `search_type: "products_json"` — the only store with this field
- **`_search_store_products_json` function** — fetches all products via `/products.json?limit=250`, filters by `query.lower() in title.lower()`, caps at `max_results`, returns same dict shape as `_search_store`
- **Routing in `search_and_get_listings`** — `_dispatch` inner function routes stores with `search_type == "products_json"` to new path; all others still hit `_search_store` unchanged

## Heartland Details

- **Base URL:** `https://heartlandrecords.com.au`
- **Endpoint verified:** `https://heartlandrecords.com.au/products.json?limit=250` — HTTP 200, 250 products returned

## Live Scan Results

**Test query used:** `"Tough Town"` (first 2 words of first product: "Tough Town - Col Vinyl LP")

| Store | Listings returned |
|-------|-------------------|
| heartland | 1 |

**Generic smoke test query:** `"radiohead"`

| Store | Listings returned |
|-------|-------------------|
| thevinylstore | 5 |
| dutchvinyl | 5 |
| strangeworld | 5 |
| goldmine | 5 |
| utopia | 5 |
| red_eye | 5 |
| rockaway | 5 |
| happy_valley | 5 |
| rare_records | 5 |
| wax_museum | 3 |

No `[Shopify] Error` or `[Shopify] Unexpected error` lines from any store.

## Heartland Listing Shape Verification

All required keys present: `source`, `title`, `price` (float), `currency` ("AUD"), `ships_from` ("Australia"), `url`, `condition` (None), `is_in_stock`, `seller` (None), `image_url`.

## _search_store Unchanged Confirmation

`_search_store` body is byte-identical to pre-plan state. Only change to `search_and_get_listings` is replacing the direct `asyncio.gather` call with a `_dispatch` inner function that routes by `search_type`. Zero regressions.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- `app/services/shopify.py` exists and imports cleanly
- Commit `3d615f2` verified in git log
- STORES count: 12 (11 suggest.json + 1 products.json)
- Only heartland has `search_type` field
- `_search_store_products_json` exists and is a coroutine function
- `_search_store` signature unchanged: `[client, store, query, max_results]`
