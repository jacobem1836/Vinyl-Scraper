---
phase: 18
plan: "18-02"
subsystem: templates
tags: [placeholder, image, item-detail, fix]
dependency_graph:
  requires: []
  provides: [FIX-02]
  affects: [templates/item_detail.html]
tech_stack:
  added: []
  patterns: []
key_files:
  created: []
  modified:
    - templates/item_detail.html
decisions:
  - Preserve all surrounding markup (style, alt text, Jinja block structure) — only swap the two path strings
metrics:
  duration: "3 minutes"
  completed: "2026-04-15"
  tasks_completed: 1
  files_modified: 1
---

# Phase 18 Plan 02: Item detail placeholder swap (FIX-02) Summary

## One-Liner

Replaced both `vinyl-placeholder.svg` references in `item_detail.html` with `empty-vinyl-placeholder.png` — onerror fallback and no-artwork else branch.

## What Was Done

**Task T1 — Swap placeholder to empty-vinyl-placeholder.png in both branches**

Two exact string replacements in `templates/item_detail.html` inside the artwork block (lines 14–29):

1. `onerror="this.src='/static/vinyl-placeholder.svg'"` → `onerror="this.src='/static/empty-vinyl-placeholder.png'"`
2. `src="/static/vinyl-placeholder.svg"` → `src="/static/empty-vinyl-placeholder.png"`

All surrounding markup preserved: style attributes (`width: 120px; height: 120px; object-fit: cover; border-radius: 0;`), alt text, and the `{% if item.artwork_url %}` / `{% else %}` / `{% endif %}` Jinja structure.

## Acceptance Criteria — All Pass

- `grep -n "vinyl-placeholder.svg" templates/item_detail.html` → 0 matches
- `grep -c "empty-vinyl-placeholder.png" templates/item_detail.html` → 2
- `onerror="this.src='/static/empty-vinyl-placeholder.png'"` → line 19
- `src="/static/empty-vinyl-placeholder.png"` → line 24 (else branch)
- Style attr count → 2
- Alt text `{{ item.query }} — no artwork available` → preserved
- Jinja parse → exit 0

## Deviations from Plan

**1. [Rule 3 - Blocking] Restored planning files and Phase 17 assets deleted by worktree state mismatch**
- **Found during:** Task T1 commit
- **Issue:** The `git reset --soft` to align the worktree base brought in staged deletions for planning files (Phase 16/17 artifacts, FUTURE.md, REQUIREMENTS.md), Gothic A1 font woff2 files, and stale working-tree reversions of style.css and base.html from before Phase 17. These were inadvertently committed alongside the T1 change.
- **Fix:** Checked out all deleted/reverted files from the base commit (`aba1012`) and committed as a fixup commit.
- **Files modified:** All Phase 16/17 planning artifacts, Gothic A1 font files, static/style.css, templates/base.html, .planning/STATE.md
- **Commit:** `009a69b`

## Known Stubs

None — placeholder paths are fully wired to an existing static asset.

## Threat Flags

None — change is template-only, no new network surface or auth paths.

## Self-Check

- [x] `templates/item_detail.html` modified — FOUND
- [x] `static/empty-vinyl-placeholder.png` exists — FOUND
- [x] Commit `f576ca4` exists — FOUND
- [x] Fixup commit `009a69b` exists — FOUND

## Self-Check: PASSED
