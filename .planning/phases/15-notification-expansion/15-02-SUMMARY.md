---
phase: 15-notification-expansion
plan: "02"
subsystem: tests
tags: [tdd, testing, notifications, red-state]
dependency_graph:
  requires: []
  provides: [tests/test_notifier.py, tests/conftest.py, tests/__init__.py]
  affects: [app/services/notifier.py]
tech_stack:
  added: []
  patterns: [pytest fixtures, SimpleNamespace mocks, AAA test structure]
key_files:
  created:
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_notifier.py
  modified: []
decisions:
  - "Used asyncio.run() instead of pytest-asyncio to avoid adding a new dependency for the two async tests"
  - "Fixtures use SimpleNamespace to avoid SQLAlchemy/DB coupling in unit tests"
  - "Tests intentionally fail (RED state) on _back_in_stock, _price_dropped, _within_cooldown, send_digest_email import"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-13"
  tasks_completed: 2
  files_created: 3
---

# Phase 15 Plan 02: Test Scaffold (RED State) Summary

**One-liner:** 9 failing unit tests for NOTIF-01 through NOTIF-04 targeting `_price_dropped`, `_back_in_stock`, `_within_cooldown`, and `send_digest_email` — confirmed RED via ImportError; Plan 03 turns them GREEN.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Create tests/ package scaffold + shared fixtures | 00797b2 |
| 2 | Write 9 failing unit tests for NOTIF-01 through NOTIF-04 | c834db4 |

## What Was Built

**tests/__init__.py** — empty init enabling pytest package discovery.

**tests/conftest.py** — three shared fixtures:
- `mock_item`: SimpleNamespace with all WishlistItem notification attributes (notify_email, notify_below_pct, notify_drop_mode, notify_drop_pct, notify_drop_usd, last_notified_at, listings)
- `mock_listing`: factory returning SimpleNamespace with price, prev_price, is_in_stock, prev_is_in_stock (all prev_ default to None)
- `settings_override`: monkeypatches `app.config.settings` attributes for test isolation; restores after

**tests/test_notifier.py** — 9 tests covering all NOTIF-* requirements:
- NOTIF-01: `test_back_in_stock`, `test_back_in_stock_first_scan`
- NOTIF-02: `test_price_drop_pct`, `test_price_drop_usd`, `test_price_drop_no_prev`
- NOTIF-03: `test_cooldown_suppresses`, `test_cooldown_expired`
- NOTIF-04: `test_no_digest_on_zero_events`, `test_digest_aggregates`

## RED State Verification

```
ImportError: cannot import name '_back_in_stock' from 'app.services.notifier'
```

Running `pytest tests/test_notifier.py` fails at collection — correct RED state. The failure is on the target function names Plan 03 will implement, not on test infrastructure.

Existing tests in `tests/test_email.py` still collect and pass cleanly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] pytest-asyncio not installed**
- **Found during:** Task 2 — writing async digest tests
- **Issue:** `pytest-asyncio` is not in requirements.txt; `@pytest.mark.asyncio` would fail before ImportError on notifier helpers
- **Fix:** Replaced `async def` test functions with synchronous wrappers using `asyncio.run()`. No new dependency required. Plan 03 can add `pytest-asyncio` if needed for its own tests.
- **Files modified:** tests/test_notifier.py
- **Commit:** c834db4

## Known Stubs

None — this plan creates test infrastructure only. No production code was added.

## Threat Flags

None — tests/ directory contains no secrets; all fixtures use mock data only.

## Self-Check: PASSED

- [x] tests/__init__.py exists (empty)
- [x] tests/conftest.py defines mock_item, mock_listing, settings_override
- [x] tests/test_notifier.py contains exactly 9 test function names from RESEARCH.md
- [x] Collection attempt on `from app.services.notifier import _back_in_stock...` fails with ImportError (RED)
- [x] Commits 00797b2 and c834db4 exist in git log
