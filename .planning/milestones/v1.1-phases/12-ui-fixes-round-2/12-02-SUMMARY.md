---
phase: 12-ui-fixes-round-2
plan: "02"
subsystem: web-forms, email-template
tags: [bug-fix, notify-email, email-branding, checkbox, form-handling]
dependency_graph:
  requires: []
  provides: [notify-email-fix, email-branding]
  affects: [app/routers/wishlist.py, templates/deal_alert.html, templates/index.html, templates/item_detail.html]
tech_stack:
  added: []
  patterns: [hidden-field-checkbox-pattern, inline-email-styles]
key_files:
  created: []
  modified:
    - app/routers/wishlist.py
    - templates/index.html
    - templates/item_detail.html
    - templates/deal_alert.html
decisions:
  - Hidden field pattern for checkbox: add <input type="hidden" name="notify_email" value=""> before each checkbox so unchecked state always sends a value
  - Explicit string allowlist for notify_email conversion: ("on", "true", "1", "yes") — any other value including "" is False
  - Georgia serif for email branding: email-safe serif font approximates Bodoni Moda display feel without web font loading
metrics:
  duration: "12 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  files_changed: 4
---

# Phase 12 Plan 02: Notify Email Bug Fix and Email Branding Summary

**One-liner:** Fixed HTML checkbox form bug using hidden field pattern and upgraded deal alert email with Georgia serif CRATE wordmark and accent bar.

## What Was Built

**Task 1 — notify_email checkbox bug fix (FIX-05)**

HTML checkboxes do not submit any value when unchecked. FastAPI's `bool = Form(True)` default meant an unchecked box was indistinguishable from an absent field, so `notify_email` always defaulted to `True`.

Fix: changed both `add_wishlist_item_web` and `edit_wishlist_item_web` routes to accept `notify_email: str = Form("")`. A hidden `<input type="hidden" name="notify_email" value="">` was added before each checkbox in all three form locations (add modal in index.html, edit modal in index.html, edit modal in item_detail.html). The string value is converted to bool via explicit allowlist: `notify_email.lower() in ("on", "true", "1", "yes")`.

**Task 2 — Email template branding update (FIX-04)**

Updated `templates/deal_alert.html`:
- Header CRATE wordmark: changed from 12px sans-serif to 24px Georgia serif with 8px letter-spacing
- Added a 40×2px white accent bar divider under the wordmark
- Item name `<h1>` changed from system sans-serif to Georgia serif
- Footer: added CRATE wordmark in 14px Georgia serif with 4px letter-spacing above the footer note

All table cell, label, and body text remains in `Arial,Helvetica,sans-serif` for readability.

## Commits

| Hash | Message |
|------|---------|
| 423b6cf | fix(12-02): fix notify_email checkbox bug with hidden field pattern |
| c38a5d9 | feat(12-02): update deal alert email with CRATE branding and serif font |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None. The notify_email string parsing uses an explicit allowlist (T-12-02 mitigation applied). Email template uses only inline styles and text (T-12-03 accepted).

## Self-Check: PASSED

- `app/routers/wishlist.py` — modified, `notify_email: str = Form("")` present twice, `notify_email_bool` present 4 times
- `templates/index.html` — 2 hidden field occurrences confirmed
- `templates/item_detail.html` — 1 hidden field occurrence confirmed
- `templates/deal_alert.html` — Georgia present 3 times, letter-spacing:8px present, width:40px accent bar present
- Commits 423b6cf and c38a5d9 exist in git log
