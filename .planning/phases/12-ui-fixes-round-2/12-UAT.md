---
status: diagnosed
phase: 12-ui-fixes-round-2
source: [12-01-SUMMARY.md, 12-02-SUMMARY.md]
started: 2026-04-11T23:10:00Z
updated: 2026-04-11T23:25:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Inter Font Applied
expected: All UI text (card titles, prices, labels, body text) renders in Inter font. CRATE logo still uses serif display font.
result: pass

### 2. Ghost Card Readability
expected: Cards with no listings appear semi-transparent but still readable — not washed out to near-invisible.
result: pass

### 3. Consistent Price Sizing
expected: All prices on cards (both deal and non-deal) display at the same 28px size. No price should appear smaller than another.
result: pass

### 4. Card Titles Enlarged
expected: Album names on cards are visibly larger than body text (18px) — noticeable but not oversized.
result: pass

### 5. Toast Without Tick Icon
expected: When an action triggers a toast notification (e.g. adding an item), the toast shows only text — no checkmark/tick icon.
result: issue
reported: "yes, but there is still a random box floating in the bottom right"
severity: cosmetic

### 6. Notify Email Checkbox Works
expected: Edit a wishlist item, uncheck the "Notify" email checkbox, save. Re-open the edit modal — the checkbox should remain unchecked. Previously it always reverted to checked.
result: pass

### 7. Deal Alert Email Branding
expected: Deal alert email shows CRATE wordmark in serif font with letter-spacing at the top, a white accent bar divider, and item name in serif font. Body text remains sans-serif.
result: issue
reported: "The item name should not be in a different font. Also the CRATE title should be in the exact same font as the website header"
severity: cosmetic

## Summary

total: 7
passed: 5
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Toast shows only text with no extra visual artifacts"
  status: failed
  reason: "User reported: yes, but there is still a random box floating in the bottom right"
  severity: cosmetic
  test: 5
  root_cause: ".toast CSS has display:flex as default state — element is visible even when idle because .hidden class is not reliably applied"
  artifacts:
    - path: "static/style.css"
      issue: ".toast missing display:none default"
  missing:
    - "Add display:none to .toast rule; JS show function should set display:flex when triggered"

- truth: "Deal alert email uses consistent fonts — item name in sans-serif, CRATE wordmark matches website header font"
  status: failed
  reason: "User reported: The item name should not be in a different font. Also the CRATE title should be in the exact same font as the website header"
  severity: cosmetic
  test: 7
  root_cause: "Phase 12-02 changed item h1 and CRATE wordmark to Georgia serif. User wants item name in sans-serif and CRATE to match website header (Bodoni Moda via --font-display). Bodoni Moda is not email-safe — need closest email-safe serif fallback for CRATE only."
  artifacts:
    - path: "templates/deal_alert.html"
      issue: "Georgia applied to item h1 (line 60), CRATE header (line 34), CRATE footer (line 130)"
  missing:
    - "Revert item h1 to sans-serif stack"
    - "Keep CRATE wordmark in serif but document email font limitation"
