# Phase 3: UI Redesign - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 03-ui-redesign
**Areas discussed:** CSS approach, Card layout, Artwork sourcing, FX rate display

---

## CSS Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Full custom CSS | Remove Tailwind CDN, hand-rolled CSS with design tokens | ✓ |
| Keep Tailwind CDN + design tokens | Keep Tailwind classes, add CSS custom properties on top | |
| Self-host Tailwind CLI build | Compile Tailwind to static file at build time | |

**User's choice:** Full custom CSS
**Notes:** User wanted whatever is most production-robust and scalable. Claude recommended full custom CSS — removes CDN runtime dependency, ships as a static file, no build tooling required for a solo Python app.

---

## Card Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Card shows summary, click for detail | Artwork hero + title + best price; click navigates to detail page | ✓ |
| Card expands inline | Click to expand listings table inline below card | |
| Card shows top 3 listings directly | Listings visible on card face | |

**User's choice:** Card shows summary, click for detail

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal: title + best price only | Clean Spotify album tile aesthetic | ✓ |
| Medium: title, best price, listing count, last scanned | More info at a glance | |
| You decide | Claude picks density | |

**User's choice:** Minimal — title + best price only
**Notes:** Spotify album-grid feel. Artwork dominant.

---

## Artwork Sourcing

| Option | Description | Selected |
|--------|-------------|----------|
| During scan, same background task | Discogs adapter captures artwork URL in existing scan | ✓ |
| Separate artwork enrichment pass | Second pass after scan for artwork only | |

**User's choice:** During scan, same background task

| Option | Description | Selected |
|--------|-------------|----------|
| Vinyl record SVG placeholder | Dark vinyl disc SVG for items without art | ✓ |
| Initials / text tile | Dark tile with item initials | |
| You decide | Claude picks placeholder | |

**User's choice:** Vinyl record SVG placeholder

---

## FX Rate Display

| Option | Description | Selected |
|--------|-------------|----------|
| exchangerate-api.com free tier | No auth, JSON, cache ~1 hour | ✓ |
| frankfurter.app | Open-source, ECB rates, no key needed | |
| You decide | Claude picks reliable free API | |

**User's choice:** exchangerate-api.com free tier

| Option | Description | Selected |
|--------|-------------|----------|
| AUD total prominent, original price secondary | AUD headline, "£22 + £8 shipping" below in smaller text. No FX rate shown. | ✓ |
| Side by side | "£22 → A$42.50" compact label | |
| You decide | Claude picks layout | |

**User's choice:** Option 1 modified — AUD total prominent, original currency below, but **no exchange rate label** in the UI.

---

## Claude's Discretion

- SVG placeholder delivery method
- Grid column count and responsive breakpoints
- Hover/focus states on cards
- Typography scale
