---
phase: 11-ui-fixes
plan: "03"
subsystem: frontend
tags: [bug-fix, ux, css, templates]
dependency_graph:
  requires: ["11-01"]
  provides: ["skeleton-loading", "bug-01-fix", "placeholder-image"]
  affects: ["templates/index.html", "templates/item_detail.html", "static/style.css"]
tech_stack:
  added: []
  patterns: ["CSS skeleton animation", "onload/onerror progressive enhancement"]
key_files:
  created:
    - static/empty-vinyl-placeholder.png
  modified:
    - static/style.css
    - templates/index.html
    - templates/item_detail.html
decisions:
  - "Toast repositioned to bottom:80px (above scan panel height) with z-index:55 — avoids overlap at all viewport widths without JS"
  - "Skeleton wrapper uses aspect-ratio:1/1 on dashboard cards; detail page overrides with explicit px dimensions"
  - "Page reload kept after post-add polling — partial DOM updates out of scope; image cache-bust added before reload"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  files_changed: 4
---

# Phase 11 Plan 03: BUG-01 Fix + Image Skeleton + Placeholder Summary

**One-liner:** Fixed toast/scan-panel overlap with CSS repositioning, added skeleton pulse loading for all card artwork, and swapped in a new vinyl placeholder image.

## What Was Built

### Task 1: BUG-01 Fix + Default Album Type + Placeholder Image

- **BUG-01 (D-15):** `.toast` CSS changed from `bottom: var(--space-lg)` to `bottom: 80px` and `z-index: 50` to `z-index: 55`. The scan panel pill sits at `bottom: var(--space-md)` (~16px) with a ~44px height, so 80px clears it at all viewport widths without JavaScript.
- **Default album type (D-18):** Added `selected` attribute to `<option value="album">` in the add-item modal form. Explicit default prevents browser-dependent selection behaviour.
- **New placeholder (D-07):** Copied `empty vinyl image.png` from project root to `static/empty-vinyl-placeholder.png`. Dashboard cards with no artwork now use this image; SVG fallback retained on `onerror`.

### Task 2: Image Skeleton Loading + Post-Add Image Refresh

- **Skeleton CSS (D-16):** Added `@keyframes skeleton-pulse` with a 200%-width gradient shimmer and `.card-artwork-wrapper` / `.card-artwork-wrapper.loaded` classes. Wrapper animates until `loaded` class is toggled.
- **Dashboard skeleton:** All card artwork wrapped in `<div class="card-artwork-wrapper">`. Images start at `opacity: 0`; `onload` adds `.loaded` to both image and wrapper, stopping animation and fading in.
- **Detail page skeleton:** 120×120 thumbnail wrapped in same skeleton wrapper with explicit `width/height` override and `aspect-ratio: unset` to avoid conflicting with the fixed-size container.
- **Post-add image refresh:** Polling block in `index.html` now busts the artwork cache (`?t=timestamp`) before `window.location.reload()` when `data.artwork_url` is present.

## Decisions Made

1. **Toast at `bottom: 80px` (not `calc`)** — Absolute value is more predictable than a `calc` expression that depends on `--space-md` (16px) + assumed pill height. 80px leaves ~20px clearance above a 44px pill at 16px bottom.
2. **`aspect-ratio: unset` on detail page wrapper** — The wrapper class sets `aspect-ratio: 1/1` for dashboard square cards; the detail thumbnail uses explicit `width: 120px; height: 120px` so the ratio must be unset to avoid layout conflict.
3. **Page reload kept after image cache-bust** — Full reload is the simplest way to refresh price data alongside artwork; partial DOM update would require a separate API response shape, out of scope for this plan.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all changes are functional and wired to real data.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes introduced. Artwork URL passthrough via existing `/api/artwork` proxy is unchanged.

## Self-Check: PASSED

| Item | Status |
|------|--------|
| static/style.css | FOUND |
| templates/index.html | FOUND |
| templates/item_detail.html | FOUND |
| static/empty-vinyl-placeholder.png | FOUND |
| .planning/phases/11-ui-fixes/11-03-SUMMARY.md | FOUND |
| commit 0a1f090 (Task 1) | FOUND |
| commit fc976c7 (Task 2) | FOUND |
