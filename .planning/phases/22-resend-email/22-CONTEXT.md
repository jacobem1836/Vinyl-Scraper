# Phase 22: Resend Email - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate deal alert email sending from SMTP to the Resend API. The email template, notification logic, and trigger conditions are unchanged — only the transport layer is replaced. SMTP configuration is removed from the codebase entirely.

</domain>

<decisions>
## Implementation Decisions

### Transport / SDK
- **D-01:** Use the official `resend` Python SDK (add `resend` to `requirements.txt`). Not raw httpx — the SDK is simpler and the todo explicitly calls for it.
- **D-02:** The async call in `send_deal_email` should wrap the SDK call in `asyncio.to_thread()` (same pattern as the current `_send_smtp` call) since the SDK is synchronous.

### Sender Identity
- **D-03:** Add `RESEND_FROM` as a new optional env var in `config.py` (e.g. `resend_from: Optional[str] = None`). The notifier uses this as the `from` address. User will set it to their verified domain address once they have one.
- **D-04:** If `RESEND_FROM` is not set, sending is skipped (same guard pattern as current SMTP check for missing credentials).

### Config Cleanup
- **D-05:** Remove `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password` from `Settings` in `app/config.py`. Old `.env` values become harmless unread vars.
- **D-06:** Existing `notify_email` stays — it's the recipient address and is unrelated to Resend.

### Guard Condition
- **D-07:** The send guard in `send_deal_email` changes from checking `smtp_user and smtp_password` to checking `resend_api_key and resend_from and notify_email`.

### Claude's Discretion
- Error handling: same pattern as current (catch Exception, print, return False)
- Subject line: keep `[CRATE] Deal alert: {item.query}`
- Email content / template: unchanged

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current notifier implementation
- `app/services/notifier.py` — Full SMTP implementation to be replaced; keep all non-transport logic intact
- `app/config.py` — Settings class; SMTP fields to remove, RESEND_* fields to add

### Requirements
- `.planning/REQUIREMENTS.md` §EMAIL-04 — "Deal alert emails sent via Resend API, replacing SMTP"

### Todo context
- `.planning/todos/pending/2026-04-15-change-to-resend-for-emails.md` — Original todo with problem/solution description

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_html_to_plaintext()` in `notifier.py` — Keep as-is; produces plain-text fallback
- `compute_typical_price()`, `should_notify()`, `_landed()` — Pure logic functions; untouched
- `deal_alert.html` Jinja template — Unchanged
- `asyncio.to_thread()` pattern — Already used for `_send_smtp`; reuse for Resend SDK call

### Established Patterns
- Send guard: check required config fields at top of `send_deal_email`, return `False` early if missing
- Error handling: `try/except Exception as e: print(f"[Notifier] Failed..."); return False`
- Config via `pydantic_settings.BaseSettings` + `.env` file

### Integration Points
- `app/config.py` — Add `resend_api_key: Optional[str]` and `resend_from: Optional[str]`; remove 4 SMTP fields
- `app/services/notifier.py` — Replace `_send_smtp` + `asyncio.to_thread` block with Resend SDK call
- `requirements.txt` — Add `resend` package

</code_context>

<specifics>
## Specific Ideas

- User doesn't have a Resend-verified domain yet; `RESEND_FROM` will be set later when they set up their domain. Implementation should treat it as optional with a graceful skip.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 22-resend-email*
*Context gathered: 2026-04-19*
