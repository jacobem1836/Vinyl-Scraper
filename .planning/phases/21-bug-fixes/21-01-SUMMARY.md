---
plan: 21-01
phase: 21-bug-fixes
status: complete
completed_at: 2026-04-19T00:00:00Z
---

# Plan 21-01 Summary — Spinner & Skeleton Bug Fixes

## What Was Done

### Task 1: Typeahead Spinner Fix (BUG-03)

Three changes were made to `static/typeahead.js` to ensure the spinner is cleared on all close paths:

1. **`closeDropdown()`** now destructures `spinner` from `getEls(prefix)` and calls `spinner.classList.add("hidden")` unconditionally. This covers Escape, Tab, and any other path that calls `closeDropdown` (including the debounce guard when the query is too short).

2. **`selectResult()`** now cancels the pending debounce timer (`clearTimeout` + `timer = null`) before calling `closeDropdown`. This prevents a race where a debounce fires after a result is selected, which would re-show the spinner.

3. **Type change handler** now cancels the pending debounce timer before calling `closeDropdown` for the same race-condition reason.

### Task 2: Skeleton Shimmer Fix (UI-07)

Two changes were made to `static/style.css`:

1. **Renamed keyframe** from `skeleton-pulse` to `skeleton-shimmer` and updated the `background-position` values from a horizontal sweep (`200% 0` → `-200% 0`) to a diagonal sweep (`200% 200%` → `-200% -200%`).

2. **Updated `.card-artwork-wrapper`** properties:
   - `background` changed from `linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%)` to `linear-gradient(135deg, #0a0a0a 25%, #141414 50%, #0a0a0a 75%)` — darker, diagonal direction
   - `background-size` changed from `200% 100%` to `400% 400%` — wider gradient travel for the diagonal
   - `animation` changed from `skeleton-pulse 1.2s ease-in-out infinite` to `skeleton-shimmer 1.4s ease-in-out infinite`

`.card-artwork-wrapper.loaded` was left unchanged (`animation: none; background: transparent`).

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| closeDropdown hides spinner | ✓ |
| Debounce cancelled on selectResult | ✓ |
| Debounce cancelled on type change | ✓ |
| skeleton-pulse removed | ✓ |
| skeleton-shimmer 135deg #0a0a0a/#141414 | ✓ |
| .card-artwork-wrapper.loaded unchanged | ✓ |

## Files Modified
- `static/typeahead.js`
- `static/style.css`

## Commit
- `38811b4` — fix(21-01): clear spinner on all typeahead close paths and replace skeleton animation

## Self-Check: PASSED
- Both files modified and committed (38811b4)
- All acceptance criteria verified via grep
