---
status: partial
phase: 26-shopify-store-expansion
source: [26-VERIFICATION.md]
started: 2026-04-26T02:50:00.000Z
updated: 2026-04-26T02:50:00.000Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. All 11 suggest.json stores return listings without error
expected: Trigger a scan for a known album (e.g. "Radiohead In Rainbows"). All 11 suggest.json stores (6 original + 5 new: wax_museum, red_eye, rockaway, happy_valley, rare_records) return results or empty list with no error log lines.
result: [pending]

### 2. Heartland returns listings via products.json path
expected: Trigger a scan for an album stocked by Heartland (e.g. "Tough Town"). At least 1 listing is returned with `source='heartland'`, correct price/URL/title fields matching the canonical dict shape.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
