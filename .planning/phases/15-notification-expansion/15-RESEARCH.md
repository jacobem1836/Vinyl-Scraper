# Phase 15: Notification Expansion - Research

**Researched:** 2026-04-13
**Domain:** Python async notification pipeline, SQLAlchemy migrations, Jinja2 email templating
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Price-drop trigger (NOTIF-02)**
- D-01: Price-drop alert fires when an existing listing's price decreases by at least a configurable threshold — either a percentage drop OR absolute dollar amount, one or the other per item, not both simultaneously.
- D-02: Add `notify_drop_mode` field to `WishlistItem` (enum: `"pct"` or `"usd"`, default `"pct"`).
- D-03: Add `notify_drop_pct` (Float, nullable) and `notify_drop_usd` (Float, nullable) to `WishlistItem` for per-item overrides. Null falls back to global defaults from settings.
- D-04: Add global settings: `notify_drop_pct_default` and `notify_drop_usd_default` to `config.py`.
- D-05: Add `prev_price` (Float, nullable) to `Listing`. Scanner writes it before overwriting `price`. Detection: `(prev_price - price) / prev_price * 100 >= threshold` (pct) or `prev_price - price >= threshold` (usd).

**Back-in-stock detection (NOTIF-01)**
- D-06: Add `prev_is_in_stock` (Boolean, nullable) to `Listing`. Scanner sets it before updating `is_in_stock`. Event fires when `prev_is_in_stock is False AND is_in_stock is True`.
- D-07: Back-in-stock is per-listing (one event per listing that transitions), not per item.

**Cool-down / deduplication (NOTIF-03)**
- D-08: Cool-down is per-WishlistItem. Add `last_notified_at` (DateTime, nullable) to `WishlistItem`.
- D-09: Add `notify_cooldown_hours` to `config.py` as env-overridable global setting.
- D-10: If `last_notified_at` is within the cooldown window at scan time, suppress all notification events for that item.

**Digest email (NOTIF-04)**
- D-11: One email per scan cycle — all qualifying events (new deals + back-in-stock + price drops). Subject: `[CRATE] Scan digest: {N} events across {M} items`.
- D-12: Existing `send_deal_email()` per-item flow in scheduler is REPLACED by scan-level `send_digest_email()`.
- D-13: New `digest_alert.html` template. Sections: deal alerts, price drops, back-in-stock.
- D-14: Zero qualifying events → no email sent.
- D-15: `send_deal_email()` can be removed or made private/internal.

### Claude's Discretion
- Exact schema migration approach (manual SQL, consistent with existing migrations)
- Email template visual layout within the existing CRATE aesthetic (near-black, inline CSS, same font stack)
- Whether `notify_drop_pct_default` defaults to 20% (same as `notify_below_pct`) or different value
- How to handle `prev_price` null (first scan) — skip price-drop check
- How to handle `prev_is_in_stock` null (first scan) — skip back-in-stock check
- Order of sections in digest email

### Deferred Ideas (OUT OF SCOPE)
- Per-notification-type preferences per item
- Per-item cool-down override
- Real-time push notifications
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NOTIF-01 | User receives back-in-stock alert when a listing transitions out-of-stock → in-stock | D-06/D-07: `prev_is_in_stock` column + scanner capture + event detection in scheduler |
| NOTIF-02 | User receives price-drop alert when a listing's price drops vs prior scan | D-01 through D-05: `prev_price` column + drop detection logic + per-item mode/threshold |
| NOTIF-03 | Notifier deduplicates repeat events within a cool-down window | D-08 through D-10: `last_notified_at` + `notify_cooldown_hours` setting |
| NOTIF-04 | Multiple events for one scan collapse into a single digest email | D-11 through D-15: scan-level `send_digest_email()` + `digest_alert.html` template |
</phase_requirements>

---

## Summary

Phase 15 is a pure Python refactor within an established codebase. No new libraries are required. The work involves four tightly coupled changes: schema additions (six new columns across two tables), scanner capture logic, event detection in the scheduler, and a new digest email flow replacing the existing per-item `send_deal_email()`.

All decisions are locked in CONTEXT.md. The research focus is confirming the exact patterns the codebase already uses and flagging every integration point the planner must address.

The riskiest task is the scheduler refactor — replacing per-item notification dispatch with scan-level event aggregation requires restructuring `scheduled_scan()` and `_scan_one()` carefully to avoid losing either scan results or in-flight exceptions.

