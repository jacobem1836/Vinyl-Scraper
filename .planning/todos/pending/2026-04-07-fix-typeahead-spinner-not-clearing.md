---
created: 2026-04-07T09:29:53.338Z
title: Fix typeahead spinner not clearing
area: ui
files:
  - static/typeahead.js:143-167
  - static/typeahead.js:271-278
---

## Problem

The typeahead loading spinner never clears after selecting a result (click or keyboard) or switching the type dropdown to "Key Word/s". The fix attempted in commit `bbea661` added `spinner.classList.add("hidden")` to `selectResult()`, `resetTypeahead()`, and the type change handler — but the spinner still persists visually.

Needs deeper investigation into why the hide calls have no effect. Possible causes:
- Wrong element ID — `getEls(prefix)` may not be finding the correct spinner element
- CSS override — another rule may be keeping the spinner visible (e.g. animation or display property overriding the `.hidden` class)
- The spinner element referenced in `getEls()` is not the one actually visible on screen
- Timing issue — spinner re-shown after hide by a pending fetch callback

UAT tests 3, 4, 6 still failing after the attempted fix.

## Solution

1. Inspect the DOM in browser devtools to confirm which element is the visible spinner and whether it matches `{prefix}Spinner` ID
2. Check if `.hidden` class is actually being applied (breakpoint in selectResult)
3. Check CSS specificity — does `.hidden { display: none }` get overridden by the spinner's animation CSS?
4. If element mismatch, fix the ID or selector in `getEls()`
