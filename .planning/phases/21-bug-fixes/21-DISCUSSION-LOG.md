> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-18
**Phase:** 21-bug-fixes
**Mode:** discuss
**Areas discussed:** Spinner fix approach, Skeleton shimmer appearance

## Gray Areas Presented

| Area | Selected? |
|------|-----------|
| Spinner fix approach | Yes |
| Skeleton shimmer appearance | Yes |

## Discussions

### Spinner Fix Approach

- **Question:** How thorough should the spinner fix be?
- **Options presented:**
  - Thorough fix: fix closeDropdown() AND cancel debounce timer on select/type change
  - Minimal fix: only add spinner hide to closeDropdown()
- **User chose:** Thorough fix

**Root cause identified:** `closeDropdown()` doesn't hide the spinner (covers Escape/blur/close paths), AND there's a debounce timing race where the debounce fires after result selection and shows the spinner with no way to clear it.

### Skeleton Shimmer Appearance

- **Question:** What should the diagonal skeleton shimmer look like?
- **Options presented:**
  - Standard 45°, same dark colors (#0a0a0a→#1a1a1a→#0a0a0a)
  - 45°, slightly brighter highlight (#0a0a0a→#252525→#0a0a0a)
- **User chose:** Standard 45°, same dark colors
- **User note:** "Doesn't matter that much — main thing is it should be a barely visible black shimmer rather than the current grey"

## Corrections Made

None — both selections matched the recommended options.

## Todos Cross-Referenced

- "Fix typeahead spinner not clearing" — in scope (BUG-03)
- "Add eBay developer keys/configs" — completed Phase 20
- "Remove dead Clarity stuff" — completed Phase 20
- "Add manual Discogs selection" — Phase 23 scope