**Primary recommendation:** Plan six logical units — migrations, model columns, scanner capture, event collection, digest notifier function, and digest template. Execute in that order; each unit has a clean dependency on the previous.

---

## Standard Stack

No new dependencies needed. All required capabilities are already present:

| Library | Current Version | Purpose in this Phase |
|---------|----------------|----------------------|
| SQLAlchemy | 2.0.36 | ORM model updates, column additions |
| Jinja2 | 3.1.4 | New `digest_alert.html` template |
| APScheduler | 3.10.4 | Scheduler refactor (no API change) |
| pydantic-settings | 2.6.0 | New config fields in `Settings` |
| aiosqlite / pg8000 | 0.20.0 / 1.31.2 | Migration SQL execution |

[VERIFIED: codebase grep — requirements.txt and app/config.py, app/models.py, app/scheduler.py]

**Installation:** No `pip install` needed.

---

## Architecture Patterns

### Recommended Project Structure (no new files except template)

```
app/
├── config.py              # + 3 new settings fields
├── models.py              # + 6 new columns across WishlistItem and Listing
├── database.py            # + 6 migration ALTER TABLE statements
├── scheduler.py           # refactored scheduled_scan()
└── services/
    └── notifier.py        # + send_digest_email(); send_deal_email() removed/privatised
templates/
└── digest_alert.html      # NEW — scan-level multi-section digest
```

### Pattern 1: Manual SQL Migration (established project pattern)

**What:** Each new column is added with a try/except `ALTER TABLE ... ADD COLUMN` block in `run_migrations()` inside `database.py`. Errors are silently swallowed because the column already existing is the expected failure mode on repeat startups.

**When to use:** Always — this is the only migration mechanism in the project. Alembic is not used.

**Example (from database.py lines 28-121):**
```python
try:
    conn.execute(text("ALTER TABLE listings ADD COLUMN prev_price FLOAT"))
    conn.commit()
except Exception:
    pass  # Column already exists

try:
    conn.execute(text("ALTER TABLE listings ADD COLUMN prev_is_in_stock INTEGER"))
    conn.commit()
except Exception:
    pass  # Column already exists
```

[VERIFIED: app/database.py — existing migration pattern]

Six migrations needed in total:
1. `listings.prev_price FLOAT` (nullable)
2. `listings.prev_is_in_stock INTEGER` (nullable, SQLite uses INTEGER for booleans)
3. `wishlist_items.last_notified_at DATETIME` (nullable)
4. `wishlist_items.notify_drop_mode VARCHAR` (default `'pct'`)
5. `wishlist_items.notify_drop_pct FLOAT` (nullable)
6. `wishlist_items.notify_drop_usd FLOAT` (nullable)

### Pattern 2: SQLAlchemy Model Column Addition

**What:** Add new `Column(...)` declarations to the existing ORM classes. SQLAlchemy reads these alongside the migration-added columns automatically — no ORM rebuild needed.

**Example:**
```python
# In WishlistItem
last_notified_at = Column(DateTime, nullable=True)
notify_drop_mode = Column(String, nullable=False, default="pct")
notify_drop_pct = Column(Float, nullable=True)
notify_drop_usd = Column(Float, nullable=True)

# In Listing
prev_price = Column(Float, nullable=True)
prev_is_in_stock = Column(Boolean, nullable=True)
```

[VERIFIED: app/models.py — existing column pattern]

### Pattern 3: Pydantic Settings Addition

**What:** Add new fields to the `Settings(BaseSettings)` class in `config.py`. Fields pick up values from `.env` automatically.

**Example:**
```python
notify_drop_pct_default: float = 20.0   # mirrors notify_below_pct default
notify_drop_usd_default: float = 5.0    # $5 absolute drop as sensible default
notify_cooldown_hours: int = 24
```

[VERIFIED: app/config.py — existing BaseSettings pattern]

### Pattern 4: Scanner prev_ Capture

**What:** In `scanner.py`, the existing-listing update path (lines 79-83) currently only updates `is_in_stock`. It must also snapshot `prev_price` and `prev_is_in_stock` before writing new values.

**Current code (lines 79-83):**
```python
if existing:
    new_stock = result.get("is_in_stock")
    if new_stock is not None:
        existing.is_in_stock = new_stock
    continue
```

