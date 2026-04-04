---
phase: 04-ui-polish
plan: "01"
subsystem: frontend
tags: [css, design-system, tokens, templates, rename]
dependency_graph:
  requires: []
  provides: [phase4-design-tokens, crate-branding, sharp-radius-system]
  affects: [static/style.css, templates/base.html, templates/index.html, templates/item_detail.html]
tech_stack:
  added: []
  patterns: [css-custom-properties, design-token-update]
key_files:
  modified:
    - static/style.css
    - templates/base.html
    - templates/index.html
    - templates/item_detail.html
decisions:
  - "Checked out Phase 3 files from gsd/phase-4-ui-polish branch — worktree was on an older commit without Phase 3 UI"
  - "Used literal 12px values for card-body/card-grid as per UI-SPEC; global --space-md remains 16px"
  - "Spinner border-radius: 50% preserved — functional geometry, not decorative"
metrics:
  duration: "~6 minutes"
  completed: "2026-04-04T02:41:19Z"
  tasks_completed: 2
  files_modified: 4
---

# Phase 4 Plan 01: CSS Design System + CRATE Rebrand Summary

Near-black neutral palette (#0a0a0a bg, #111111 surface), white accent (#ffffff replacing amber #f59e0b), sharp edges everywhere (--radius-card: 0px), and full CRATE rebrand across all Jinja2 templates.

## What Was Built

**Task 1 — CSS Design System (static/style.css)**

- Replaced all Phase 3 blue-tinted palette tokens with neutral near-black values (#0a0a0a, #111111, #222222)
- Replaced amber/gold accent (#f59e0b) with white (#ffffff) across all accent tokens
- Added `--radius-*` token group (--radius-card: 0px, --radius-modal: 0px, --radius-btn: 2px, --radius-badge: 2px, --radius-input: 2px)
- Updated all 13 hardcoded `border-radius` component values to use tokens or literal 0
- Preserved `border-radius: 50%` on `.spinner` (functional circular shape)
- Updated `.spinner` border colours from amber to white accent
- Updated `@keyframes pulse-border` stop colours from amber rgba to white rgba
- Updated `.nav-brand` rule: font-size 16px, font-weight 600, letter-spacing 0.25em, text-transform uppercase
- Compressed `.card-body` padding from `var(--space-md)` (16px) to `12px`
- Compressed `.card-grid` gap from `var(--space-lg)` (24px) to `12px`
- Updated card hover box-shadow to deeper `rgba(0,0,0,0.6)` against near-black background
- Updated file header comment to "CRATE"

**Task 2 — Template CRATE Rename (base.html, index.html, item_detail.html)**

- `base.html`: `<title>` default → "CRATE"; nav-brand link text → "CRATE"
- `index.html`: title block → "Dashboard · CRATE"; empty state heading → "Your crate is empty"
- `item_detail.html`: title block → "CRATE — {{ item.query }}"; delete form confirm → "Remove this item from your crate?"; delete button → "Remove from Crate"; both artwork img inline border-radius 8px → 0

## Verification Results

| Check | Result |
|-------|--------|
| No Phase 3 colours (#f59e0b, #0f172a, etc.) remain in style.css | PASS (0 matches) |
| `border-radius: 50%` on .spinner preserved | PASS |
| `letter-spacing: 0.25em` in .nav-brand | PASS |
| `rgba(255, 255, 255, 0.2)` in spinner/keyframe | PASS |
| `.card-body` padding 12px | PASS |
| `.card-grid` gap 12px | PASS |
| `--space-md: 16px` unchanged | PASS |
| No "Vinyl Wishlist" in templates/ | PASS |
| "Your crate is empty" in index.html | PASS |
| "Remove from Crate" in item_detail.html | PASS |
| No `border-radius: 8px` in item_detail.html | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Worktree lacked Phase 3 CSS and templates**
- **Found during:** Initial file reads (pre-execution)
- **Issue:** The worktree was on an older commit (Phase 1 infrastructure state). `static/style.css` was only 36 lines with no `:root` design system block. Templates were using Tailwind classes (`bg-amber-500`, `text-amber-400`) not the Phase 3 custom CSS classes.
- **Fix:** Checked out the four target files from the `gsd/phase-4-ui-polish` branch (which had the Phase 3 UI redesign applied) before making Phase 4 changes. `git checkout gsd/phase-4-ui-polish -- static/style.css templates/base.html templates/index.html templates/item_detail.html`
- **Files modified:** All four plan files
- **Commit:** 5b60230 (includes the Phase 3 baseline + Phase 4 changes in one commit)

## Commits

| Hash | Task | Description |
|------|------|-------------|
| 5b60230 | Task 1 | feat(04-01): update CSS design system — neutral palette, white accent, sharp edges, compressed spacing |
| 48b076f | Task 2 | feat(04-01): rename app to CRATE, update copy and inline styles in templates |

## Known Stubs

None — all token updates are wired to real CSS custom property consumers. All copy changes reference actual Jinja2 template text.

## Self-Check: PASSED

- `/Users/jacobmarriott/Documents/Personal/Vinyl-Scraper/.claude/worktrees/agent-acf62ed4/static/style.css` — FOUND
- `/Users/jacobmarriott/Documents/Personal/Vinyl-Scraper/.claude/worktrees/agent-acf62ed4/templates/base.html` — FOUND
- `/Users/jacobmarriott/Documents/Personal/Vinyl-Scraper/.claude/worktrees/agent-acf62ed4/templates/index.html` — FOUND
- `/Users/jacobmarriott/Documents/Personal/Vinyl-Scraper/.claude/worktrees/agent-acf62ed4/templates/item_detail.html` — FOUND
- Commit 5b60230 — FOUND
- Commit 48b076f — FOUND
