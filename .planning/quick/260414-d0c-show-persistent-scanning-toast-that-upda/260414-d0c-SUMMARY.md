---
phase: quick
plan: 260414-d0c
subsystem: frontend
tags: [toast, scan, feedback, ux]
key-files:
  modified:
    - templates/base.html
decisions:
  - Re-use existing window.showToast() with 999999ms duration to keep toast persistent during scan
metrics:
  duration: "< 5 minutes"
  completed: "2026-04-14"
  tasks: 1
  files: 1
---

# Quick Task 260414-d0c: Show Persistent Scanning Toast Summary

**One-liner:** Added persistent in-progress toast to `renderStatus()` that updates on every poll cycle showing current item name and progress counter.

## What Was Done

Inside the `if (s.is_running)` branch of `renderStatus()` in `templates/base.html`, added two lines:

```js
var currentName = (s.current && s.current.length > 0) ? s.current[0].query : 'items';
window.showToast('Scanning (' + s.done + '/' + s.total + ') \u2014 ' + currentName, 999999);
```

The `999999` ms duration keeps the toast visible indefinitely until replaced. The existing completion branch already calls `window.showToast(..., 6000)` which naturally replaces the in-progress toast and auto-dismisses after 6s.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: Add in-progress toast to renderStatus() | ce4883f | templates/base.html |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — client-side only change, no new network endpoints or auth paths.

## Self-Check: PASSED

- templates/base.html modified with the two new lines
- Commit ce4883f exists
