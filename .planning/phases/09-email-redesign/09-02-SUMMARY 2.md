---
phase: 09-email-redesign
plan: 02
subsystem: email
tags: [email, jinja2, plain-text, mime, notifier]
dependency_graph:
  requires: [templates/deal_alert.html]
  provides: [app/services/notifier.py updated, tests/test_email.py]
  affects: [app/services/notifier.py]
tech_stack:
  added: [pytest]
  patterns: [Jinja2 Environment with autoescape, MIMEMultipart alternative, HTML-to-plaintext stripping]
key_files:
  created: [tests/test_email.py]
  modified: [app/services/notifier.py]
decisions:
  - "Jinja2 Environment created at module level with autoescape=True for XSS prevention (T-09-01)"
  - "Plain-text part attached before HTML part in MIMEMultipart alternative per RFC 2046 ordering"
  - "Subject line updated from [Vinyl Wishlist] to [CRATE] to match brand identity"
  - "test_html_to_plaintext_table_rows uses two-row input to verify newline separation (single row strips trailing newline)"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-07"
  tasks_completed: 2
  files_created: 1
  files_modified: 1
---

# Phase 9 Plan 2: Wire Jinja2 Rendering into Notifier Summary

**One-liner:** notifier.py now renders deal_alert.html via Jinja2 with autoescape, computes all 8 template variables from live data, and sends dual MIME parts (plain-text + HTML) for broad email client compatibility.

## What Was Built

### Task 1: Jinja2 rendering + plain-text fallback (app/services/notifier.py)

- **`_email_env`** — module-level `jinja2.Environment` with `FileSystemLoader("templates")` and `autoescape=True`. Autoescape ensures all user-supplied data (item query, listing titles) is HTML-escaped at render time per T-09-01.
- **`_html_to_plaintext()`** — strips HTML tags via regex, converts `<br>`, `</tr>`, `</td>` to whitespace/separators, decodes common HTML entities, and collapses runs of blank lines. Produces readable plain-text fallback from any rendered email HTML.
- **`send_deal_email()`** — rewritten to compute all 8 template variables (`item_name`, `item_type`, `best_landed_price`, `pct_below_typical`, `has_typical_price`, `listings`, `item_url`, `notify_below_pct`) from `WishlistItem` and `Listing` ORM objects, then render `deal_alert.html` via Jinja2. Function signature unchanged.
- **`_send_smtp()`** — updated to attach plain-text part first, HTML part second in `MIMEMultipart("alternative")`. RFC 2046 ordering ensures text-only clients receive plain text; HTML-capable clients receive the rich template.
- **`_landed()`, `compute_typical_price()`, `should_notify()`** — unchanged.

### Task 2: Email tests (tests/test_email.py)

7 pytest tests:

| Test | What it covers |
|------|----------------|
| `test_html_to_plaintext_strips_tags` | Tags removed, text preserved, no `<`/`>` in output |
| `test_html_to_plaintext_table_rows` | Multi-row tables produce newline-separated output |
| `test_template_renders_without_error` | Jinja2 renders deal_alert.html without exception |
| `test_template_inline_css_colors` | `#0a0a0a`, `#111111`, `#f5f5f5` present; no `var(--)` |
| `test_template_data_in_output` | item_name, best_landed_price, listing title in output |
| `test_template_mso_conditional` | `[if mso]` present for Outlook compatibility |
| `test_template_footer_link` | "View on CRATE" and item_url present in footer |

All 7 pass.

## Decisions Made

1. **`autoescape=True`** — Jinja2 Environment at module level with autoescaping enabled. Satisfies T-09-01 (injection mitigation flagged in Plan 01 SUMMARY) without requiring manual `html.escape()` calls in the template render callsite.
2. **Plain-text before HTML in MIME** — RFC 2046 §5.1.4 states the last attachment is the preferred version. Email clients pick the last format they can render. Attaching plain-text first, HTML last means HTML-capable clients show the designed template; fallback clients show readable text.
3. **Subject updated to `[CRATE]`** — Brand name used consistently in template header and subject line (per CONTEXT.md D-06 brand identity).
4. **pytest installed into project venv** — `pytest` was not in `requirements.txt`. Installed via `venv/bin/pip install pytest` for test execution. Adding to requirements.txt is deferred (test-only dependency, not needed for runtime).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Single-row plaintext test produced no newline after strip()**
- **Found during:** Task 2 test execution
- **Issue:** `_html_to_plaintext` converts `</tr>` to `\n` but then strips trailing whitespace. A single-row input `<tr>...</tr>` produced `A | B |` with no newline after `.strip()`. Original test `assert "\n" in result` failed.
- **Fix:** Changed test to use two-row input `<tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr>` so the newline between rows is preserved after strip.
- **Files modified:** `tests/test_email.py`
- **Commit:** b53646c

## Known Stubs

None — all template variables are computed from live ORM data in `send_deal_email()`.

## Threat Flags

None — T-09-01 (injection) was resolved in this plan by adding `autoescape=True` to `_email_env`. No new surfaces introduced.

## Verification

```
PASS: python3 -m pytest tests/test_email.py -v — 7 passed
PASS: notifier.py structure validated (all 6 functions present, autoescape=True, deal_alert.html reference)
PASS: send_deal_email() signature unchanged
PASS: _landed(), compute_typical_price(), should_notify() unchanged
```

## Self-Check: PASSED

- `app/services/notifier.py` exists and passes ast.parse() validation
- `tests/test_email.py` exists with 7 test functions
- Commit `aa5831e` exists: `feat(09-02): wire Jinja2 rendering into notifier and add plain-text fallback`
- Commit `b53646c` exists: `test(09-02): add email rendering and plain-text fallback tests`
