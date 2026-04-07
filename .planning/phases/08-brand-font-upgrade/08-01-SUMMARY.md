---
phase: 08-brand-font-upgrade
plan: "01"
subsystem: frontend/static
tags: [font, css, branding, performance]
dependency_graph:
  requires: []
  provides: [self-hosted-bodoni-moda-bold]
  affects: [templates/base.html, static/style.css]
tech_stack:
  added: []
  patterns: [css-custom-properties, font-face, preload-hint]
key_files:
  created:
    - static/fonts/BodoniModa-Bold.woff2
  modified:
    - static/style.css
    - templates/base.html
decisions:
  - "Latin subset woff2 downloaded from fonts.gstatic.com (15KB); covers all characters needed for CRATE wordmark"
  - "font-display: block chosen per D-04 — brief invisibility preferred over FOUT on brand mark"
  - "font-weight: 700 on .nav-brand to match Bold weight loaded in @font-face"
metrics:
  duration: ~5 minutes
  completed: "2026-04-07"
  tasks: 2
  files: 3
---

# Phase 8 Plan 1: Self-Host Bodoni Moda Bold for CRATE Wordmark Summary

**One-liner:** Self-hosted Bodoni Moda Bold (woff2, latin subset) applied to .nav-brand via @font-face + CSS custom property with font-display:block preload for zero-FOUT rendering.

## What Was Built

- `/static/fonts/BodoniModa-Bold.woff2` — 15KB latin-subset woff2 downloaded from fonts.gstatic.com at execution time; committed to repo for zero-CDN serving
- `@font-face` declaration added to `static/style.css` before the `:root` block with `font-display: block` and `src: url("fonts/BodoniModa-Bold.woff2") format("woff2")`
- `--font-display` CSS custom property added to `:root` alongside `--font-sans`, value: `"Bodoni Moda", var(--font-sans)`
- `.nav-brand` rule updated: added `font-family: var(--font-display)`, changed `font-weight: 600` to `700` to match loaded Bold weight
- Preload hint added to `templates/base.html` head before the stylesheet link: `<link rel="preload" href="/static/fonts/BodoniModa-Bold.woff2" as="font" type="font/woff2" crossorigin>`

## Key Files

| File | Change |
|------|--------|
| `static/fonts/BodoniModa-Bold.woff2` | Created — 15KB self-hosted font |
| `static/style.css` | @font-face block, --font-display property, .nav-brand update |
| `templates/base.html` | Preload link before stylesheet |

## Decisions Made

- Latin-only subset used (covers U+0000-00FF range which includes all uppercase ASCII needed for CRATE)
- Weight 700 (Bold) selected — closest standard weight to previous `font-weight: 600` and what the @font-face declares
- `font-display: block` per D-04 — brand mark should be invisible briefly, not flash in system font

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — font is a static committed asset with no user upload vector. Threats T-08-01 and T-08-02 accepted per threat model.

## Self-Check

- [x] `static/fonts/BodoniModa-Bold.woff2` exists and is 15KB
- [x] `@font-face` with `font-display: block` in style.css
- [x] `--font-display` custom property in :root
- [x] `.nav-brand` uses `font-family: var(--font-display)` with `font-weight: 700`
- [x] Preload link in base.html before stylesheet
- [x] No `fonts.googleapis.com` or `fonts.gstatic.com` references in any HTML/CSS
- [x] Commits: 65eb64d (font file), ee4f89d (CSS + HTML)

## Self-Check: PASSED
