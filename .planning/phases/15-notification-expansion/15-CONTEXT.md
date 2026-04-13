# Phase 15: Notification Expansion - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Users receive back-in-stock and price-drop alerts on existing listings, deduped within a cool-down window, consolidated into a single digest email per scan cycle. Existing deal alerts (new listings below threshold) are merged into the same digest — there is no separate email flow after this phase.

In scope: NOTIF-01, NOTIF-02, NOTIF-03, NOTIF-04
Out of scope: per-notification-type preferences per item, UI to manage notification settings, real-time push notifications, new email template themes.

</domain>

<decisions>
## Implementation Decisions

### Price-drop trigger (NOTIF-02)
- **D-01:** Price-drop alert fires when an existing listing's price decreases by at least a configurable threshold. The threshold is expressed as EITHER a percentage drop OR an absolute dollar amount — one or the other per item, not both simultaneously.
- **D-02:** Add `notify_drop_mode` field to `WishlistItem` (enum: `"pct"` or `"usd"`, default `"pct"`) to record which mode is active.
- **D-03:** Add `notify_drop_pct` (Float, nullable) and `notify_drop_usd` (Float, nullable) to `WishlistItem` for per-item overrides. When both are null, fall back to global defaults from settings.
- **D-04:** Add global settings: `notify_drop_pct_default` and `notify_drop_usd_default` to `config.py`.
- **D-05:** Price tracking: add `prev_price` (Float, nullable) column to `Listing`. Scanner populates it with the previous price before overwriting. Price-drop detection reads `(prev_price - price) / prev_price * 100 >= threshold` (pct mode) or `prev_price - price >= threshold` (usd mode).

### Back-in-stock detection (NOTIF-01)
- **D-06:** Add `prev_is_in_stock` (Boolean, nullable) column to `Listing`. Scanner sets it to the current value before updating `is_in_stock`. A back-in-stock event fires when `prev_is_in_stock is False AND is_in_stock is True`.
- **D-07:** Back-in-stock is per-listing (one event per listing that transitions), not per item.

### Cool-down / deduplication (NOTIF-03)
- **D-08:** Cool-down is per-WishlistItem (shared across all event types for that item). Add `last_notified_at` (DateTime, nullable) to `WishlistItem`.
- **D-09:** Add `notify_cooldown_hours` to `config.py` as an env-overridable global setting (no per-item override for now). Planner picks a sensible default (e.g. 24h).
- **D-10:** If `last_notified_at` is within the cooldown window at scan time, suppress all notification events for that item.

### Digest email (NOTIF-04)
- **D-11:** One email per scan cycle covering ALL items with qualifying events (new deals + back-in-stock + price drops). Subject: `[CRATE] Scan digest: {N} events across {M} items` (or similar — exact copy at Claude's discretion).
- **D-12:** The existing `send_deal_email()` per-item flow in the scheduler is REPLACED by a scan-level `send_digest_email()` function. No separate email paths remain after this phase.
- **D-13:** Digest email template: a new `digest_alert.html` template. Sections: deal alerts (new listings below threshold), price drops, back-in-stock. Each section lists the relevant item name, listing title, old/new price or price, and a link to the item detail page.
- **D-14:** If zero qualifying events across all items, no email is sent.
- **D-15:** `send_deal_email()` in `notifier.py` can be removed or made private/internal — no longer called from scheduler.

### Claude's Discretion
- Exact schema migration approach (manual SQL, consistent with existing migrations in the project)
- Email template visual layout within the existing CRATE aesthetic (near-black, inline CSS, same font stack)
- Whether `notify_drop_pct_default` defaults to same value as `notify_below_pct` default (20%) or different
- How to handle a listing where `prev_price` is null (first scan) — skip price-drop check that scan
- How to handle `prev_is_in_stock` null (first scan) — skip back-in-stock check that scan
- Order of sections in digest email

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — NOTIF-01, NOTIF-02, NOTIF-03, NOTIF-04 acceptance criteria
- `.planning/ROADMAP.md` §"Phase 15: Notification Expansion" — success criteria and scope anchor

### Existing code to modify
- `app/services/notifier.py` — `send_deal_email()` to be replaced with `send_digest_email()`; `should_notify()`, `compute_typical_price()` remain but may be refactored
- `app/scheduler.py` — `scheduled_scan()` inner loop to be replaced with scan-level digest dispatch
- `app/models.py` — `Listing` (add `prev_price`, `prev_is_in_stock`); `WishlistItem` (add `last_notified_at`, `notify_drop_mode`, `notify_drop_pct`, `notify_drop_usd`)
- `app/config.py` — add `notify_drop_pct_default`, `notify_drop_usd_default`, `notify_cooldown_hours`
- `app/services/scanner.py` — update existing-listing path to capture `prev_price` and `prev_is_in_stock` before overwriting
- `templates/deal_alert.html` — reference for CRATE inline-CSS style to replicate in new digest template

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_landed()`, `compute_typical_price()`, `should_notify()` in `notifier.py` — reuse for deal-alert section of digest
- `_send_smtp()` and `_html_to_plaintext()` in `notifier.py` — reuse unchanged
- `_email_env` (Jinja2 env) in `notifier.py` — new digest template slots in via same env
- `WishlistItem.notify_email` boolean — still gates whether item participates in notifications at all
- `WishlistItem.notify_below_pct` — still used for deal-alert section of digest (unchanged threshold logic)

### Established Patterns
- Manual SQL migrations (not Alembic) — existing pattern in codebase
- Settings via `pydantic_settings.BaseSettings` in `config.py` with env override — add new fields here
- `asyncio.to_thread()` for SMTP blocking I/O — keep this pattern in `send_digest_email()`
- Per-item scan continues on exception (`return_exceptions=True` in gather) — keep for robustness

### Integration Points
- Scanner (`scanner.py` `scan_item()`) — existing-listing update path (lines ~50-55) needs to write `prev_price` and `prev_is_in_stock` before updating
- Scheduler (`scheduler.py` `scheduled_scan()`) — per-item `_scan_one` callback to be replaced with scan-level event collection then single digest dispatch
- Event collection: after all scans complete, query listings with (`prev_price > price` by threshold OR `prev_is_in_stock = False AND is_in_stock = True`) for items with `notify_email = True` and outside cooldown window

</code_context>

<specifics>
## Specific Ideas

- Price drop: user wants the flexibility of % OR $ — "maybe keep this [the existing % approach], and also add a $ amount they can set (an option for one or the other, not both)". Per-item mode toggle is the right shape.
- Cool-down: user confirmed it should be a configurable setting, not hardcoded.

</specifics>

<deferred>
## Deferred Ideas

- Per-notification-type preferences per item (e.g., opt-in to back-in-stock but not price-drop) — "global preferences only for now" as per REQUIREMENTS.md
- Per-item cool-down override — current design is global setting; per-item override deferred
- Real-time push notifications — email-only this milestone

</deferred>

---

*Phase: 15-notification-expansion*
*Context gathered: 2026-04-13*
