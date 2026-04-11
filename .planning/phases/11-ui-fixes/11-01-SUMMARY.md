---
phase: 11-ui-fixes
plan: "01"
subsystem: frontend/css
tags: [css, design-tokens, typography, colour]
dependency_graph:
  requires: []
  provides: [warm-bw-palette, reverted-typography-scale]
  affects: [all-templates, style.css]
tech_stack:
  added: []
  patterns: [css-custom-properties]
key_files:
  created: []
  modified:
    - static/style.css
decisions:
  - "Badge tokens unified to single greyscale set — album/artist/other all use rgba(255,255,255,0.06) per D-03 (only artwork has colour)"
  - "text-title dropped to 16px (matches body) to make album artwork the visual hero, not the text"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 1
---

# Phase 11 Plan 01: CSS Design Token Update Summary

CSS design tokens updated to implement the warm B&W palette and reverted typography scale — warm dark background (#0d0b0a), muted semantic colours, greyscale type badges, and pre-Phase-10 type sizes.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update colour tokens for warm B&W palette | 00c363e | static/style.css |
| 2 | Revert typography scale to pre-Phase-10 values | 00c363e | static/style.css |

## Changes Made

### Colour Tokens (Task 1)

| Token | Before | After |
|-------|--------|-------|
| `--color-bg` | `#0a0a0a` | `#0d0b0a` |
| `--color-surface` | `#111111` | `#141210` |
| `--color-surface-alt` | `#0a0a0a` | `#0d0b0a` |
| `--color-success` | `#34d399` | `#5a9e7a` |
| `--color-destructive` | `#f87171` | `#c46060` |
| `--color-destructive-border` | `rgba(239,68,68,0.4)` | `rgba(196,96,96,0.4)` |
| `--color-destructive-bg` | `rgba(239,68,68,0.1)` | `rgba(196,96,96,0.1)` |
| `--color-cta-text` | `#0a0a0a` | `#0d0b0a` |
| Badge album/artist/other (all 3 each) | Coloured rgba values | `rgba(255,255,255,0.06)` / `#999999` / `rgba(255,255,255,0.12)` |

### Typography Tokens (Task 2)

| Token | Before | After |
|-------|--------|-------|
| `--text-title` | `21px` | `16px` |
| `--text-heading` | `36px` | `24px` |
| `--text-subheading` | `22px` | `20px` |
| `--text-heading-secondary` | `21px` | `20px` |
| `.text-title` font-weight | `500` | `400` |
| `.text-subheading` font-weight | `700` | `600` |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — CSS-only changes, no security surface affected.

## Self-Check: PASSED

- `static/style.css` modified: confirmed
- Commit `00c363e` exists: confirmed
- `--color-bg: #0d0b0a` present: confirmed (3 occurrences)
- `--text-heading: 24px` present: confirmed
