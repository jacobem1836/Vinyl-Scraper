---
phase: 09-email-redesign
plan: 01
subsystem: email
tags: [email, template, jinja2, inline-css]
dependency_graph:
  requires: []
  provides: [templates/deal_alert.html]
  affects: [app/services/notifier.py]
tech_stack:
  added: []
  patterns: [tables-only email layout, MSO conditional comments, inline CSS hex literals]
key_files:
  created: [templates/deal_alert.html]
  modified: []
decisions:
  - "Tables-only email layout with no flexbox/grid for broad email client compatibility"
  - "MSO conditional fallback renders white background with dark text for Outlook Word-engine clients"
  - "All styles as inline hex literals — no CSS custom properties (Jinja2 renders before email delivery)"
  - "Single footer CTA 'View on CRATE' — no per-listing links per D-02"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-07"
  tasks_completed: 1
  files_created: 1
  files_modified: 0
---

# Phase 9 Plan 1: CRATE Deal Alert Email Template Summary

**One-liner:** Dark CRATE deal alert email using tables-only layout, inline hex CSS, Jinja2 variables, and MSO Outlook fallback.

## What Was Built

Created `templates/deal_alert.html` — a complete Jinja2 HTML email template implementing the CRATE deal alert design:

- **Hero block:** CRATE wordmark header, item name with type badge, best landed price (large), percentage below typical in success green (#34d399), notification threshold note in muted text
- **Listing table:** Columns for Title, Landed Price (AUD), Source, Ships From — rendered via `{% for listing in listings %}` loop
- **Footer:** Single centered "View on CRATE" link pointing to `{{ item_url }}`; compliance note below
- **MSO fallback:** `<!--[if mso]>` conditional block forces white background with dark #333333 text for Outlook/Word-rendering clients

## Template Variables

| Variable | Type | Description |
|----------|------|-------------|
| `item_name` | str | Wishlist item query |
| `item_type` | str | "album", "artist", or "label" |
| `best_landed_price` | str | Formatted AUD price |
| `pct_below_typical` | str | Formatted percentage |
| `has_typical_price` | bool | Guards pct_below_typical display |
| `listings` | list[dict] | Each with title, landed_price, source, ships_from |
| `item_url` | str | Relative URL to item detail page |
| `notify_below_pct` | str | User's notification threshold |

## Decisions Made

1. **Tables-only layout** — `<table>/<tr>/<td>` throughout; no divs for structure; no flexbox or grid; `align="center"` attributes on outer table for broad compatibility.
2. **Inline hex only** — All CSS as inline `style="..."` attributes with hex literals. No `<style>` block (Gmail strips it), no `var(--)` (Jinja2 can't resolve them).
3. **MSO conditional** — `<!--[if mso]>` block overrides background colors to white and text to dark for Outlook's Word-rendering engine which strips background-color.
4. **Single footer link** — Per D-02, no per-listing links. One "View on CRATE" CTA pointing to the item dashboard page.
5. **Autoescaping** — Jinja2's default `Environment` has autoescaping off for `.html` files unless explicitly enabled. Since notifier.py currently uses `html.escape()` manually, Plan 02 should enable `autoescape=True` when constructing the Jinja2 Environment to satisfy T-09-01 (injection mitigation).

## Deviations from Plan

None — plan executed exactly as written. The four design tool invocations (ui-ux-pro-max, design-for-ai, magic MCP, stitch MCP) were noted in the important_note as design research aids already incorporated into the plan spec; they were not invoked per orchestrator instruction.

## Known Stubs

None — all template variables render real data from notifier.py's call site.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: injection | templates/deal_alert.html | Jinja2 autoescaping not explicitly enabled in Environment; Plan 02 must set `autoescape=True` when rendering this template to satisfy T-09-01 |

## Verification

```
PASS: template renders correctly
All acceptance criteria PASS
No forbidden patterns found
```

Checked: `#0a0a0a`, `#111111`, `#f5f5f5` present as inline styles; `{{ item_name }}`, `{{ best_landed_price }}`, `{{ pct_below_typical }}`, `{% for listing in listings %}`, `View on CRATE`, `{{ item_url }}`, `<!--[if mso]>` all present; no `var(--)`, `display:flex`, or `display:grid`.

## Self-Check: PASSED

- `templates/deal_alert.html` exists and renders without error
- Commit `ddd1812` exists: `feat(09-01): create CRATE deal alert email template`
