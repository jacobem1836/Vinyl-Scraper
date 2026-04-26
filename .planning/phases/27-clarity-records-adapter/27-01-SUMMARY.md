---
phase: 27-clarity-records-adapter
plan: "01"
subsystem: scraping
tags: [scraping, bigcommerce, adapter, html-parsing]
dependency_graph:
  requires: []
  provides: [clarity-records-adapter]
  affects: [scanner, adapter-registry]
tech_stack:
  added: []
  patterns: [BeautifulSoup-html-scraping, asyncio-semaphore, httpx-async]
key_files:
  created:
    - app/services/clarity.py
  modified:
    - app/services/adapter.py
decisions:
  - "BigCommerce /search.php?search_query={query} endpoint — page 1 only (D-01, D-02)"
  - "source=clarity, currency=AUD, ships_from=Australia — AU store identity (D-03)"
  - "Include sold-out listings with is_in_stock=False — UI already handles opacity/badge (D-04)"
  - "Selectors: li.product with card-title a, .price--withoutTax, sold-out class/text detection"
metrics:
  duration: "~10 min"
  completed: "2026-04-26"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 1
---

# Phase 27 Plan 01: Clarity Records Adapter Summary

**One-liner:** BigCommerce HTML scraper for clarityrecords.com.au returning AUD-priced listings with stock detection via juno.py pattern.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create Clarity Records BigCommerce HTML adapter | 22554be | app/services/clarity.py (created, 131 lines) |
| 2 | Register clarity adapter in ADAPTER_REGISTRY | 787a71b | app/services/adapter.py (import + registry entry) |

## What Was Built

`app/services/clarity.py` — a new scraping adapter for Clarity Records, an Australian vinyl store running on BigCommerce. The adapter:

- GETs `https://clarityrecords.com.au/search.php?search_query={query}` (BigCommerce standard search endpoint)
- Parses HTML with BeautifulSoup + lxml using BigCommerce Stencil selectors (`li.product`, `.card-title a`, `.price--withoutTax`, `.card-out-of-stock`)
- Handles 403/404 gracefully (log + return `[]`)
- Rate-limits with `asyncio.Semaphore(1)` + 2s sleep after request
- Returns up to 10 `ListingDict` entries with `source="clarity"`, `currency="AUD"`, `ships_from="Australia"`, parsed `is_in_stock` (both in-stock and sold-out included)
- Logs under `[Clarity]` prefix

`app/services/adapter.py` — updated to import `clarity` and add it as the 7th enabled entry in `ADAPTER_REGISTRY`. The scanner dispatches to it automatically on the next scan cycle.

## Decisions Made

1. **No pagination** (D-02): Page 1 only. For targeted artist/album queries this is sufficient; the BigCommerce search is relevance-ordered.
2. **Stock handling** (D-04): Both sold-out and in-stock listings returned. `is_in_stock=False` triggers existing UI opacity/badge — no template changes needed.
3. **Selectors at Claude's discretion**: Used `li.product` + `.card-title a` (Stencil default) with fallback to `article.card` for non-standard themes. Price via `.price--withoutTax` or `.price--main`.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. The adapter returns real scraped data; all ListingDict fields are populated from parsed HTML or set to documented defaults (`condition=None`, `seller=None`).

## Threat Flags

No new network surface introduced beyond what other adapters already establish. `clarity.py` follows the same outbound-only httpx GET pattern as `juno.py` and `bandcamp.py`.

## Self-Check

Verifying files and commits exist.
