---
status: complete
phase: 21-bug-fixes
source: 21-01-SUMMARY.md
started: 2026-04-19T00:30:00Z
updated: 2026-04-19T00:35:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Typeahead spinner clears on result select
expected: Type in the Add Item search field to trigger typeahead results. Click (or keyboard-select) one of the dropdown results. The loading spinner disappears immediately — it does not linger after selection.
result: issue
reported: "its still there"
severity: major

### 2. Typeahead spinner clears on type dropdown change
expected: Type enough to trigger typeahead (spinner appears). While the spinner/dropdown is visible, change the type dropdown (album → artist or similar). The spinner hides immediately when the type changes.
result: issue
reported: "no, it never hides"
severity: major

### 3. Image skeleton uses diagonal dark shimmer
expected: Open the dashboard while images are loading (or on a slow connection). The artwork placeholder shows a diagonal top-left → bottom-right sweep shimmer — not a horizontal pulse or glow. The shimmer background is visibly dark (#0a0a0a / #141414), matching the true-black card surface.
result: issue
reported: "its still the light grey shimmer"
severity: major

## Summary

total: 3
passed: 0
issues: 3
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Spinner disappears immediately after selecting a typeahead result"
  status: failed
  reason: "User reported: its still there"
  severity: major
  test: 1
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "Spinner hides immediately when type dropdown changes while typeahead is open"
  status: failed
  reason: "User reported: no, it never hides"
  severity: major
  test: 2
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "Image skeleton shimmer is dark (#0a0a0a/#141414), diagonal, not light grey"
  status: failed
  reason: "User reported: its still the light grey shimmer"
  severity: major
  test: 3
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