**Required change:**
```python
if existing:
    # Snapshot previous state before overwriting
    existing.prev_price = existing.price
    existing.prev_is_in_stock = existing.is_in_stock
    # Now update current values
    new_price = result.get("price")
    if new_price is not None:
        existing.price = new_price
    new_stock = result.get("is_in_stock")
    if new_stock is not None:
        existing.is_in_stock = new_stock
    continue
```

[VERIFIED: app/services/scanner.py lines 74-83]

Note: The existing code does NOT update `existing.price` on re-scans — it only updates stock status. This phase adds price updating as well, which is a behaviour change. The planner should treat this as intentional (price drift tracking requires it).

### Pattern 5: Scan-Level Event Collection and Digest Dispatch

**What:** Replace the per-item `_scan_one` callback in `scheduler.py` with a two-phase approach:
1. Gather all scan results (existing pattern, keep `return_exceptions=True`)
2. After all scans complete, query for qualifying events and call `send_digest_email()`

**Current scheduler (lines 16-31):**
```python
async def scheduled_scan():
    db = SessionLocal()
    try:
        items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

        async def _scan_one(item):
            new_listings = await scanner.scan_item(db, item)
            if item.notify_email and new_listings:
                notifiable = [l for l in new_listings if notifier.should_notify(item, l, list(item.listings or []))]
                if notifiable:
                    await notifier.send_deal_email(item, notifiable)

        await asyncio.gather(*[_scan_one(item) for item in items], return_exceptions=True)
        invalidate_dashboard_cache()
    finally:
        db.close()
```

**Required shape after refactor:**
```python
async def scheduled_scan():
    db = SessionLocal()
    try:
        items = db.query(WishlistItem).filter(WishlistItem.is_active.is_(True)).all()

        async def _scan_one(item):
            return await scanner.scan_item(db, item)

        results = await asyncio.gather(*[_scan_one(item) for item in items], return_exceptions=True)
        invalidate_dashboard_cache()

        # Collect events across all items
        digest_items = []
        for item, result in zip(items, results):
            if isinstance(result, Exception):
                continue
            if not item.notify_email:
                continue
            # Cool-down check
            if item.last_notified_at and _within_cooldown(item.last_notified_at):
                continue
            events = _collect_events(db, item, result)
            if events:
                digest_items.append((item, events))

        if digest_items:
            await notifier.send_digest_email(digest_items)
            # Update last_notified_at for all notified items
            for item, _ in digest_items:
                item.last_notified_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
```

[VERIFIED: app/scheduler.py — full file read]

### Pattern 6: Digest Email Function Signature

**What:** `send_digest_email()` in `notifier.py` receives a list of `(WishlistItem, events_dict)` tuples where `events_dict` contains three keys:

```python
{
    "deal_alerts": [Listing, ...],       # new listings below notify_below_pct threshold
    "price_drops": [(Listing, float, float), ...],  # (listing, prev_price, new_price)
    "back_in_stock": [Listing, ...],
}
```

Subject line: `[CRATE] Scan digest: {total_events} events across {len(digest_items)} items`

[ASSUMED] — the exact function signature is Claude's discretion per CONTEXT.md. The shape above is the recommended approach based on what the template needs to render.

### Pattern 7: Digest Email Template Structure

**What:** `digest_alert.html` follows the same inline-CSS near-black CRATE aesthetic as `deal_alert.html`. Three sections, each rendered only if non-empty. Each section links back to the item detail page.

**Template sections:**
1. Deal alerts — new listings below threshold (reuses existing per-item deal logic from `should_notify()`)
2. Price drops — existing listings where `prev_price - price` exceeds threshold
3. Back-in-stock — existing listings transitioning `False → True`

**MSO / Outlook considerations:** The existing `deal_alert.html` already includes the MSO conditional comment block for Outlook light-mode fallback. Replicate this in `digest_alert.html` verbatim.

[VERIFIED: templates/deal_alert.html — full template read]

### Anti-Patterns to Avoid

