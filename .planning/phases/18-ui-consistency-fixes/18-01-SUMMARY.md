---
phase: 18
plan: "18-01"
subsystem: frontend/ui
tags: [ui, toast, scan-panel, javascript, python]
dependency_graph:
  requires: []
  provides: [FIX-01]
  affects: [templates/base.html, app/routers/wishlist.py]
tech_stack:
  added: []
  patterns: [guard-clause JS, URL encoding em-dash]
key_files:
  created: []
  modified:
    - templates/base.html
    - app/routers/wishlist.py
decisions:
  - "Removed else-if(s.started_at) branch entirely rather than patching — cleaner intent, no completed-state ghost panel"
  - "Em-dash (%E2%80%94) used in URL encoding for toast copy, consistent with existing em-dash usage in scan polling UI"
metrics:
  duration: "5 minutes"
  tasks_completed: 2
  files_modified: 2
  completed_date: "2026-04-15"
---

# Phase 18 Plan 01: Toast-only post-add confirmation (FIX-01) Summary

**One-liner:** Scan panel gated to is_running-only by removing the else-if(s.started_at) branch; toast copy updated to em-dash separator.

## What Was Built

Two targeted one-line fixes to eliminate the ghost scan panel that appeared after adding an item:

1. **templates/base.html** — DOMContentLoaded scan-status handler simplified from:
   ```js
   .then(function(s) { if (s.is_running) { showPanel(); startPolling(); } else if (s.started_at) { showPanel(); renderStatus(s); } })
   ```
   to:
   ```js
   .then(function(s) { if (s.is_running) { showPanel(); startPolling(); } })
   ```
   The `else if (s.started_at)` branch caused `#scanPanel` to appear whenever a prior scan had a `started_at` value — i.e. always after any historical scan, including right after adding a new item.

2. **app/routers/wishlist.py** — Add-item redirect URL updated from `?toast=Item+added%2C+scanning+in+background` to `?toast=Item+added+%E2%80%94+scanning+in+background` (em-dash separator instead of comma).

## Verification Results

All acceptance criteria pass:
- `grep -n "else if (s.started_at)" templates/base.html` — no matches
- `grep -nE "if \(s\.is_running\)..."` — exactly one match at line 258
- `grep -n "toast=Item+added%2C"` — no matches (old form removed)
- `grep -n "toast=Item+added+%E2%80%94"` — one match at line 121
- `renderStatus` function body unchanged
- `params.get('toast')` handler unchanged

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes introduced.

## Self-Check

Files verified:
- `templates/base.html` — modified, else-if branch removed
- `app/routers/wishlist.py` — modified, em-dash URL in place

Commit: b349b07
