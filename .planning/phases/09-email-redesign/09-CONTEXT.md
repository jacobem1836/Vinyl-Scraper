# Phase 9: Email Redesign - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Deal alert emails redesigned with inline CSS, CRATE-consistent dark aesthetic, and scannable deal summary. Only `notifier.py` and a new template file are in scope. No changes to scan logic, deal detection thresholds, or notification triggers.

</domain>

<decisions>
## Implementation Decisions

### Email Layout & Hierarchy
- **D-01:** Hero summary block at top with item name + type badge, best landed price, and % below typical price — then a listing table below with all deal listings
- **D-02:** Single "View on CRATE" link in the email footer pointing to the item's dashboard page — no per-listing links, no hero link

### Visual Treatment
- **D-03:** Full dark CRATE aesthetic as primary: #0a0a0a body, #111111 content area, #f5f5f5 text, #ffffff accent, #222222 borders — all as inline CSS with hex literals (no CSS custom properties)
- **D-04:** Outlook fallback via MSO conditional comments — renders dark text on white background for clients that strip background colors. Belt-and-suspenders approach for cross-client compatibility.

### Deal Summary Content
- **D-05:** Hero block shows: item name with type badge (album/artist/label), best landed price (AUD), percentage below typical price
- **D-06:** Listing table columns: Title, Landed Price (AUD), Source, Ships From — no condition column, no per-listing links

### Template Approach
- **D-07:** Email HTML in a separate Jinja2 template file (`templates/deal_alert.html`). `notifier.py` renders it with Jinja2 (already a project dependency). Separates layout from logic.
- **D-08:** Auto-generated plain-text fallback — strip HTML to produce a text/plain MIME part for text-only clients and improved deliverability

### Claude's Discretion
- Exact inline CSS implementation (table widths, padding, font sizing)
- MSO conditional comment structure for Outlook fallback
- HTML-to-plaintext stripping approach
- Email subject line format (current: `[Vinyl Wishlist] New deal for: {query}`)
- CRATE wordmark/header treatment in email (text-only is fine)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Email requirements
- `.planning/REQUIREMENTS.md` — EMAIL-01, EMAIL-02, EMAIL-03 define the acceptance criteria

### Existing email implementation
- `app/services/notifier.py` — Current email construction logic, SMTP sending, deal threshold calculation
- `app/config.py` — SMTP settings (smtp_host, smtp_port, smtp_user, smtp_password, notify_email)

### Design system
- `static/style.css` lines 20-65 — CRATE design tokens (color palette, spacing) — use hex equivalents in email inline CSS

### Required design tooling (from ROADMAP.md)
- `ui-ux-pro-max` Claude skill — email layout and visual hierarchy direction
- `design-for-ai` Claude skill — visual design principles
- `mcp__magic__*` — 21st Magic component inspiration for email patterns
- `mcp__stitch__*` — design system application

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/services/notifier.py` — `compute_typical_price()`, `should_notify()`, `_landed()` functions stay as-is; only `send_deal_email()` and `_send_smtp()` change
- Jinja2 already in requirements (used for web templates) — no new dependency needed
- `MIMEMultipart("alternative")` already set up in `_send_smtp()` — adding a text/plain part is straightforward

### Established Patterns
- Email sending uses `asyncio.to_thread()` to avoid blocking the event loop
- HTML escaping via `html.escape()` for user-supplied data
- Settings accessed via `settings.smtp_*` and `settings.notify_email`

### Integration Points
- `send_deal_email(item, new_listings)` is called from `app/services/scanner.py` — signature should not change
- Template directory: `templates/` (already exists for web templates, Jinja2 Environment may need configuration for email templates)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches within the decisions above.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-email-redesign*
*Context gathered: 2026-04-07*
