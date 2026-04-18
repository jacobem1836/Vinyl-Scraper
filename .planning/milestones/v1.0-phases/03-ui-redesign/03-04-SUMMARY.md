---
phase: 03-ui-redesign
plan: "04"
subsystem: templates
tags: [ui, jinja2, css, dashboard, detail-page]
dependency_graph:
  requires: [03-01, 03-02, 03-03]
  provides: [redesigned-dashboard, redesigned-detail-page]
  affects: [templates/index.html, templates/item_detail.html]
tech_stack:
  added: []
  patterns: [album-art-card-grid, aud-landed-cost-display, css-design-system-classes]
key_files:
  created: []
  modified:
    - templates/index.html
    - templates/item_detail.html
decisions:
  - Cards are pure <a> tags (no edit button on card face); edit accessible from detail page only (D-05)
  - Best deals grid reuses .card-grid (4-col at desktop) — 4 columns is acceptable for 3 items
  - aud_total shown when available; falls back to landed_price + currency label when FX fetch failed (Open Q3 resolution)
metrics:
  duration_seconds: 112
  completed_date: "2026-04-03T01:32:37Z"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
---

# Phase 03 Plan 04: Dashboard and Detail Page Redesign Summary

Rewrote both Jinja2 templates — Spotify-style album art card grid dashboard and redesigned detail page with AUD landed costs — removing all Tailwind utility classes in favour of the CSS design system from plan 01.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Rewrite index.html — album art card grid dashboard | 722f3cf | templates/index.html |
| 2 | Rewrite item_detail.html — artwork header + AUD landed costs | 33ea4d9 | templates/item_detail.html |

## What Was Built

**index.html:** Stats bar at top (item count, listing count, total cost). Album art card grid using `.card-grid` / `.card` / `.card-artwork` classes. Each card is an `<a>` tag linking to `/item/{id}`. Artwork loaded via `/api/artwork?url=` proxy with `vinyl-placeholder.svg` fallback. Card body shows title and best AUD price only (no listing count or timestamp per D-04). Scanning state uses `.card--scanning` animation and `data-scanning="true"` polling. Add Item and Edit Item modals fully restyled with `.modal-overlay` / `.modal-panel` / `.form-input` / `.btn-cta` classes.

**item_detail.html:** Header section with 120x120 artwork thumbnail (same proxy + fallback pattern). Title, type badge, notes, notify threshold, last-scanned displayed. `Scan Now` (`.btn-cta`) and `Delete` (`.btn-destructive`) action buttons. Best Deals section reuses `.card-grid`. All Listings table uses `.table-container` / `.table` / `.listing-row` classes. Landed (AU) column shows `aud_total` prominently in amber with `orig_display` as muted sub-text below; falls back to `landed_price` + currency label when `aud_total` is None. Delete confirmation text updated to "Remove this item from your wishlist?".

## Decisions Made

- Cards are pure `<a>` tags (no edit button on card face). Edit is accessible from the detail page only, keeping the card as a clean artwork tile (per D-05 and RESEARCH.md Open Question 1).
- Best Deals grid reuses `.card-grid` (4 columns at 1280px+). For the typical 3 top listings this leaves one empty cell — acceptable, avoids introducing a new modifier class.
- `aud_total` fallback: when FX fetch failed and `aud_total` is None, show `landed_price` with `listing.currency` prefix. This ensures the price column is never blank (resolves RESEARCH.md Open Question 3).

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. Both `aud_total` and `orig_display` are wired to the listing dicts produced by plan 03-03 (FX service). Artwork proxy from plan 03-02. CSS classes from plan 03-01. All data flows are live.

## Self-Check: PASSED
