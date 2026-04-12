# Phase 11: UI Fixes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 11-ui-fixes
**Mode:** discuss
**Areas discussed:** Logo, Colour Palette, Card System, Typography, Dynamic UI, Functional Fixes

---

## Logo

| Option | Description | Selected |
|--------|-------------|----------|
| New wordmark font | Keep CRATE text, different display font | |
| Image/icon logo | Actual logo asset alongside or replacing text | ✓ |
| Both | New icon + new wordmark font | |

**User's choice:** Image/icon logo — abstract vinyl-on-shelf concept with diagonal lines evoking records standing in a crate, side-on view. AI-generated, multiple options to be presented.

---

## Fonts (page body)

| Option | Description | Selected |
|--------|-------------|----------|
| Pure system fonts | Revert to system font stack | |
| Specific web font | User has a particular font in mind | |
| Claude recommends | Claude picks options fitting B&W brutalist aesthetic | ✓ |

**User's choice:** Claude recommends font options, user chooses from them during planning.

---

## Text Sizes

| Option | Description | Selected |
|--------|-------------|----------|
| Full revert | Back to pre-Phase 10 flat scale (14→16→20→24px) | ✓ |
| Partial revert | Shrink headings/prices, keep some improvements | |
| Just tweak | Keep new scale, adjust specific sizes | |

**User's choice:** Full revert or equivalent — key priority is keeping album covers as the visual focus. Text subordinate to artwork.

---

## Dynamic UI Energy

| Option | Description | Selected |
|--------|-------------|----------|
| Subtle & refined | Gentle fades, soft reveals, slight parallax (Linear/Vercel) | ✓ (primary) |
| Confident & punchy | Snappy transitions, bold hover transforms (Stripe/Framer) | |
| Brutalist motion | Sharp cuts, no easing, instant state changes | ✓ (secondary) |

**User's choice:** Combination of subtle & refined (primary) with brutalist sharpness (secondary). All three types wanted (hover effects, transitions, micro-interactions). Magic MCP (21st.dev) MUST be used. User wants to sense-check proposals before implementation.

---

## B&W Palette Strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Strict B&W | No green, no red anywhere | |
| B&W + functional colour | Keep red/green as functional signals | ✓ (combined) |
| B&W + subtle accents | Very muted/desaturated accent tones | ✓ (combined) |

**User's choice:** B&W at rest with minimal functional colour on hover/interaction only. Accents are muted and desaturated.

---

## Background Colour

| Option | Description | Selected |
|--------|-------------|----------|
| Keep near-black (#0a0a0a) | Current background | |
| True black (#000000) | Maximum contrast, OLED-friendly | |
| Warm dark (#0d0b0a) | Subtle warmth without losing dark feel | ✓ |

---

## Deal Indicators

| Option | Description | Selected |
|--------|-------------|----------|
| Badge only | DEAL badge fades in on hover, no border | ✓ |
| Border + badge | Both green border and badge on hover | |
| Price highlight | Price text shifts to green on hover | |

---

## Empty Cards

| Option | Description | Selected |
|--------|-------------|----------|
| Keep current | 50% opacity + dashed border | |
| Minimal ghost | 30-40% opacity, no border, faded art | ✓ |
| Outlined only | Full opacity, thin grey outline | |

**Notes:** User will provide a new placeholder asset file for empty card artwork.

---

## Card Sizing

| Option | Description | Selected |
|--------|-------------|----------|
| Too much side margin | Cards centred with wasted space | ✓ |
| Cards too narrow | Want fewer, bigger cards | |
| Both | Less margin AND bigger cards | |

**User's choice:** Reduce side margins so grid goes closer to edge-to-edge.

---

## Claude's Discretion

- Ghost card exact opacity (30-40% range)
- Scrollbar styling details
- Loading state design
- Warm dark background exact hex

## Deferred Ideas

- Irrelevant results filtering → Phase 12
- Digital listing filtering → Phase 12
- Discogs location data → Phase 12
