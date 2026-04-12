---
phase: 12-ui-fixes-round-2
plan: "01"
subsystem: frontend
tags: [css, html, typography, font, ui-polish]
dependency_graph:
  requires: []
  provides: [inter-font, ghost-card-fix, consistent-price-sizing, scrollbar-fix, title-size-fix, tick-icon-removed]
  affects: [static/style.css, templates/base.html, templates/index.html]
tech_stack:
  added: ["Inter variable font (woff2)"]
  patterns: ["CSS custom property overrides", "font-face self-hosting"]
key_files:
  created: ["static/fonts/Inter-VariableFont_opsz,wght.woff2"]
  modified: ["static/style.css", "templates/base.html", "templates/index.html"]
decisions:
  - "Used Inter v4.1 InterVariable.woff2 (renamed to match Google Fonts convention) rather than a static weight"
  - "Firefox scrollbar changed from * selector to html to avoid cascade conflicts"
  - "Removed conditional has_deal price branching — unified all prices to card-price class"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  files_changed: 3
---

# Phase 12 Plan 01: Visual Polish Fixes — FIX-01, FIX-02, FIX-03, FIX-06, FIX-07, FIX-08 Summary

**One-liner:** Six UI fixes applied — Inter font self-hosted, ghost card opacity raised, price sizing unified, tick icon removed, Firefox scrollbar scoped to html, card titles enlarged to 18px.

## What Was Built

Six visual regressions and polish issues from the Phase 11 review were fixed across two files.

### FIX-01: Ghost card readability

`.card--empty` opacity raised from `0.35` to `0.55`. Items with no listings are now readable while still visually distinct from active cards.

### FIX-02: Consistent price sizing

Removed the `{% if has_deal %}` / `{% else %}` branching for price display in `index.html`. Both deal and non-deal prices now use `class="card-price price-best"`, mapping to `--text-price: 28px`. A new `.card-price` utility class was added to `style.css` alongside `.text-price`.

### FIX-03: Font overhaul — Inter as primary UI font

- Added `@font-face` block for Inter variable font (100–900 weight range, `font-display: swap`)
- `--font-sans` updated to `"Inter", -apple-system, BlinkMacSystemFont, ...`
- `<link rel="preload">` added to `base.html` for the Inter woff2 file
- Font file (`Inter-VariableFont_opsz,wght.woff2`) downloaded from rsms/inter v4.1 and stored at `static/fonts/`
- Bodoni Moda remains the `--font-display` for the CRATE logo — unchanged

### FIX-06: Tick icon removed

SVG checkmark element (`M5 13l4 4L19 7` path) removed from the `#toast` div in `base.html`. Toast now shows only the text message span.

### FIX-07: Scrollbar scoped to html

Firefox scrollbar rule changed from `* { scrollbar-width: thin; ... }` to `html { scrollbar-width: thin; ... }`. The `*` selector was too broad and could conflict with inner scrollable containers.

### FIX-08: Card titles enlarged

`--text-title` increased from `16px` to `18px`. Card album names are now noticeably larger than body text while remaining subordinate to artwork.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | CSS token and component fixes | 456f64c | static/style.css, static/fonts/Inter-VariableFont_opsz,wght.woff2 |
| 2 | Template fixes | 0ce30dd | templates/base.html, templates/index.html |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written with one minor adaptation:

**Adaptation: Font filename**
- The Inter v4.1 release zip contains `InterVariable.woff2`, not `Inter-VariableFont_opsz,wght.woff2` (Google Fonts naming)
- File was copied with the plan's expected name to maintain consistency with the `@font-face` and preload references
- No behavior difference

## Known Stubs

None. All fixes are fully wired.

## Threat Flags

None. No new network endpoints, auth paths, or trust boundaries introduced. Font file is a static asset served locally from the official rsms/inter release.

## Self-Check: PASSED

- [x] `static/style.css` — exists and contains all six changes
- [x] `static/fonts/Inter-VariableFont_opsz,wght.woff2` — exists (downloaded)
- [x] `templates/base.html` — Inter preload present, tick SVG absent
- [x] `templates/index.html` — `card-price price-best` class used, no conditional price sizing
- [x] Commit `456f64c` — CSS + font changes
- [x] Commit `0ce30dd` — template changes
- [x] Python syntax check: `python3 -m py_compile app/main.py` passed