- **Triggering back-in-stock on first scan:** `prev_is_in_stock` will be `None` on first scan for any listing. The detection must guard: `prev_is_in_stock is False AND is_in_stock is True` (explicit False, not just falsy).
- **Triggering price-drop on first scan:** `prev_price` will be `None` on first scan. Guard: `prev_price is not None AND price is not None AND prev_price > price`.
- **Per-item email inside the gather:** The old `_scan_one` sent email inside the concurrent gather. The new design must not do this — email goes after all scans complete, at the scan level.
- **Forgetting to update `last_notified_at`:** After sending the digest, `last_notified_at` must be committed for every item that was included. Forgetting this makes cool-down permanently ineffective.
- **Re-sending on zero events:** Guard with `if not digest_items: return` before calling `send_digest_email()`.
- **Price not updated on re-scan:** Currently the scanner does not update `existing.price` on repeat scans (only updates stock). Adding `prev_price` snapshot requires also updating `existing.price` — both changes must land together or the feature is broken.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SMTP dispatch | Custom SMTP wrapper | Existing `_send_smtp()` in notifier.py | Already handles STARTTLS, MIMEMultipart, to_thread |
| Plain-text fallback | Custom HTML stripper | Existing `_html_to_plaintext()` in notifier.py | Already handles HTML entity decoding |
| Jinja2 env setup | New env instance | Existing `_email_env` in notifier.py | Same env, just add new template to `templates/` dir |
| Database migrations | Alembic | Manual SQL in `run_migrations()` | Project pattern — Alembic not present |
| Median price calc | Custom median | Existing `compute_typical_price()` | Already handles edge cases (None, empty) |
| Deal detection | Custom threshold | Existing `should_notify()` | Already handles null prices, no-history case |

**Key insight:** Every infrastructure primitive for this phase already exists. The entire implementation is orchestration — wiring existing functions together in a new order.

---

## Common Pitfalls

### Pitfall 1: Scanner Does Not Currently Update existing.price

**What goes wrong:** The current existing-listing path in `scanner.py` only updates `is_in_stock`. If `prev_price` is written before overwriting `price`, but `price` is never overwritten, `prev_price` will always equal `price` — price-drop detection fires zero events forever.

**Why it happens:** The original scanner was append-only for listings; `is_in_stock` was the only mutable field added later.

**How to avoid:** The scanner change must update BOTH `prev_price = existing.price` AND then `existing.price = result.get("price")` (when the result has a price). These are a single atomic change — planner must put them in the same task.

**Warning signs:** Integration test shows no price-drop events despite price changes in test data.

### Pitfall 2: SQLite Boolean Stored as INTEGER

**What goes wrong:** SQLite has no native BOOLEAN type. `ALTER TABLE listings ADD COLUMN prev_is_in_stock INTEGER` is correct. The existing `is_in_stock` column uses `INTEGER NOT NULL DEFAULT 1`. The migration for `prev_is_in_stock` should be nullable (no DEFAULT) so NULL correctly means "not yet observed."

**Why it happens:** SQLAlchemy maps `Boolean` to INTEGER(0/1) for SQLite automatically, but the raw SQL migration must match.

**How to avoid:** Migration SQL: `ALTER TABLE listings ADD COLUMN prev_is_in_stock INTEGER` (no DEFAULT, nullable).

**Warning signs:** Column created with DEFAULT 0, causing first-scan back-in-stock false positives for listings that start in-stock.

### Pitfall 3: Cool-Down Applied at Collection Time vs Notification Time

**What goes wrong:** If cool-down is checked only at collection time (before scanning), an item that was notified recently is silently skipped — but its listings' `prev_price` and `prev_is_in_stock` snapshots are still written during scan. Next cycle, events for those skipped items will not re-fire because `prev_price` is now updated to current. This is correct behaviour.

**Why it happens:** Subtle sequencing — snapshot write happens in scanner (always), event detection happens in scheduler (cool-down gated).

**How to avoid:** Cool-down check must be in the scheduler event collection, not in the scanner. Scanner always writes prev_ snapshots regardless of notification preferences.

### Pitfall 4: asyncio.gather return_exceptions Masking scan results

**What goes wrong:** With `return_exceptions=True`, some elements of the `results` list will be `Exception` instances, not `list[Listing]`. The event collection loop must check `isinstance(result, Exception)` before using it.

**How to avoid:** The refactored `_scan_one` callback should return the scan result list. Event collection iterates `zip(items, results)` and skips exception entries.

### Pitfall 5: Digest Email Sent with Empty Sections

**What goes wrong:** If `digest_items` has entries but all events for every item are empty after filtering, the digest email would render with only headers and no content.

