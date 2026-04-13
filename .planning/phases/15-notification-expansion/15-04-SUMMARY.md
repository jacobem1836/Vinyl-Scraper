---
phase: 15-notification-expansion
plan: "04"
subsystem: scheduler-digest-wiring
tags: [scheduler, digest, cooldown, notifications, refactor]
dependency_graph:
  requires: [15-01, 15-02, 15-03]
  provides: [scheduled_scan-collect-then-dispatch, _collect_events, last_notified_at-update]
  affects: [app/scheduler.py]
tech_stack:
  added: []
  patterns: [collect-then-dispatch, asyncio-gather-return-exceptions, cooldown-gate]
key_files:
  created: []
  modified:
    - app/scheduler.py
decisions:
  - "_collect_events() is a local helper inside setup_scheduler() — follows project pattern of defining closures inside setup functions"
  - "last_notified_at commit wrapped in inner try/except per Pitfall 6 — commit failure is logged but does not crash the scheduler"
  - "Cool-down check uses _within_cooldown(item.last_notified_at) directly — handles None internally (returns False)"
  - "send_deal_email removed from scheduler; _send_deal_email (private) remains in notifier.py for wishlist.py deal-alert route"
metrics:
  duration_minutes: 10
  tasks_completed: 1
  tasks_total: 2
  files_modified: 1
  completed_date: "2026-04-13"
---

# Phase 15 Plan 04: Scheduler Digest Wiring Summary

**One-liner:** `scheduled_scan()` refactored from per-item `_send_deal_email` dispatch inside `asyncio.gather` to two-phase collect-then-dispatch with `_collect_events()` helper, cool-down gating, single `send_digest_email()` call, and `last_notified_at` commit.

## What Was Built

### Task 1 — Scheduler refactor (commit: bde25ca)

**app/scheduler.py** — full replacement of `scheduled_scan()` body and import list inside `setup_scheduler()`:

**Imports added:**
```python
from datetime import datetime  # top-level
from app.services.notifier import (
    _back_in_stock, _price_dropped, _within_cooldown,
    send_digest_email, should_notify,
)
```

**`_collect_events(item, new_listings)` local helper:**
- `deal_alerts`: new listings that pass `should_notify()` (preserves existing deal-alert threshold logic)
- `price_drops`: all `item.listings` where `_price_dropped(l, item)` is True — returns `(listing, prev_price, new_price)` tuples
- `back_in_stock`: all `item.listings` where `_back_in_stock(l)` is True
- Returns `None` if all three lists are empty (Pitfall 5 guard)

**`scheduled_scan()` two-phase structure:**
1. Phase 1: `asyncio.gather(*[_scan_one(item) for item in items], return_exceptions=True)` — scan all items concurrently; `_scan_one` now returns new_listings instead of dispatching email
2. Phase 2: iterate `zip(items, results)`, skip `Exception` results (Pitfall 4), gate on `item.notify_email` and `_within_cooldown()` (Pitfall 3), collect events per item
3. `send_digest_email(digest_items)` called exactly once after all items processed — outside the gather
4. On successful send: `last_notified_at = datetime.utcnow()` set on each notified item, committed in inner try/except (Pitfall 6)

## Commits

| Task | Commit | Files |
|------|--------|-------|
| 1 — Scheduler refactor | bde25ca | app/scheduler.py |

## Task 2 — Awaiting Human Verification (checkpoint)

Task 2 is a `checkpoint:human-verify` gate. The automated portion is complete; human must verify the live scan produces a single digest email with correct content and cool-down suppression.

## Deviations from Plan

None — plan executed exactly as written. The `_collect_events()` helper signature matches the plan spec. Cool-down uses `_within_cooldown(item.last_notified_at)` directly (the helper handles None internally, so no extra guard needed — this simplifies vs the RESEARCH.md pattern which added a redundant `if item.last_notified_at and ...` check).

## Known Stubs

None. All logic is fully wired. The digest email function (`send_digest_email`) is implemented in Plan 03 and accepts real ORM objects.

## Threat Flags

None. No new network endpoints, no new user input paths, no auth changes. `last_notified_at` is updated server-side only. Commit failure is logged (T-15-07 mitigation in place).

## Self-Check: PASSED

- [x] app/scheduler.py: `send_digest_email` present in source
- [x] app/scheduler.py: `_within_cooldown` present in source
- [x] app/scheduler.py: `last_notified_at` present in source
- [x] app/scheduler.py: `send_deal_email` NOT present in source
- [x] app/scheduler.py: `isinstance(result, Exception)` present
- [x] app/scheduler.py: `if digest_items:` guard present
- [x] bde25ca: present in git log
- [x] `pytest tests/ -x -q` → 16 passed
