# Phase 25: eBay Credentials - Context

**Gathered:** 2026-04-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire eBay credentials to config and verify the adapter returns AU listings for wishlist items. The eBay adapter (`app/services/ebay.py`) is already fully implemented and registered — this phase is about credential wiring, `.env.example` documentation, startup warnings, and live verification.

</domain>

<decisions>
## Implementation Decisions

### Adapter Status
- **D-01:** The eBay adapter is already complete and registered. `app/services/ebay.py` handles OAuth2 Browse API auth, `adapter.py` registers it as enabled. Real credentials (`EBAY_APP_ID`, `EBAY_CERT_ID`) are already in `.env`. No new adapter code needed.

### What to add
- **D-02:** Add eBay credentials section to `.env.example` — document `EBAY_APP_ID`, `EBAY_CERT_ID`, and `EBAY_DEV_ID` with descriptions explaining what each is and where to get them.
- **D-03:** Add a startup warning to `app/main.py` `startup()` when `settings.ebay_app_id` or `settings.ebay_cert_id` is absent. Follow the existing `print("[startup] ...")` pattern used for DB init.

### EBAY_DEV_ID
- **D-04:** Document `EBAY_DEV_ID` in `.env.example` only. Do NOT add it to `config.py` or the adapter — the Browse API only uses App ID + Cert ID for OAuth2. Dev ID is a Trading API credential and is unused in this codebase.

### Claude's Discretion
- Exact wording of the startup warning message
- Placement order of eBay entries in `.env.example`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §eBay Activation — EBAY-01, EBAY-02 acceptance criteria

### Existing implementation
- `app/services/ebay.py` — Complete Browse API adapter (OAuth2, AU marketplace, graceful skip when no creds)
- `app/config.py` — `ebay_app_id` and `ebay_cert_id` already present as `Optional[str]`
- `app/services/adapter.py` — eBay registered in `ADAPTER_REGISTRY` as enabled
- `app/main.py` — `startup()` function where warning should be added (lines 28-45)
- `.env.example` — File to update with eBay credential entries

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/main.py` startup pattern: `print("[startup] ...")` for logging — use same prefix for eBay warning
- `app/services/ebay.py:47-49`: existing per-scan skip logic (`if not settings.ebay_app_id or not settings.ebay_cert_id`)

### Established Patterns
- Config: `Optional[str] = None` fields in `app/config.py` with inline comments — pattern for new fields if needed
- Startup warnings: `print(f"[startup] ...")` as established in `main.py`
- `.env.example`: comment-prefixed sections with `# Description` then `KEY=placeholder` format

### Integration Points
- Startup warning wires into `startup()` in `app/main.py` — no new file needed
- `.env.example` is standalone documentation file — no code dependency

</code_context>

<specifics>
## Specific Ideas

No specific requirements — the implementation is essentially pre-built. Focus is credential documentation and startup observability.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 25-ebay-credentials*
*Context gathered: 2026-04-21*
