---
phase: 17-typography-overhaul
plan: "01"
subsystem: frontend/typography
tags: [typography, fonts, css, gothic-a1, self-hosted]
dependency_graph:
  requires: []
  provides: [gothic-a1-fonts, font-sans-token]
  affects: [static/style.css, templates/base.html, static/fonts/]
tech_stack:
  added: [Gothic A1 woff2 (Latin subset)]
  patterns: [self-hosted font, @font-face, CSS custom property token]
key_files:
  created:
    - static/fonts/GothicA1-Light.woff2
    - static/fonts/GothicA1-Regular.woff2
    - static/fonts/GothicA1-Medium.woff2
  modified:
    - static/style.css
    - templates/base.html
decisions:
  - "Used Latin-only woff2 subsets from Google Fonts CDN (14–15 KB each vs 352 KB Inter variable font)"
  - "Relative font paths in @font-face (fonts/GothicA1-*.woff2) matching existing Bodoni Moda pattern"
  - "Only Regular (400) preloaded; Light and Medium load on demand"
  - "Inter woff2 file left in place (cleanup out of scope per plan)"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-15"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 5
requirements: [TYPO-01]
---

# Phase 17 Plan 01: Gothic A1 Font Swap Summary

Self-hosted Gothic A1 (Light/Regular/Medium) replaces Inter as the body typeface via three woff2 files, updated @font-face declarations, a --font-sans token swap, and a preload link update in base.html.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Download Gothic A1 woff2 files | 97e1dd9 | static/fonts/GothicA1-{Light,Regular,Medium}.woff2 |
| 2 | Add @font-face block, update --font-sans, swap preload | 09e9740 | static/style.css, templates/base.html |

## What Was Built

Three Gothic A1 Latin-subset woff2 files (300/400/500) are now self-hosted in `/static/fonts/`. The `static/style.css` file declares three `@font-face` blocks for Gothic A1 replacing the single Inter variable font declaration, and `--font-sans` now starts with `"Gothic A1"` instead of `"Inter"`. The `templates/base.html` preload link points to `GothicA1-Regular.woff2` instead of the Inter variable font file. Bodoni Moda is untouched throughout.

## Verification Results

- 3 Gothic A1 woff2 files present in static/fonts/ (all non-empty, all valid woff2 magic header)
- `grep -c 'font-family: "Gothic A1"' static/style.css` returns `3`
- `--font-sans` starts with `"Gothic A1", -apple-system, ...`
- No `font-family: "Inter"` in style.css
- base.html preloads `GothicA1-Regular.woff2`, not Inter
- Bodoni Moda @font-face and preload unchanged
- `--font-display` still references `"Bodoni Moda"` (D-04)

## Deviations from Plan

None - plan executed exactly as written.

The earlier commit (9378739) included planning file deletions as a side-effect of the worktree `git reset --soft` to rebase onto the correct base commit. This was a git mechanics issue with the worktree setup, not a code deviation. The font files themselves were correctly committed in a follow-up commit (97e1dd9).

## Known Stubs

None. Gothic A1 is wired into `--font-sans` which flows site-wide via `font-family: var(--font-sans)` on `body`. All body text, card titles, and price numerals will render in Gothic A1.

## Threat Flags

None. No new network endpoints, auth paths, or trust boundaries introduced. Font files are static assets.

## Self-Check: PASSED

- static/fonts/GothicA1-Light.woff2: FOUND
- static/fonts/GothicA1-Regular.woff2: FOUND
- static/fonts/GothicA1-Medium.woff2: FOUND
- Commit 97e1dd9: FOUND
- Commit 09e9740: FOUND