**How to avoid:** `_collect_events()` should return `None` or an empty dict when no events qualify. The outer loop appends only items with non-empty events. Guard: `if events` before appending.

### Pitfall 6: `last_notified_at` not Committed After Send

**What goes wrong:** If the `db.commit()` updating `last_notified_at` fails silently, the cool-down window is never set. Next scheduled scan sends another digest.

**How to avoid:** Update and commit `last_notified_at` in a separate try/except block so a commit failure is at least logged, even if it can't be retried.

---

## Code Examples

### Migration SQL for Six New Columns
```python
# Source: established pattern from app/database.py lines 28-121
try:
    conn.execute(text("ALTER TABLE listings ADD COLUMN prev_price FLOAT"))
    conn.commit()
except Exception:
    pass

try:
    conn.execute(text("ALTER TABLE listings ADD COLUMN prev_is_in_stock INTEGER"))
    conn.commit()
except Exception:
    pass

try:
    conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN last_notified_at DATETIME"))
    conn.commit()
except Exception:
    pass

try:
    conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN notify_drop_mode VARCHAR NOT NULL DEFAULT 'pct'"))
    conn.commit()
except Exception:
    pass

try:
    conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN notify_drop_pct FLOAT"))
    conn.commit()
except Exception:
    pass

try:
    conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN notify_drop_usd FLOAT"))
    conn.commit()
except Exception:
    pass
```

### Price-Drop Detection Logic
```python
def _price_dropped(listing: Listing, item: WishlistItem, settings: Settings) -> bool:
    """Return True if listing price dropped beyond threshold since last scan."""
    if listing.prev_price is None or listing.price is None:
        return False  # first scan or no price data — skip
    if listing.prev_price <= listing.price:
        return False  # price didn't drop

    mode = item.notify_drop_mode or "pct"
    if mode == "pct":
        threshold = item.notify_drop_pct if item.notify_drop_pct is not None else settings.notify_drop_pct_default
        drop_pct = (listing.prev_price - listing.price) / listing.prev_price * 100
        return drop_pct >= threshold
    else:  # usd
        threshold = item.notify_drop_usd if item.notify_drop_usd is not None else settings.notify_drop_usd_default
        return (listing.prev_price - listing.price) >= threshold
```

### Back-in-Stock Detection Logic
```python
def _back_in_stock(listing: Listing) -> bool:
    """Return True if listing transitioned from out-of-stock to in-stock."""
    # prev_is_in_stock must be explicitly False (not None) — None means first scan
    return listing.prev_is_in_stock is False and listing.is_in_stock is True
```

### Cool-Down Check
```python
from datetime import datetime, timedelta

def _within_cooldown(last_notified_at: datetime) -> bool:
    cooldown = timedelta(hours=settings.notify_cooldown_hours)
    return (datetime.utcnow() - last_notified_at) < cooldown
```

---

## State of the Art

No library ecosystem changes needed. This is a pure internal refactor.

| Old Approach | Current Approach | Notes |
|--------------|------------------|-------|
| Per-item `send_deal_email()` called inside scatter | Scan-level `send_digest_email()` called once after all scans | Core change of this phase |
| No prev_ snapshot columns | `prev_price` + `prev_is_in_stock` on `Listing` | Enables delta detection |
| No cool-down | `last_notified_at` + `notify_cooldown_hours` | Prevents notification spam |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `send_digest_email()` should receive `list[tuple[WishlistItem, dict]]` as its primary argument | Architecture Patterns §6 | Low — Claude's discretion per CONTEXT.md; can be adjusted in planning without user input |
| A2 | `notify_drop_pct_default` defaults to 20.0 (mirrors `notify_below_pct`) | Standard Stack | Low — CONTEXT.md says this is Claude's discretion |
| A3 | `notify_drop_usd_default` defaults to 5.0 | Standard Stack | Low — Claude's discretion |
| A4 | `notify_cooldown_hours` defaults to 24 | Standard Stack | Low — CONTEXT.md says planner picks sensible default |
| A5 | The scanner should update `existing.price` (not just `is_in_stock`) when re-scanning | Common Pitfalls §1 | Medium — this is a behaviour change, but required for price-drop tracking. If wrong, price-drop detection never fires. Confirmed by decision D-05 logic. |

**Claims A1–A5 are Claude's-discretion items.** No user confirmation needed before planning.

---

## Open Questions

