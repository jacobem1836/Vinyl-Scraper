---
phase: 19
plan: 01
status: complete
---

# Plan 19-01 Summary — Card Layout Expansion

## What Was Built

Pure CSS/HTML changes to make wishlist cards feel more spacious at wider viewports.

## Exact Changes

### static/style.css

| Location | Before | After |
|---|---|---|
| `.card-grid` gap (line 320) | `gap: var(--space-sm)` | `gap: var(--space-md)` |
| `.container` padding-inline (line 154) | `padding-inline: var(--space-md)` | `padding-inline: 12px` |
| `.nav-inner` padding-inline (line 190) | `padding-inline: var(--space-md)` | `padding-inline: 12px` |
| `@media (min-width: 1280px)` block (lines 335–339) | Entire 4-col breakpoint block | Removed |

### templates/index.html

| Location | Before | After |
|---|---|---|
| `<section class="card-grid">` (line 146) | Had `style="margin-inline: calc(-1 * var(--space-sm));"` | No style attribute |

## Decisions

**Why 12px for padding-inline (not 10px):** 12px provides a balanced breathing room at 1440px that doesn't feel flush. 10px reads slightly too tight alongside the card border-radius.

**Why the bleed was removed entirely (not adjusted):** The original `-8px` bleed worked when container padding was `16px` (net `8px` from edge). With padding now `12px`, a `-8px` bleed would leave only `4px` — nearly flush and visually incorrect. Removing the bleed altogether lets the `12px` container padding stand on its own.

## Verification

- ✓ No `repeat(4, 1fr)` in style.css (4-col breakpoint gone)
- ✓ `.card-grid` gap is `var(--space-md)` (16px)
- ✓ `.container` and `.nav-inner` both at `padding-inline: 12px`
- ✓ `<section class="card-grid">` has no `style=` attribute
- ✓ No backend files touched
