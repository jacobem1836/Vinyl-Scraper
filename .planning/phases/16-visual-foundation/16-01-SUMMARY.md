---
phase: 16
plan: 01
title: True black palette, skeleton pulse, and scrollbar rework
status: completed
completed_at: 2026-04-14
commits:
  - cca23e7
  - 12247f0
  - 41c90af
---

## Summary

All three tasks executed and committed. `static/style.css` is the only file modified — no templates, JS, fonts, spacing, or radius changes.

## Changes Made

### Task 1 — Color tokens shifted to #000000 (lines 28–30, 46)

| Token | Before | After |
|-------|--------|-------|
| `--color-bg` | `#0d0b0a` | `#000000` |
| `--color-surface` | `#141210` | `#000000` |
| `--color-surface-alt` | `#0d0b0a` | `#000000` |
| `--color-cta-text` | `#0d0b0a` | `#000000` |

Unchanged as required: `--color-border: #222222`, `--color-border-muted: #111111`, all `--color-text*`, `--color-accent*`, spacing, radius tokens.

**`--color-border-muted` decision:** Left at `#111111` — visually it is extremely subtle against `#000000` but `--color-border: #222222` provides the primary visible border. Flag for Wave 2 human verification to decide if it needs lifting.

### Task 2 — Skeleton pulse lifted (line 640)

`.card-artwork-wrapper` gradient: `#1a1a1a → #0a0a0a` (base), `#2a2a2a → #141414` (highlight). Animation timing and keyframes unchanged. Scoped to `.card-artwork-wrapper` only — no other rules touched.

### Task 3 — Section 19 scrollbar rework (lines 824–845)

Full replacement of previous 6px colored-track scrollbar block. New block covers three scopes:

1. **Global** — `width: 4px; track: transparent; thumb: rgba(255,255,255,0.2); hover: rgba(255,255,255,0.4); border-radius: 0`
2. **`.typeahead-dropdown`** — identical values, scoped selectors
3. **`.table-container`** — identical values, scoped selectors
4. **Firefox** — `html { scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.2) transparent; }`

Legacy values `#444444`, `#666666`, `#1a1a1a`, `width: 6px` fully purged from section 19.

## Verification

```
✓ --color-bg: #000000 in :root
✓ --color-surface: #000000 in :root
✓ --color-surface-alt: #000000 in :root
✓ --color-cta-text: #000000 in :root
✓ Skeleton pulse: #0a0a0a / #141414 present in .card-artwork-wrapper
✓ Global ::-webkit-scrollbar { width: 4px }
✓ rgba(255,255,255,0.2) appears 5 times (global thumb + 2x scoped thumb + Firefox)
✓ rgba(255,255,255,0.4) appears 2 times (global hover + 2x scoped hover)
✓ .typeahead-dropdown::-webkit-scrollbar rules present (4 selectors)
✓ .table-container::-webkit-scrollbar rules present (4 selectors)
✓ Firefox scrollbar-color: rgba(255,255,255,0.2) transparent
✓ No legacy values (#444444, #666666) in scrollbar rules
✓ Previous token values (#0d0b0a, #141210) absent from :root for affected tokens
```

## Notes for Plan 02 (Human Verification)

- Check that `--color-border-muted: #111111` is perceptible against `#000000` surfaces — may need raising to `#1a1a1a` if invisible
- Skeleton pulse should be barely-but-visibly animated (subtle lift above true black is intentional per D-03)
- Scrollbar should be invisible until scrolling, then thin white-translucent strip appears

## Self-Check: PASSED
