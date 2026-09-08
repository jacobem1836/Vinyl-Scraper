---
status: complete
phase: 21-bug-fixes
source: 21-01-SUMMARY.md
started: 2026-04-19T00:30:00Z
updated: 2026-04-19T01:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Typeahead spinner clears on result select
expected: Type in the Add Item search field to trigger typeahead results. Click (or keyboard-select) one of the dropdown results. The loading spinner disappears immediately — it does not linger after selection.
result: pass

### 2. Typeahead spinner clears on type dropdown change
expected: Type enough to trigger typeahead (spinner appears). While the spinner/dropdown is visible, change the type dropdown (album → artist or similar). The spinner hides immediately when the type changes.
result: pass

### 3. Image skeleton uses diagonal dark shimmer
expected: Open the dashboard while images are loading (or on a slow connection). The artwork placeholder shows a diagonal top-left → bottom-right sweep shimmer — not a horizontal pulse or glow. The shimmer background is visibly dark (#0a0a0a / #141414), matching the true-black card surface.
result: pass
notes: "Redesigned — replaced shimmer with vinyl placeholder + opacity pulse per user request"

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
