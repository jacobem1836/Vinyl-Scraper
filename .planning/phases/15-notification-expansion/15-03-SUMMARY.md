---
phase: 15-notification-expansion
plan: "03"
subsystem: notifier-and-scanner
tags: [notifications, price-drop, back-in-stock, cooldown, digest-email, jinja2, tdd]
dependency_graph:
  requires: [15-01, 15-02]
  provides: [_price_dropped, _back_in_stock, _within_cooldown, send_digest_email, digest_alert.html, scanner-prev-snapshot]
  affects: [app/services/scanner.py, app/services/notifier.py, templates/digest_alert.html, app/routers/wishlist.py, app/scheduler.py]
tech_stack:
  added: []
  patterns: [snapshot-before-overwrite, jinja2-email-template, asyncio-to-thread, private-helper-rename]
key_files:
  created:
    - templates/digest_alert.html
  modified:
    - app/services/scanner.py
    - app/services/notifier.py
    - app/routers/wishlist.py
    - app/scheduler.py
decisions:
  - "send_deal_email renamed to _send_deal_email (private) rather than deleted — external callers in scheduler.py and routers/wishlist.py found via grep; Plan 04 will replace those call sites with send_digest_email"
  - "datetime.utcnow() kept consistent with existing project code; deprecation warnings noted but not treated as failures"
  - "digest_alert.html uses namespace() for section presence tracking to avoid Jinja2 scoping issues with variables set inside for loops"
  - "Template uses relative /items/{item.id} URLs — no base_url setting present in config.py"
metrics:
  duration_minutes: 20
  tasks_completed: 2
  tasks_total: 2
  files_modified: 5
  files_created: 1
  completed_date: "2026-04-13"
---

# Phase 15 Plan 03: Detection Helpers + Digest Email Summary

**One-liner:** Scanner prev_ snapshot + price overwrite on re-scan; `_price_dropped`, `_back_in_stock`, `_within_cooldown` helpers and `send_digest_email` added to notifier; three-section `digest_alert.html` CRATE template created; all 9 tests GREEN.

## What Was Built

### Task 1 — Scanner prev_ snapshot + price overwrite (commit: c56c5b7)

Modified the existing-listing branch in `scan_item()` (`app/services/scanner.py`):

**Before:**
```python
if existing:
    new_stock = result.get("is_in_stock")
    if new_stock is not None:
        existing.is_in_stock = new_stock
    continue
```

**After:**
```python
if existing:
    # Snapshot previous state before overwriting (NOTIF-01, NOTIF-02)
    existing.prev_price = existing.price
    existing.prev_is_in_stock = existing.is_in_stock
    # Update current values from scan result
    new_price = result.get("price")
    if new_price is not None:
        existing.price = new_price
    new_stock = result.get("is_in_stock")
    if new_stock is not None:
        existing.is_in_stock = new_stock
    continue
```

This adds two behaviours: (1) prev_ snapshot before any overwrite, enabling delta detection; (2) price update on re-scan (new behaviour — previously scanner only updated stock status).

### Task 2 — Notifier helpers + send_digest_email + digest template (commit: b628f14)

**app/services/notifier.py additions:**

- `_price_dropped(listing, item) -> bool` — checks prev_price vs price against pct or usd threshold per D-05
- `_back_in_stock(listing) -> bool` — guards `prev_is_in_stock is False AND is_in_stock is True` per D-06; None means first scan
- `_within_cooldown(last_notified_at) -> bool` — compares against `settings.notify_cooldown_hours` per D-09; None returns False
- `send_digest_email(digest_items) -> bool` — renders `digest_alert.html`, calls `_send_smtp` via `asyncio.to_thread`; returns False on empty input or missing SMTP credentials

**send_deal_email renamed to `_send_deal_email`** — external callers existed in `app/routers/wishlist.py` (3 call sites) and `app/scheduler.py` (1 call site); all updated to use the private name.

**templates/digest_alert.html:**

Three-section CRATE-style digest email with inline CSS, MSO Outlook conditional block, near-black palette matching `deal_alert.html`:
- Section 1: "New Deals" (green accent, `#34d399`) — renders if any item has `deal_alerts`
- Section 2: "Price Drops" (blue accent, `#60a5fa`) — was/now price columns, strikethrough on old price
- Section 3: "Back in Stock" (amber accent, `#f59e0b`) — listing title, price, source

Each section is guarded by `{% if has_*.value %}` using Jinja2 `namespace()` to work around for-loop scoping.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| 1 — Scanner prev_ snapshot | c56c5b7 | app/services/scanner.py |
| 2 — Notifier helpers + template | b628f14 | app/services/notifier.py, templates/digest_alert.html, app/routers/wishlist.py, app/scheduler.py |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Updated callers of send_deal_email in wishlist.py and scheduler.py**

- **Found during:** Task 2 — grep before rename
- **Issue:** Plan said to delete `send_deal_email` or rename to private. Grep found 4 external callers (3 in wishlist.py, 1 in scheduler.py). Renaming without updating callers would break the app.
- **Fix:** Renamed function to `_send_deal_email` AND updated all 4 call sites to `notifier._send_deal_email`. Plan 04 will replace the scheduler call with `send_digest_email`.
- **Files modified:** app/routers/wishlist.py, app/scheduler.py
- **Commit:** b628f14

## Known Stubs

None. All helpers implement full logic. The template renders real data from digest_items. No placeholder text or hardcoded empty values.

## Threat Flags

None. Template uses Jinja2 autoescape (inherited from `_email_env` autoescape=True), satisfying T-15-04. `send_digest_email` returns early on empty input, satisfying T-15-06.

## Self-Check: PASSED

- [x] app/services/scanner.py: `existing.prev_price = existing.price` present before any price overwrite
- [x] app/services/notifier.py: exports `_price_dropped`, `_back_in_stock`, `_within_cooldown`, `send_digest_email`
- [x] templates/digest_alert.html: exists and renders without Jinja error
- [x] `pytest tests/test_notifier.py -x -q` → 9 passed
- [x] c56c5b7: present in git log
- [x] b628f14: present in git log
