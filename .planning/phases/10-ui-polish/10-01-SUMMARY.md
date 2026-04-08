---
phase: 10
plan: 01
subsystem: frontend/css
tags: [css, design-tokens, typography, spacing, cards, buttons, table, typeahead]
dependency_graph:
  requires: []
  provides: [design-tokens-D07, spacing-tiers-D08, card-tier-classes-D09, disabled-button-state, table-cleanup-D11, spinner-fix]
  affects: [static/style.css]
tech_stack:
  added: []
  patterns: [CSS custom properties, semantic token reassignment, card modifier classes]
key_files:
  created: []
  modified:
    - static/style.css
decisions:
  - "Added 8 typography tokens (D-07 + D-04): --text-label 12px, --text-sm 14px (compat), --text-body 16px, --text-title 21px, --text-price 28px, --text-heading 36px, --text-subheading 22px, --text-heading-secondary 21px"
  - "Component rules reassigned to semantically correct tokens: buttons -> text-body, form-label/badge/typeahead-empty/typeahead-pin-badge -> text-label, table -> text-body"
  - "D-13 monospace font (JetBrains Mono) skipped — design tools unavailable in worktree per plan notes"
  - "Table td border-top removed per D-11; padding set to 10px space-md"
  - ".col-landed right-aligned; .col-price skipped — no template element uses it"
metrics:
  duration_seconds: 240
  completed_date: "2026-04-08"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 1
---

# Phase 10 Plan 01: CSS Design System Overhaul Summary

CSS design system tokens and component rules updated to implement the full D-07 7-token type scale, D-08 3-tier spacing hierarchy, D-09 card tier classes, D-05 disabled button state, D-11 table border cleanup, and typeahead spinner animation fix.

## What Was Built

All downstream template changes in Plan 02 can now reference the new tokens and tier modifier classes.

**Task 1 — Design tokens and typography helpers (commit 0b06a97)**

- Added 8 CSS custom properties to `:root` per D-07 full 7-token set (plus `--text-subheading` for D-04):
  - `--text-label: 12px` (new)
  - `--text-sm: 14px` (preserved for backward compat)
  - `--text-body: 16px` (unchanged)
  - `--text-title: 21px` (new)
  - `--text-price: 28px` (was 20px)
  - `--text-heading: 36px` (was 28px)
  - `--text-subheading: 22px` (new — D-04)
  - `--text-heading-secondary: 21px` (new)
- Applied D-08 spacing tiers: `.card-grid` gap changed from `--space-sm` (8px) to `--space-md` (16px); `.stack-lg` gap changed from `--space-lg` (24px) to `--space-2xl` (48px)
- Reassigned component rules to semantically correct tokens:
  - `.btn-cta`, `.btn-secondary`, `.btn-destructive`: `--text-sm` → `--text-body`
  - `.form-label`, `.badge`, `.typeahead-empty`, `.typeahead-pin-badge`: `--text-sm` → `--text-label`
  - `.table`: `--text-sm` → `--text-body`
- Added new typography helper classes: `.text-label`, `.text-body`, `.text-title`, `.text-subheading`
- Updated existing helpers: `.text-heading` (700 weight, 1.1 line-height), `.text-price` (600 weight, 1.2 line-height via new 28px token)

**Task 2 — Card tiers, disabled buttons, table cleanup, spinner fix (commit b96f85f)**

- Added `position: relative` to `.card` to support deal badge absolute positioning
- Added card tier classes per D-09:
  - `.card--deal`: `border-left: 3px solid var(--color-success)`
  - `.card--empty`: `opacity: 0.5; border-style: dashed`
  - `.card-deal-badge`: absolute positioned badge with success color, label size, uppercase
- Added disabled button state per UIP-06/D-05: `.btn-cta:disabled`, `.btn-secondary:disabled`, `.btn-destructive:disabled` — `opacity: 0.5; cursor: not-allowed; pointer-events: none`
- Removed `border-top` from `.table td`; set padding to `10px var(--space-md)` per D-11
- Added `.table .col-landed { text-align: right }` for numeric column alignment
- Added `.typeahead-spinner.hidden { animation: none }` to stop animation when hidden

## Phase 5 Carry-Forwards Verified

- `--color-text-faint: #686868` — present (UIP-01)
- `:focus-visible` rules on all button classes — present (UIP-04)
- `:active { transform: scale(0.97) }` on all button classes — present (UIP-05)
- `repeat(3, 1fr)` at 1024px media query in `.card-grid` — present (UIP-09)

## Deviations from Plan

### Skipped Items (per plan notes)

**1. D-13 — JetBrains Mono font skipped**
- **Reason:** Plan notes explicitly state: "Do NOT add JetBrains Mono font — skip the D-13 discretionary item since we can't run a design audit tool in the worktree."
- **Impact:** No monospace token; prices will render in system sans-serif. Plan 02 template changes should not reference `--font-mono`.

**2. Worktree file restoration needed**
- **Found during:** Task 1 setup
- **Issue:** Worktree was checked out at Phase 1 commit (a5838a8) but branch HEAD was at f7d722f. git status showed many files as D (deleted). The working tree had a stub style.css (37 lines) instead of the full CRATE design system.
- **Fix:** Used `git reset --soft` to move HEAD, then `git checkout HEAD -- static/style.css` and `git checkout HEAD -- .planning/` to restore files. Subsequent per-task commits staged only `static/style.css` explicitly to avoid committing unrelated worktree differences.

## Known Stubs

None — all token values are concrete pixel values. No placeholder text or empty data flows introduced.

## Threat Flags

None — pure CSS presentation changes, no trust boundary crossed.

## Self-Check: PASSED

- static/style.css: FOUND
- 10-01-SUMMARY.md: FOUND
- commit 0b06a97 (task 1): FOUND
- commit b96f85f (task 2): FOUND
- --text-label 12px token: FOUND
- --text-heading 36px token: FOUND
- .card--deal class: FOUND
- .btn-cta:disabled rule: FOUND
- .typeahead-spinner.hidden rule: FOUND
