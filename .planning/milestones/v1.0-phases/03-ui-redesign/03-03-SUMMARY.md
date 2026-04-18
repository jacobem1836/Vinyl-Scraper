---
phase: 03-ui-redesign
plan: "03"
subsystem: fx-conversion
tags: [fx, currency, aud, listing-enrichment, caching]
dependency_graph:
  requires: [03-02]
  provides: [aud_total, orig_display, fx_rates enrichment pipeline]
  affects: [app/main.py, app/routers/wishlist.py]
tech_stack:
  added: [open.er-api.com free FX API, cachetools TTLCache for FX rates]
  patterns: [pre-resolve async rates at handler level before sync enrichment]
key_files:
  created:
    - app/services/fx.py
  modified:
    - app/main.py
    - app/routers/wishlist.py
decisions:
  - Pre-resolve FX rates at route handler level so _enrich_item stays synchronous (Pitfall 4)
  - TTLCache(maxsize=4, ttl=3600) — 4 slots for potential future currencies, 1-hour TTL
  - AUD pass-through: convert_to_aud returns amount unchanged when currency is AUD
  - None fallback: FX failure returns None; templates must handle missing aud_total gracefully
metrics:
  duration: "~2 minutes"
  completed: "2026-04-03"
  tasks_completed: 2
  files_changed: 3
requirements: [UI-04]
---

# Phase 03 Plan 03: FX Rate Service Summary

FX rate service with TTLCache and async fetch from open.er-api.com, integrated into route handlers so all listing dicts expose aud_total and orig_display for AUD-comparable prices in templates.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create FX service module | e764718 | app/services/fx.py (new) |
| 2 | Integrate FX conversion into listing enrichment | 34e45d3 | app/main.py, app/routers/wishlist.py |

## What Was Built

**app/services/fx.py** — New FX rate service module providing:
- `get_rate(from_currency, to_currency="AUD")` — async, TTL-cached (1 hour), returns None on failure
- `convert_to_aud(amount, currency, rate)` — pure sync, AUD passthrough, None-safe
- `format_orig_display(price, shipping_cost, currency)` — formats "£22.00 + £8.00 shipping" style strings

**app/routers/wishlist.py** changes:
- `_landed(listing, fx_rates=None)` — now converts landed total to AUD if fx_rates provided
- `_enrich_item(item, fx_rates=None)` — accepts fx_rates, passes to all `_landed` calls; `best_price` and `top_listings.landed_price` are AUD-converted when rates available

**app/main.py** changes:
- `index` route: pre-fetches USD/GBP rates before enrichment and caching; FX-converted values stored in cache
- `item_detail` route: pre-fetches rates, listing dicts now include `aud_total` and `orig_display` keys

## Decisions Made

- **Pre-resolve at handler level:** `_enrich_item` stays synchronous; async FX fetch happens once per request in the handler before passing rates down. This avoids the async-in-comprehension pitfall (RESEARCH.md Pitfall 4).
- **TTLCache maxsize=4:** Room for EUR and others if needed later; only USD and GBP actively fetched now.
- **AUD passthrough in convert_to_aud:** `currency == "AUD"` returns amount unchanged so AU store listings (Discrepancy, Bandcamp AU) work correctly without needing a rate.
- **None fallback:** If exchangerate-api.com is unavailable, `get_rate` returns None, `convert_to_aud` returns None, and `_landed` falls back to the raw USD/GBP landed cost. Templates must render gracefully when `aud_total` is None.

## Deviations from Plan

**1. [Rule 2 - Missing Field] Added artwork_url to _enrich_item output**
- Found during: Task 2 code review
- Issue: `_enrich_item` was missing `artwork_url` field added in plan 03-02; templates would need it for the artwork hero UI
- Fix: Added `"artwork_url": item.artwork_url if hasattr(item, "artwork_url") else None` to the returned dict
- Files modified: app/routers/wishlist.py
- Commit: 34e45d3

## Known Stubs

None — all price fields are wired to real data sources. `aud_total` will be None when FX fetch fails (documented fallback, not a stub).

## Self-Check

Files created/modified:
- [x] app/services/fx.py — confirmed exists
- [x] app/main.py — confirmed contains fx_rates, aud_total, orig_display
- [x] app/routers/wishlist.py — confirmed contains fx_rates, convert_to_aud

Commits:
- [x] e764718 — feat(03-03): create FX rate service module
- [x] 34e45d3 — feat(03-03): integrate FX conversion into listing enrichment pipeline

## Self-Check: PASSED
