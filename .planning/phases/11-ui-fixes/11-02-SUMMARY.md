---
phase: 11-ui-fixes
plan: "02"
subsystem: frontend/css
tags: [css, interactions, cards, hover, scrollbar]
dependency_graph:
  requires: ["11-01"]
  provides: [card-hover-reveal, ghost-card-styling, interaction-layer, scrollbar]
  affects: [static/style.css, templates/index.html]
tech_stack:
  added: []
  patterns: [parent-hover-child-reveal, css-transitions, scrollbar-styling]
key_files:
  created: []
  modified:
    - static/style.css
    - templates/index.html
decisions:
  - "Deal badge uses opacity+visibility transition (not display) for smooth fade — CSS-only, no JS"
  - "btn-secondary hover goes to full white bg (#ffffff) — strong contrast signal for engagement"
  - "btn-destructive hover fills solid muted red (not just tint) — clear destructive intent on hover"
  - "Button :active uses transition-duration:0ms for instant press, ease-out on base for smooth release"
  - "Scrollbar hardcoded in hex (#1a1a1a, #444444) not CSS vars — scrollbar pseudo-elements don't inherit vars reliably"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
---

# Phase 11 Plan 02: Card System and Interaction Layer Summary

Card system overhauled to B&W-at-rest with colour-on-engagement: deal badges hidden until hover, ghost cards faded with no border, card grid pulls closer to viewport edges. Interaction layer adds 150ms ease-out transitions throughout, solid-fill button hover states, instant-press :active with ease-out release, and a 6px B&W scrollbar.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Card system — deal badge hover, ghost cards, margins | 9a13010 | static/style.css, templates/index.html |
| 2 | Interaction layer — hover effects, micro-interactions, transitions | 0462429 | static/style.css |

## Changes Made

### Task 1: Card System

| Change | Before | After |
|--------|--------|-------|
| `.card--deal` border | `border-left: 3px solid var(--color-success)` | `border-left: none` |
| `.card--empty` opacity | `0.5` | `0.35` |
| `.card--empty` border | `border-style: dashed` | `border: none` |
| `.card-deal-badge` visibility | always visible | `opacity:0; visibility:hidden` at rest |
| `.card:hover .card-deal-badge` | (did not exist) | `opacity:1; visibility:visible` |
| Card grid margins | flush to container | `margin-inline: calc(-1 * var(--space-sm))` pulls 8px inward |

### Task 2: Interaction Layer

| Change | Before | After |
|--------|--------|-------|
| Card transition timing | `200ms ease` | `150ms ease-out` |
| Card hover shadow | `0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0,5,20,0.8)` | `0 4px 16px rgba(0,0,0,0.4)` |
| Button transitions | `background 200ms` | `background 150ms, color 150ms, transform 150ms ease-out` |
| `.btn-secondary:hover` | `background: var(--color-surface)` | `background: #ffffff; color: #0d0b0a` |
| `.btn-destructive:hover` | `background: var(--color-destructive-bg)` | solid red bg + white text + border fill |
| Button `:active` | `transform: scale(0.97)` | same + `transition-duration: 0ms` (instant press) |
| Scrollbar | browser default | 6px, dark track, grey thumb, hover highlight |

## Deviations from Plan

None — plan executed exactly as written. Interaction spec from Task 0 (approved by user as UI-SPEC fallback values) implemented precisely.

## Known Stubs

None.

## Threat Flags

None — CSS and template layout changes only, no security surface affected.

## Self-Check: PASSED

- `static/style.css` modified: confirmed
- `templates/index.html` modified: confirmed
- Commit `9a13010` exists: confirmed (Task 1)
- Commit `0462429` exists: confirmed (Task 2)
- `.card:hover .card-deal-badge` rule present: confirmed (grep count = 1)
- `::-webkit-scrollbar` rules present: confirmed (grep count = 4)
- `transition-duration: 0ms` on :active: confirmed
