---
phase: 15-notification-expansion
plan: "01"
subsystem: schema-and-config
tags: [schema, migrations, orm, config, notifications]
dependency_graph:
  requires: []
  provides: [prev_price, prev_is_in_stock, last_notified_at, notify_drop_mode, notify_drop_pct, notify_drop_usd, notify_drop_pct_default, notify_drop_usd_default, notify_cooldown_hours]
  affects: [app/database.py, app/models.py, app/config.py]
tech_stack:
  added: []
  patterns: [manual-sql-migration, sqlalchemy-declarative-columns, pydantic-settings]
key_files:
  created: []
  modified:
    - app/database.py
    - app/models.py
    - app/config.py
decisions:
  - "prev_is_in_stock uses INTEGER (not BOOLEAN) in migration SQL to match SQLite storage; ORM Column uses Boolean which SQLAlchemy maps correctly"
  - "Six migrations added after existing relevance_score/relevance_threshold blocks, preserving all prior migrations"
  - "notify_drop_mode defaults to 'pct' consistent with D-02; VARCHAR NOT NULL DEFAULT 'pct' in SQL"
  - "New config fields placed after relevance_threshold_default in the Settings class, grouped with other notification-related settings"
metrics:
  duration_minutes: 15
  tasks_completed: 2
  tasks_total: 2
  files_modified: 3
  completed_date: "2026-04-13"
---

# Phase 15 Plan 01: Schema + Config Foundation Summary

**One-liner:** Six idempotent ALTER TABLE migrations and ORM column declarations for prev_price, prev_is_in_stock, last_notified_at, notify_drop_mode, notify_drop_pct, notify_drop_usd across Listing and WishlistItem, plus three pydantic-settings fields for global notification thresholds.

## What Was Built

### Task 1 — Schema migrations + ORM columns (commits: e17b96c)

Added six ALTER TABLE blocks to `run_migrations()` in `app/database.py`, each in an independent try/except block following the established project migration pattern:

**On `listings` table:**
- `prev_price FLOAT` (nullable) — price captured before overwriting on re-scan
- `prev_is_in_stock INTEGER` (nullable, no DEFAULT) — stock status captured before overwriting; NULL means not yet observed

**On `wishlist_items` table:**
- `last_notified_at DATETIME` (nullable) — timestamp of most recent digest email for cool-down enforcement
- `notify_drop_mode VARCHAR NOT NULL DEFAULT 'pct'` — "pct" or "usd" price-drop trigger mode
- `notify_drop_pct FLOAT` (nullable) — per-item percentage threshold override
- `notify_drop_usd FLOAT` (nullable) — per-item dollar threshold override

Added matching SQLAlchemy ORM column declarations on `Listing` and `WishlistItem`.

### Task 2 — Config settings (commit: 057d147)

Added three new fields to `Settings(BaseSettings)` in `app/config.py`:

```python
notify_drop_pct_default: float = 20.0
notify_drop_usd_default: float = 5.0
notify_cooldown_hours: int = 24
```

All three are env-overridable via pydantic-settings convention (`NOTIFY_DROP_PCT_DEFAULT`, `NOTIFY_DROP_USD_DEFAULT`, `NOTIFY_COOLDOWN_HOURS`).

## Commits

| Task | Commit | Files |
|------|--------|-------|
| 1 — Schema migrations + ORM columns | e17b96c | app/database.py, app/models.py |
| 2 — Config settings | 057d147 | app/config.py |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Worktree working tree was at older commit than HEAD**

- **Found during:** Setup before Task 1
- **Issue:** The worktree was created at commit `5b1de12` (pre-phase-15), but the plan expected execution from `007d06d`. The working tree files for `app/database.py`, `app/models.py`, and `app/config.py` were all at the older state — missing `relevance_score`, `relevance_threshold`, and `relevance_threshold_default` from Phase 13.
- **Fix:** Restored each file from `git checkout HEAD -- <file>` before applying plan edits, ensuring additions landed on top of the correct Phase 13 baseline. First commit attempt was reverted via `git reset HEAD~1` after detecting it had included unintended file deletions.
- **Files modified:** No extra files — only the plan's intended three files.
- **Commit:** N/A (corrective action; final commits e17b96c and 057d147 are clean)

## Verification

All three checks passed:

```
run_migrations() — idempotent (ran twice, no error)
Listing.prev_price, Listing.prev_is_in_stock — ORM columns present
WishlistItem.last_notified_at, WishlistItem.notify_drop_mode, WishlistItem.notify_drop_pct, WishlistItem.notify_drop_usd — ORM columns present
settings.notify_drop_pct_default == 20.0 — OK
settings.notify_drop_usd_default == 5.0 — OK
settings.notify_cooldown_hours == 24 — OK
```

## Known Stubs

None. This plan adds pure schema + config with no UI rendering or data flow.

## Threat Flags

None. No new user-input surfaces, no new network endpoints, no auth changes. Settings fields are non-sensitive numeric thresholds consistent with T-15-01 and T-15-02 in the plan's threat model.

## Self-Check: PASSED

- app/database.py: confirmed modified (6 new migration blocks appended)
- app/models.py: confirmed modified (prev_price, prev_is_in_stock on Listing; 4 columns on WishlistItem)
- app/config.py: confirmed modified (3 new settings fields)
- e17b96c: present in git log
- 057d147: present in git log
