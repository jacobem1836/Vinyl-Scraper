---
status: complete
phase: 18-ui-consistency-fixes
source: 18-01-SUMMARY.md, 18-02-SUMMARY.md
started: 2026-04-18T00:00:00Z
updated: 2026-04-18T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Post-add scan panel does not appear
expected: Add a new item (via the Add Item modal or iOS Shortcut). After the redirect back to the dashboard, the scan panel / scan status box does NOT appear. You should only see the standard toast notification — not a boxed scanning UI.
result: issue
reported: "it appears higher and larger text. The toasts should all be processed the same way — same size and location as the Scanning n/N toast"
severity: major

### 2. Toast text uses em-dash separator
expected: After adding an item, the toast that appears reads "Item added — scanning in background" with an em-dash (—) between "added" and "scanning", not a comma. The toast appears in the standard toast location with standard toast styling.
result: pass

### 3. Item detail placeholder — no artwork
expected: Open an item detail page for a record that has no artwork. The placeholder image shown is the new empty vinyl PNG (a vinyl silhouette/ring image), not the old grey SVG placeholder that looked like a generic image icon.
result: pass

### 4. Item detail placeholder — broken image fallback
expected: If an item has an artwork URL that fails to load (broken link), the fallback shown is the same new empty vinyl PNG — not the old SVG. (You can test this by temporarily breaking a URL, or verify visually that any item with a failed image load shows the vinyl silhouette.)
result: pass

## Summary

total: 4
passed: 3
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Post-add toast renders at same size and location as the Scanning n/N toast — unified styling via #toast primitive"
  status: failed
  reason: "User reported: it appears higher and larger text. The toasts should all be processed the same way — same size and location as the Scanning n/N toast"
  severity: major
  test: 1
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