1. **Deal alert section of digest: filter by `should_notify()` or include all new listings?**
   - What we know: `should_notify()` is the existing gate for deal alerts; new listings are returned by `scan_item()`
   - What's unclear: CONTEXT.md D-11 says "new deals" in the digest — "deals" implies `should_notify()` still filters them
   - Recommendation: Apply `should_notify()` to new listings for the deal-alert section, consistent with current behaviour. Planner can lock this.

2. **Should `send_deal_email()` be fully deleted or kept as a private helper?**
   - What we know: D-15 says it can be removed or made private/internal
   - What's unclear: No other callers detected in the codebase
   - Recommendation: Remove it entirely to reduce surface area. Planner can decide.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 15 is a pure code/config change with no new external dependencies. All runtime dependencies (SMTP, SQLite/PostgreSQL) are already wired.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (configured via rules; no pytest.ini found in repo) |
| Config file | None detected — Wave 0 must create minimal config if needed |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NOTIF-01 | `prev_is_in_stock=False + is_in_stock=True` fires back-in-stock event | unit | `pytest tests/test_notifier.py::test_back_in_stock -x` | Wave 0 |
| NOTIF-01 | `prev_is_in_stock=None` (first scan) does NOT fire | unit | `pytest tests/test_notifier.py::test_back_in_stock_first_scan -x` | Wave 0 |
| NOTIF-02 | Price drop in pct mode fires when drop >= threshold | unit | `pytest tests/test_notifier.py::test_price_drop_pct -x` | Wave 0 |
| NOTIF-02 | Price drop in usd mode fires when drop >= threshold | unit | `pytest tests/test_notifier.py::test_price_drop_usd -x` | Wave 0 |
| NOTIF-02 | `prev_price=None` does NOT fire | unit | `pytest tests/test_notifier.py::test_price_drop_no_prev -x` | Wave 0 |
| NOTIF-03 | Item within cooldown window produces no events | unit | `pytest tests/test_notifier.py::test_cooldown_suppresses -x` | Wave 0 |
| NOTIF-03 | Item outside cooldown window produces events | unit | `pytest tests/test_notifier.py::test_cooldown_expired -x` | Wave 0 |
| NOTIF-04 | Zero events → no email sent | unit | `pytest tests/test_notifier.py::test_no_digest_on_zero_events -x` | Wave 0 |
| NOTIF-04 | Multiple items/events → single digest call | unit | `pytest tests/test_notifier.py::test_digest_aggregates -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_notifier.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_notifier.py` — covers all NOTIF-* unit cases above
- [ ] `tests/conftest.py` — shared fixtures (mock WishlistItem, mock Listing with prev_ columns)

---

## Security Domain

Phase 15 does not introduce new authentication, user input, or cryptographic operations. No new ASVS categories are relevant.

| ASVS Category | Applies | Notes |
|---------------|---------|-------|
| V2 Authentication | no | No auth changes |
| V3 Session Management | no | No session changes |
| V4 Access Control | no | No ACL changes |
| V5 Input Validation | no | No new user input paths |
| V6 Cryptography | no | No crypto; SMTP credentials already managed via settings |

The one security-adjacent concern: `last_notified_at` is a server-side field — no user input involved.

---

## Sources

### Primary (HIGH confidence)
- `app/services/notifier.py` — full read; confirmed reusable assets (_send_smtp, _html_to_plaintext, _email_env, should_notify, compute_typical_price)
- `app/scheduler.py` — full read; confirmed current _scan_one pattern and gather call
- `app/models.py` — full read; confirmed existing columns and relationship definitions
- `app/config.py` — full read; confirmed BaseSettings pattern
- `app/database.py` — full read; confirmed manual SQL migration pattern (6 prior examples)
- `app/services/scanner.py` — full read; confirmed existing-listing update path at lines 79-83
- `templates/deal_alert.html` — full read; confirmed CRATE inline-CSS style to replicate
- `.planning/phases/15-notification-expansion/15-CONTEXT.md` — full read; all decisions locked

### Secondary (MEDIUM confidence)
- None required — all research was direct codebase inspection

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified via direct file reads; no new libraries
- Architecture: HIGH — all patterns drawn from existing code with line references
- Pitfalls: HIGH — derived from direct code inspection, not generalised knowledge

**Research date:** 2026-04-13
**Valid until:** Until scanner.py or notifier.py are substantially refactored (indefinitely stable otherwise)
