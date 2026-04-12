---
phase: 07-image-source-priority-scan-log-fix
plan: "01"
subsystem: scraping/scanner
tags: [image-url, adapters, scan-status, store-image-priority]
dependency_graph:
  requires: []
  provides: [Listing.image_url, store-image-priority, scan-status-item-type]
  affects: [app/models.py, app/database.py, app/services/scanner.py, app/services/scan_status.py, app/services/ebay.py, app/services/shopify.py, app/services/discrepancy.py, app/services/juno.py, app/services/bandcamp.py, app/services/clarity.py]
tech_stack:
  added: []
  patterns: [store-image-first priority, nullable adapter field, migration guard]
key_files:
  created: []
  modified:
    - app/models.py
    - app/database.py
    - app/services/ebay.py
    - app/services/shopify.py
    - app/services/discrepancy.py
    - app/services/juno.py
    - app/services/bandcamp.py
    - app/services/clarity.py
    - app/services/scanner.py
    - app/services/scan_status.py
decisions:
  - Store image wins over Discogs _cover_image; artwork_url unchanged when neither source has an image
  - image_url=None is the correct return for adapters that cannot find an image (no error raised)
  - item_type defaults to empty string in item_finished to preserve backward compatibility with direct callers
metrics:
  duration: ~5 minutes
  completed_date: "2026-04-07"
  tasks_completed: 2
  files_modified: 10
requirements: [IMG-01, IMG-02, BUG-02]
---

# Phase 07 Plan 01: Image Source Priority and Scan Log Fix Summary

Store images from all 6 non-Discogs adapters now take priority over the Discogs fallback cover image, and scan log entries include the item type string for correct downstream display labels.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add image_url to Listing model, migration, and all 6 adapters | 11026c4 | app/models.py, app/database.py, app/services/ebay.py, app/services/shopify.py, app/services/discrepancy.py, app/services/juno.py, app/services/bandcamp.py, app/services/clarity.py |
| 2 | Scanner image priority + scan_status type tracking | 3adb751 | app/services/scanner.py, app/services/scan_status.py |

## What Was Built

### Task 1 — image_url column and adapter extraction

- `Listing.image_url` column added (`Column(String, nullable=True)`) to the ORM model
- Migration guard added to `run_migrations()`: `ALTER TABLE listings ADD COLUMN image_url VARCHAR` (silently skipped if column exists)
- All 6 non-Discogs adapters updated to extract product images and include `"image_url"` in their listing dicts:
  - **ebay**: `item.get("image", {}).get("imageUrl")` from Browse API itemSummary
  - **shopify**: `product.get("image")` from suggest.json (URL string)
  - **discrepancy**: `.thumbnail img[src]` with `/`-relative URL resolution to `https://www.discrepancy-records.com.au`
  - **juno**: `.dv-item img[src]` with `//`-relative and `/`-relative URL resolution
  - **bandcamp**: `.art img[src]` inside `.searchresult`
  - **clarity**: `img[src]` inside product card with `//`-relative and `/`-relative URL resolution
- All adapters return `None` for `image_url` when no image element is found — no errors raised

### Task 2 — Scanner priority logic and scan_status fix

- `Listing()` constructor in `scan_item` now passes `image_url=result.get("image_url")`
- Image priority logic replaces simple `if cover_image:` block:
  1. Check `new_listings` for any listing with `image_url` set — use the first one found as `store_image`
  2. If `store_image` found: set `item.artwork_url = store_image`
  3. Else if Discogs `cover_image` found: set `item.artwork_url = cover_image`
  4. Else: leave `item.artwork_url` unchanged (preserves any previously set value)
- `scan_status.item_finished` signature updated: `item_type: str = ""` parameter added
- Log entries now include `"type": item_type` key alongside `query` and `new_listings`
- Scanner calls `item_finished(item.id, item.query, len(new_listings), item.type)` — passes `WishlistItem.type` through

## Decisions Made

- **Store image over Discogs**: Store images from retail product pages are higher quality and more relevant than Discogs thumbnail cover images. Priority: store > Discogs > preserve existing.
- **`None` for missing images**: Adapters that cannot locate an image element return `None` — no sentinel value, no exception. Downstream code guards against `None` via `if listing.image_url:`.
- **`item_type` default `""`**: Preserves backward compatibility with any direct callers of `item_finished` that don't pass the new param.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all adapters wire real extraction logic. Images may be `None` at runtime if the store HTML changes selectors, but the code path is complete.

## Threat Flags

None — image URLs are stored in the DB and proxied server-side via the existing `/api/artwork` proxy. No new network surface introduced. Consistent with T-07-01 and T-07-02 dispositions in the plan threat model.

## Self-Check: PASSED

- `app/models.py` — Listing.image_url column present: confirmed via import test
- `app/database.py` — migration block present: confirmed via grep
- All 6 adapter files contain `"image_url":` key: confirmed via source inspection
- `app/services/scanner.py` — `image_url=result.get("image_url")`, `store_image` block, `item.type)` call: confirmed
- `app/services/scan_status.py` — `item_type: str` param, `"type": item_type` in log: confirmed
- Commits 11026c4 and 3adb751 verified in git log
