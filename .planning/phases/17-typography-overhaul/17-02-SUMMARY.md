---
phase: 17-typography-overhaul
plan: "02"
subsystem: frontend/typography
tags: [typography, css, hierarchy, card-layout, font-weight]
dependency_graph:
  requires: [17-01]
  provides: [name-price-hierarchy, text-title-token-23px, text-price-token-17px]
  affects: [static/style.css]
tech_stack:
  added: []
  patterns: [CSS token override, utility-class font-weight tuning]
key_files:
  created: []
  modified:
    - static/style.css
decisions:
  - "--text-title set to 23px (upper half of D-05 22-24px range) — strong hierarchy without overpowering artwork"
  - "--text-price set to 17px (middle of D-05 16-18px range) — clearly subordinate to 23px name"
  - "font-weight 450 for .text-title rounds to Gothic A1 Regular (400) in browser — intentional thin gothic feel per D-05"
  - "font-weight 350 for .card-price / .text-price rounds to Gothic A1 Light (300) — visually lighter than name"
  - ".price-best weight 400 (not 600) to stay within D-05 price range without overriding .card-price 350"
metrics:
  duration: "~8 minutes"
  completed: "2026-04-15"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 1
requirements: [TYPO-02, TYPO-03]
---

# Phase 17 Plan 02: Name > Price Hierarchy Summary

Inverted card hierarchy so item name (23px / weight 450) reads as the visual hero and price (17px / weight 350) becomes a supporting detail. Two CSS token values and four utility-class rules changed in static/style.css — no template modifications required.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update --text-title and --text-price tokens | 5aa5bae | static/style.css |
| 2 | Update .text-title / .card-price / .text-price / .price-best font-weights | 9679e7d | static/style.css |

## What Was Built

Two token values in `:root` were updated: `--text-title` from 18px to 23px, `--text-price` from 28px to 17px. Four utility-class rules were updated: `.text-title` weight 400 → 450 (line-height 1.3 → 1.25), `.text-price` and `.card-price` weight 600 → 350 (line-height 1.2 → 1.3), `.price-best` weight 600 → 400 to avoid overriding the new price weight. All other tokens and utility classes unchanged (`--text-heading` 24px/700, `--text-subheading` 20px/600, `--text-body` 16px).

The hierarchy now reads name > price on every dashboard card (23px/450 vs 17px/350), and the item detail page h1 at 24px/700 continues to outrank listing prices at 17px/350. Gothic A1 font swap from plan 01 propagates automatically via `--font-sans`, so no per-template overrides were needed.

## Verification Results

- `--text-title: 23px` confirmed in :root
- `--text-price: 17px` confirmed in :root
- `--text-heading: 24px` unchanged (untouched per D-09)
- `--text-body: 16px` unchanged
- `--text-subheading: 20px` unchanged
- `.text-title { font-weight: 450 }` confirmed
- `.card-price { font-weight: 350 }` confirmed
- `.text-price { font-weight: 350 }` confirmed
- `.price-best { font-weight: 400 }` confirmed
- `.text-heading { font-weight: 700 }` unchanged
- `.text-subheading { font-weight: 600 }` unchanged
- No template files modified

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. All token and weight changes flow directly through the CSS cascade. No placeholder values or disconnected wiring.

## Threat Flags

None. CSS-only change; no new endpoints, auth paths, or trust boundaries.

## Self-Check: PASSED

- static/style.css updated with 23px title token: FOUND (--text-title: 23px)
- static/style.css updated with 17px price token: FOUND (--text-price: 17px)
- .text-title weight 450: FOUND
- .card-price weight 350: FOUND
- .text-price weight 350: FOUND
- .price-best weight 400: FOUND
- Commit 5aa5bae: FOUND
- Commit 9679e7d: FOUND
