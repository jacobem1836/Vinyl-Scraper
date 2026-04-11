---
phase: 10-ui-polish
plan: 02
subsystem: frontend-templates
tags: [ui, templates, typography, card-tiers, accessibility]
dependency_graph:
  requires: [10-01]
  provides: [card-tier-ui, deal-badges, stats-bar-upgrade, disabled-scan-buttons, h2-tokens, delete-copy, typeahead-copy]
  affects: [templates/index.html, templates/item_detail.html, templates/base.html, static/typeahead.js]
tech_stack:
  added: []
  patterns: [jinja2-conditional-classes, css-token-references, data-attribute-selectors]
key_files:
  created: []
  modified:
    - templates/index.html
    - templates/item_detail.html
    - templates/base.html
    - static/typeahead.js
decisions:
  - "card--empty applied to both no_listings and is_scanning states as plan specified"
  - "text-sm in JS template strings (renderStatus innerHTML) replaced with inline style attributes"
metrics:
  duration_minutes: 35
  completed_date: "2026-04-08"
  tasks_completed: 3
  tasks_total: 3
  files_modified: 4
requirements: [UIP-02, UIP-03, UIP-06, UIP-08, UIP-10]
---

# Phase 10 Plan 02: Template Token Wiring Summary

Templates wired to Plan 01 design tokens — card tiers, deal badges, stats bar with large values/small labels, H2 token classes, disabled scan buttons, updated delete/typeahead copy, zero `text-sm` references remaining.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Card tiers, deal badges, stats bar | 507644d | templates/index.html |
| 2 | Card titles, text-sm cleanup, typeahead copy | 62cd561 | templates/index.html, static/typeahead.js |
| 3 | H2 tokens, disabled scan buttons, delete copy, text-sm cleanup | f270e47 | templates/item_detail.html, templates/base.html |

## What Was Built

### Task 1 — Card tiers and stats bar (index.html)

- Added `has_deal` Jinja2 set statement: computes deal percentage from `item.typical_price` and `item.best_price` against `item.notify_below_pct`
- Added `no_listings` set statement: items that have been scanned but found nothing
- Card `<a>` class now conditionally applies `card--deal`, `card--empty`, `card--scanning`
- Deal badge (`card-deal-badge`) injected above `card-body` with computed `-XX%` discount
- Deal price uses `text-price` class (28px); non-deal price uses `font-size: var(--text-body)`
- Stats bar replaced: values at `var(--text-subheading)` weight 700, labels at `var(--text-label)` in `--color-text-faint`
- Scan All button has `data-scan-btn` attribute for JS disabled toggling

### Task 2 — Card title sizing and copy (index.html, typeahead.js)

- Card `<h3>` changed from `class="text-sm"` with inline weight to `class="text-title"` (21px/500)
- Modal headings font-weight updated from 600 to 700
- Checkbox labels: `text-sm text-muted` replaced with `text-muted` + `font-size: var(--text-label)`
- Typeahead no-results message: "No results for..." → "Nothing matched — try a different title or artist"
- Zero `text-sm` class references remain in index.html

### Task 3 — Detail page and base (item_detail.html, base.html)

- "Best Deals" H2: `style="font-size: 22px"` → `class="text-subheading"` (22px/700 via CSS)
- "All Listings" H2: `style="font-size: 22px"` → `style="font-size: var(--text-heading-secondary); font-weight: 400;"` (21px/400)
- Scan Now button: added `data-scan-btn` attribute
- Delete confirmation copy: "Confirm?" → "Confirm Delete", "Cancel" → "Keep Record"
- `startScan()`: disables all `[data-scan-btn]` elements on call; re-enables on scan-not-started or error
- `renderStatus()`: re-enables all `[data-scan-btn]` elements when scan completes
- Landed (AU) table `<th>` and `<td>` have `class="col-landed"` for right-alignment
- All `text-sm` references removed from both files; replaced with inline `font-size: var(--text-label)` or `var(--text-body)` as appropriate

## Deviations from Plan

### Minor Adjustments

**1. [Rule 2 - Missing] text-sm in JS innerHTML strings (base.html)**
- **Found during:** Task 3
- **Issue:** Plan specified removing `text-sm` from HTML elements but the JS `renderStatus` function builds innerHTML strings also containing `text-sm` classes
- **Fix:** Replaced `class="text-sm text-muted"` in innerHTML template strings with `class="text-muted" style="font-size:var(--text-label)"`
- **Files modified:** templates/base.html

**2. [Rule 2 - Missing] scanSummary div had text-sm**
- **Found during:** Task 3
- **Issue:** `<div id="scanSummary" class="hidden text-sm text-success">` — not covered explicitly in plan's text-sm list
- **Fix:** Changed to `class="hidden text-success"` with `style="font-size: var(--text-label); font-weight:600"`
- **Files modified:** templates/base.html

## Phase 5 Carry-Forwards Verified

- `role="dialog"` and `aria-modal="true"` present on `editItemModal` in item_detail.html (UIP-07)
- Delete confirmation uses JS `onclick` toggle, not `confirm()` (UIP-08)
- Scan panel and delete confirmation do not overlap — different z-layers/positions (BUG-01)

## Known Stubs

None — all template changes wire to real data from the router's enriched item dict (`best_price`, `typical_price`, `listing_count`, `notify_below_pct`).

## Threat Flags

None — all deal percentage computation uses server-provided floats; Jinja2 auto-escaping handles XSS. No new network endpoints or auth paths introduced.

## Self-Check: PASSED

- FOUND: templates/index.html
- FOUND: templates/item_detail.html
- FOUND: templates/base.html
- FOUND: static/typeahead.js
- FOUND: .planning/phases/10-ui-polish/10-02-SUMMARY.md
- FOUND commit: 507644d (Task 1)
- FOUND commit: 62cd561 (Task 2)
- FOUND commit: f270e47 (Task 3)
