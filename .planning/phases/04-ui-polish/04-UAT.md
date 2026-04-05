---
status: resolved
phase: 04-ui-polish
source: [04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md]
started: 2026-04-04T00:00:00Z
updated: 2026-04-04T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. CRATE branding in nav and tab title
expected: Open the dashboard. The browser tab title reads "Dashboard · CRATE". The nav bar shows "CRATE" as the brand name (not "Vinyl Wishlist" or any other name). All references to the old name are gone.
result: pass

### 2. Near-black palette and white accent
expected: The dashboard background is very dark (near-black, ~#0a0a0a). Cards/surfaces are a slightly lighter dark (~#111111). Accent elements (buttons, links, highlights) are white — no amber/gold/orange tones visible anywhere.
result: pass

### 3. Sharp card edges
expected: Cards on the dashboard have perfectly sharp (square) corners — no rounded edges. Buttons have very minimal rounding (2px or less). No visible border-radius on any card or modal element.
result: pass

### 4. Compressed card grid spacing
expected: Cards in the dashboard grid are packed tighter than before — smaller gaps between cards (~12px), and card content has tighter padding (~12px) rather than the larger spacing from before.
result: pass

### 5. Empty state copy
expected: When the wishlist is empty, the heading reads "Your crate is empty" (not "Your wishlist is empty" or similar).
result: pass

### 6. Item detail page — CRATE copy and artwork
expected: On an item's detail page, the delete button reads "Remove from Crate" and the confirmation prompt says "Remove this item from your crate?". The album artwork image has square corners (no border-radius). The page title shows "CRATE — [item name]".
result: pass

### 7. High-res Discogs artwork on new scan
expected: Add a new item (or rescan an existing one with no artwork_url). After the scan completes, the artwork shown is a full-resolution cover image from Discogs (not a small thumbnail). Note: existing items with artwork already set won't change until rescanned.
result: issue
reported: "Scanning crashes with UNIQUE constraint failed: listings.url (IntegrityError on INSERT). Also images are still low res."
severity: blocker

## Summary

total: 7
passed: 6
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "Scanning completes without error; existing listings are updated in-place rather than re-inserted"
  status: resolved
  reason: "User reported: UNIQUE constraint failed: listings.url — scanner attempts to INSERT a listing whose URL already exists in the DB instead of skipping or updating it"
  severity: blocker
  test: 7
  resolved_by: 04-03
  root_cause: |
    DB UNIQUE constraint on `listings.url` is global (url alone), but scanner dedup logic at scanner.py:46-55
    filters by (wishlist_item_id + url). When the same store URL (e.g. dutchvinyl) appears in results for
    two different wishlist items, the dedup check finds no existing row for that item, proceeds to INSERT,
    and the global unique constraint fires. Fix: change the constraint to UNIQUE(wishlist_item_id, url).
  artifacts: [app/models.py, app/services/scanner.py]
  missing: []

- truth: "After scan, artwork displayed is full-resolution Discogs cover image (not thumbnail)"
  status: resolved
  reason: "User reported: images are still low res after scan"
  severity: major
  test: 7
  resolved_by: 04-03
  root_cause: |
    scanner.py:30 skips artwork update entirely if item.artwork_url is already set (`if not item.artwork_url`).
    Existing items have old thumbnail URLs from previous scans. The high-res discogs.py change only applies
    to items whose artwork_url is currently NULL. Fix: remove the guard — always overwrite artwork_url with
    the newly fetched cover_uri on each scan.
  artifacts: [app/services/scanner.py]
  missing: []
