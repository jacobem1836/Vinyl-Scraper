# Phase 4: UI Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 04-ui-polish
**Areas discussed:** Colour palette, Accent colour, Spacing & border-radius, Nav title / App name, Discogs manual selection (deferred)

---

## Colour Palette

| Option | Description | Selected |
|--------|-------------|----------|
| Near-black neutral | `#0a0a0a` bg, `#111111` surface — Apple dark mode / Vercel territory | ✓ |
| Cool dark (subtle tint) | `#0d1117` bg — GitHub dark, very subtle cool tint | |
| True black + contrast | `#000000` bg — highest drama, premium product | |

**User's choice:** Near-black neutral  
**Notes:** User initially questioned warm charcoal as not achieving "super sleek and slick." Warm palette was dropped in favour of neutral near-black. Key framing: Vercel/Linear/Apple dark mode aesthetic.

---

## Accent Colour

| Option | Description | Selected |
|--------|-------------|----------|
| Crisp white / off-white | `#ffffff` — maximum sleekness, pairs with near-black | ✓ |
| Muted green | `#4ade80` — alive without being loud (Linear, Raycast style) | |
| Ice blue / slate | `#7dd3fc` — sophisticated but adds back some blue | |

**User's choice:** White  
**Notes:** Replaces amber/gold (`#f59e0b`) entirely.

---

## Border Radius

| Option | Description | Selected |
|--------|-------------|----------|
| Sharp everywhere | radius: 0 on cards/containers, 2px on buttons/badges | ✓ |
| Minimal rounding | 4px max across the board | |
| Sharp cards, rounded buttons | Cards: 0, buttons: 6px | |

**User's choice:** Sharp everywhere  
**Notes:** "No rounded excess" from roadmap taken to its logical conclusion.

---

## Spacing

| Option | Description | Selected |
|--------|-------------|----------|
| Tighter overall | Card padding 12px, grid gap 12px, section gap 20px | ✓ |
| Tighter only in cards | Compress card internals, keep page-level spacing | |
| You decide | Leave to Claude | |

**User's choice:** Tighter overall

---

## Nav Title / App Name

**Initial discussion:** User asked about renaming the app rather than just styling the existing name.

**Name considered and selected:** CRATE — chosen because the dashboard literally simulates a record crate; the metaphor is functional, not decorative.

| Option | Description | Selected |
|--------|-------------|----------|
| Wide-tracked wordmark | `C R A T E`, caps, tracking 0.25em, weight 700 | ✓ |
| Mixed case + accent dot | `Crate•` with white accent dot | |
| You decide | Leave typographic treatment to Claude | |

**User's choice:** Wide-tracked wordmark  
**Notes:** App renamed from "Vinyl Wishlist Manager" (or similar) to **CRATE**.

---

## Discogs Manual Selection (Deferred)

**User clarification:** The issue is that auto-match sometimes picks the wrong Discogs release (e.g. Hamilton soundtrack shows wrong pressing). User wants a way to manually search and select the correct release from scan results. This is a new feature capability, not visual polish — explicitly deferred to a future phase.

## Claude's Discretion

- Exact font-size / line-height for CRATE wordmark
- Badge colour variants after amber removal
- Hover/focus state adjustments after palette swap

## Deferred Ideas

- Discogs manual release selection — detail page + Discogs release API search + new model field (pinned release ID); defer to future phase
