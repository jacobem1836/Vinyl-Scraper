# Phase 24: Per-Item Notification Thresholds - Context

**Gathered:** 2026-04-21 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Each wishlist item can have its own notification threshold (% below typical price), overriding the global default. Items without a custom threshold continue using the global default. The global default itself is not configurable from the web UI — only per-item overrides are.

Requirements: NOTIF-05, NOTIF-06

</domain>

<decisions>
## Implementation Decisions

### Data Model
- **D-01:** Make `notify_below_pct` on `WishlistItem` nullable (`nullable=True`). Existing items keep their current value (20.0 stays as an explicit custom threshold; not reset to NULL). The column was added as `NOT NULL DEFAULT 20.0` in a prior migration.
- **D-02:** DB migration: use an `ALTER TABLE` approach for PostgreSQL (`DROP NOT NULL`); for SQLite, use the existing create-copy-rename pattern if needed. Both are already used in `app/database.py`.
- **D-03:** `WishlistItemResponse` schema (`app/schemas.py:50`) must change `notify_below_pct: float` → `Optional[float]` to avoid serialization errors when the DB has NULLs. The `WishlistItemUpdate` schema already has `Optional[float] = None` at line 19.

### Global Default
- **D-04:** Global default stored in `Settings` (env var `NOTIFY_BELOW_PCT_DEFAULT`, default `20.0`). No web UI to configure the global default — it's an operator config like other settings in `app/config.py`. New items added without an explicit threshold get `None` in the DB (resolved to the global default at runtime).

### Notification Logic
- **D-05:** `notifier.should_notify()` and the email body builder use: `item.notify_below_pct if item.notify_below_pct is not None else settings.notify_below_pct_default`. Fallback logic lives in the notifier service, not the router, so the scheduler path also benefits.
- **D-06:** `notifier.py:127` currently formats `item.notify_below_pct` for the email body — must use the resolved effective value, not the raw nullable field.

### Edit Form & Item Detail
- **D-07:** The threshold input on the edit form becomes optional. Blank submission → saves `None` to DB (= use global default). Router changes: `notify_below_pct: Optional[float] = Form(None)` replacing the current `float = Form(20.0)`.
- **D-08:** Item detail display shows the effective threshold. Two cases:
  - Custom set: "Notifying at X% below typical"
  - Using global default: "Notifying at X% below typical (default)"
  The enrichment helper in `app/routers/wishlist.py:64` passes raw `notify_below_pct`; the template or enricher must resolve the effective value for display.

### Claude's Discretion
- Exact label wording for "using global default" indicator in the UI
- Whether to show the global default value in the "using default" label or just say "default"
- Exact form placeholder text for the optional threshold input

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §NOTIF-05, NOTIF-06 — Per-item threshold requirements and acceptance criteria

### Core files to read
- `app/models.py` — `WishlistItem.notify_below_pct` column (line 13); full model structure
- `app/schemas.py` — `WishlistItemCreate` (line 10), `WishlistItemUpdate` (line 19), `WishlistItemResponse` (line 50)
- `app/services/notifier.py` — `should_notify()` (line ~34), email body builder (line ~127); full threshold logic
- `app/routers/wishlist.py` — add endpoint (line ~98), edit endpoint (line ~130), enricher (line ~64), API create endpoint (line ~316)
- `app/database.py` — existing migration pattern (lines 27–110); new migration goes here
- `app/config.py` — `Settings` class; new `notify_below_pct_default` field goes here
- `app/templates/item_detail.html` — threshold display (line ~47) and edit form (line ~248)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/schemas.py:19` — `WishlistItemUpdate.notify_below_pct: Optional[float] = None` already exists; create schema needs updating to match
- `app/database.py` — hand-written migration blocks using `try/except`; new migration block follows same pattern

### Established Patterns
- All settings are env-var backed via `pydantic-settings` (`app/config.py`); global default follows this pattern
- Migration pattern: `conn.execute(text("ALTER TABLE ..."))` wrapped in `try/except Exception: pass` for idempotency
- SQLite migration for structural changes uses create-new-table → copy → rename (see lines 67–92 in `app/database.py`)
- Form handlers: `notify_below_pct: float = Form(20.0)` → becomes `Optional[float] = Form(None)`

### Integration Points
- `app/services/notifier.py` — primary consumer of the threshold; needs `settings` injected or imported to resolve fallback
- `app/scheduler.py` — calls scanner/notifier for all active items; fallback logic in notifier covers this automatically
- iOS Shortcut API: `POST /api/wishlist` sends `notify_below_pct`; `WishlistItemCreate.notify_below_pct` has default 20.0 so existing Shortcut payloads without the field still work correctly
- Bulk import (`bulk_import.py`) posts to the API endpoint; same default applies

</code_context>

<specifics>
## Specific Ideas

No specific UI/UX references given — open to standard label approach for the "using default" indicator.

</specifics>

<deferred>
## Deferred Ideas

None — analysis stayed within phase scope.

</deferred>

---

*Phase: 24-per-item-notification-thresholds*
*Context gathered: 2026-04-21*
