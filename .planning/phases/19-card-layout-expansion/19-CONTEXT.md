# Phase 19: Card Layout Expansion - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Make wishlist cards fill more of the screen width and feel larger/more spacious — more visual impact per card. CSS-only change: grid column counts, gaps, and container side margins. No backend changes. No card content or markup restructuring.

Requirements in scope: CARD-01

</domain>

<decisions>
## Implementation Decisions

### Column Count (CARD-01)
- **D-01:** Drop the 4-column tier entirely. New breakpoint scheme: 3 cols at 1024px+, 2 cols at 768px+, 1 col below 768px.
- **D-02:** The 1280px breakpoint that currently bumps to 4 cols is removed. Large screens (1280px, 1440px) render at 3 cols alongside 1024–1279px.
- **D-03:** The 768px tier (2 cols) is unchanged — keeps standard tablet layout.
- **D-04:** Mobile (below 768px) stays at 1 col — unchanged.

### Card Gap
- **D-05:** Increase grid gap from `var(--space-sm)` (8px) to `var(--space-md)` (16px). Doubles the breathing room between cards, consistent with the larger card size.

### Side Margins (Container Padding)
- **D-06:** Reduce container `padding-inline` from `var(--space-md)` (16px) to approximately 10px — about 2/3 of current. This gives cards more horizontal real-estate while keeping a small gutter at the viewport edge.
- **D-07:** The same reduction applies to `.nav-inner` padding-inline so nav and card grid stay aligned.

### Claude's Discretion
- Exact side margin value: 10px or 12px, whichever reads most balanced with the new 3-col layout at 1440px.
- Card body padding: currently 8px/16px. May increase slightly if the wider card makes the text feel cramped — but only if obviously needed.
- Whether to introduce a new CSS variable for the reduced side margin (e.g. `--space-page`) or inline the value — choose the simpler option.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §CARD-01 — Acceptance criteria for card layout expansion

### Codebase — change surfaces
- `static/style.css` lines 151–155 — `.container` definition; `padding-inline: var(--space-md)` is the side margin to reduce
- `static/style.css` lines 188–192 — `.nav-inner`; same `padding-inline` value; must match `.container`
- `static/style.css` lines 317–339 — `.card-grid` with all 4 breakpoint tiers; 1280px tier (4-col) is removed, others adjusted
- `templates/index.html` line 146 — Card grid `<section class="card-grid">` markup (no change expected)

### Prior phase context
- `.planning/phases/16-visual-foundation/16-CONTEXT.md` — Warner Music aesthetic (restraint, no decorative additions)
- `.planning/phases/17-typography-overhaul/17-CONTEXT.md` — Typography tokens; card hierarchy (name larger, price secondary)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `--space-md` (16px) already exists as the new gap target — no new variable needed for gap change
- Grid breakpoint structure in `.card-grid` is clean and easy to modify (3 `@media` blocks, lines 322–338)

### Established Patterns
- All spacing via CSS variables; no hardcoded values in templates
- Container max-width 1280px — unchanged; this phase widens cards by reducing columns and margins, not by changing max-width
- `margin-inline: calc(-1 * var(--space-sm))` on `.card-grid` compensates for parent padding; if gap changes this may need revisiting

### Integration Points
- `.container` padding-inline reduction affects ALL pages (index, item detail, any future pages) — desired, keeps nav and content aligned
- `.card-grid` gap and column changes are isolated to the grid itself — no cascade risk

</code_context>

<specifics>
## Specific Ideas

- "Also decrease the margins on the sides — make them about 2/3 of their current size." — reduce container and nav-inner padding-inline from 16px → ~10px.
- The existing `margin-inline: calc(-1 * var(--space-sm))` on `.card-grid` (line 146 of index.html) may need updating if the page padding changes. Planner should verify this compensates correctly after the side margin change.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 19-card-layout-expansion*
*Context gathered: 2026-04-16*
