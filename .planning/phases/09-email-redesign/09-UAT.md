---
status: testing
phase: 09-email-redesign
source: [09-01-SUMMARY.md, 09-02-SUMMARY.md]
started: 2026-04-07T22:50:00Z
updated: 2026-04-07T22:50:00Z
---

## Current Test

number: 1
name: Deal Alert Email Renders with CRATE Dark Branding
expected: |
  Trigger a deal alert email (or render the template manually). The email should display a dark background (#0a0a0a / #111111), the CRATE wordmark header, the item name with a type badge, the best landed price in large text, and the percentage below typical price in green (#34d399).
awaiting: user response

## Tests

### 1. Deal Alert Email Renders with CRATE Dark Branding
expected: Trigger a deal alert email (or render the template manually). The email should display a dark background (#0a0a0a / #111111), the CRATE wordmark header, the item name with a type badge, the best landed price in large text, and the percentage below typical price in green (#34d399).
result: [pending]

### 2. Listing Table Shows Deal Details
expected: The email body contains a table with columns for Title, Landed Price (AUD), Source, and Ships From. Each listing row displays the correct data for matched deals.
result: [pending]

### 3. Footer Contains "View on CRATE" Link
expected: The email footer has a single centered "View on CRATE" button/link. No per-listing links are present. The link points to the item's dashboard page.
result: [pending]

### 4. Email Subject Line Shows [CRATE] Prefix
expected: The email subject line starts with "[CRATE]" instead of the old "[Vinyl Wishlist]" prefix.
result: [pending]

### 5. Plain-Text Fallback is Readable
expected: Viewing the email as plain text (or in a text-only client) shows a readable version with item name, prices, and listing details — no HTML tags visible.
result: [pending]

### 6. Outlook/MSO Conditional Fallback
expected: The HTML source contains `<!--[if mso]>` conditional comments that force white background with dark text for Outlook's Word-rendering engine.
result: [pending]

### 7. Jinja2 Autoescape Prevents Injection
expected: If an item name contains HTML characters (e.g. `<script>` or `&`), they are escaped in the rendered email output — no raw HTML injection possible.
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0
blocked: 0

## Gaps

[none yet]
