---
phase: 24-per-item-notification-thresholds
plan: 01
subsystem: notifications, data-model, web-ui
tags: [notifications, per-item-config, nullable-column, migration, jinja2]
dependency_graph:
  requires: []
  provides: [per-item-notify-threshold, global-default-fallback, nullable-notify-column]
  affects: [app/services/notifier.py, app/routers/wishlist.py, templates/item_detail.html]
tech_stack:
  added: []
  patterns: [nullable-with-global-default, form-raw-string-parsing, migration-sqlite-rebuild]
key_files:
  created: []
  modified:
    - app/config.py
    - app/models.py
    - app/schemas.py
    - app/database.py
    - app/services/notifier.py
    - app/routers/wishlist.py
    - templates/item_detail.html
decisions:
  - "Nullable notify_below_pct uses None=global-default pattern instead of storing 20.0 on every row"
  - "Server-side _parse_notify_pct clamps [1,90] and returns None for blank — T-24-01 mitigation"
  - "SQLite migration uses regex to detect NOT NULL on the specific column before rebuilding table"
metrics:
  duration: "15 min"
  completed_date: "2026-04-21"
  tasks_completed: 2
  files_changed: 7
---

# Phase 24 Plan 01: Per-Item Notification Thresholds Summary

Nullable `notify_below_pct` column with `settings.notify_below_pct_default` fallback — each item can override the global 20% threshold or leave it blank to use the default.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Data layer — nullable column, migration, config, schemas | fd330b9 | app/config.py, app/models.py, app/schemas.py, app/database.py |
| 2 | Notifier fallback, router form handling, and item detail UI | eb7456e | app/services/notifier.py, app/routers/wishlist.py, templates/item_detail.html |

## What Was Built

### Data Layer (Task 1)

- **app/config.py**: Added `notify_below_pct_default: float = 20.0` to `Settings` — env-var `NOTIFY_BELOW_PCT_DEFAULT` overrides it
- **app/models.py**: Changed `notify_below_pct` from `nullable=False, default=20.0` to `nullable=True, default=None`
- **app/schemas.py**: `WishlistItemCreate.notify_below_pct` and `WishlistItemResponse.notify_below_pct` both changed to `Optional[float] = None`
- **app/database.py**: Added two migration blocks:
  - PostgreSQL: `ALTER TABLE wishlist_items ALTER COLUMN notify_below_pct DROP NOT NULL` + `DROP DEFAULT`
  - SQLite: Regex checks for NOT NULL on the column in `sqlite_master`, then rebuilds the table with all 11 columns intact

### Service and UI Layer (Task 2)

- **app/services/notifier.py**: `should_notify` resolves `effective_pct = item.notify_below_pct or settings.notify_below_pct_default`; `send_deal_email` uses the same `effective_pct` when rendering the email template
- **app/routers/wishlist.py**:
  - Added `_parse_notify_pct(raw)` helper — parses string to float, clamps to [1, 90], returns None for blank (T-24-01 mitigation)
  - `add_wishlist_item_web` and `edit_wishlist_item_web` accept `notify_below_pct_raw: str = Form("")` and use the helper
  - `_enrich_item` adds `effective_notify_pct` and `is_default_threshold` to the enriched dict
- **templates/item_detail.html**:
  - Threshold display uses `effective_notify_pct` and shows `(default)` when `is_default_threshold` is True
  - Edit button `data-notify-below-pct` uses Jinja conditional to render empty string instead of "None"
  - Form label updated with "leave blank for default" hint; `min="1"` removed from input

## Deviations from Plan

### Auto-added: Server-side range validation (Rule 2 — T-24-01 mitigation)

- **Found during:** Task 2
- **Issue:** Threat model T-24-01 required server-side clamping/rejection of out-of-range values, not just float parsing
- **Fix:** Extracted `_parse_notify_pct` helper that clamps to [1, 90] range before persisting, handling the threat model mitigation in one place
- **Files modified:** app/routers/wishlist.py
- **Commit:** eb7456e

## Known Stubs

None — all functionality is fully wired end-to-end.

## Threat Flags

None — no new security surface beyond what was planned in the threat model.

## Self-Check

- [x] app/config.py — `notify_below_pct_default` present
- [x] app/models.py — `nullable=True, default=None`
- [x] app/schemas.py — `Optional[float] = None` in Create and Response
- [x] app/database.py — PostgreSQL and SQLite migration blocks present
- [x] app/services/notifier.py — `notify_below_pct_default` fallback in both functions
- [x] app/routers/wishlist.py — `_parse_notify_pct`, `effective_notify_pct`, `is_default_threshold` present
- [x] templates/item_detail.html — `(default)` and `leave blank for default` present

## Self-Check: PASSED
