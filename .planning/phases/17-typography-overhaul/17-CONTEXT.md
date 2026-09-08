# Phase 17: Typography Overhaul - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Swap body/card typography to a thinner, crispier gothic typeface and apply a hierarchy where item name is larger and heavier than price. No backend changes, no layout restructuring — CSS and font files only.

Requirements in scope: TYPO-01, TYPO-02, TYPO-03.

</domain>

<decisions>
## Implementation Decisions

### Typeface (TYPO-01)
- **D-01:** Replace Inter with a light gothic font — Gothic A1 or closest equivalent available as a woff2. A "gothic geometric" character: thin strokes, clean letterforms, crispness at small sizes.
- **D-02:** The new font applies to both text and numbers — price figures must render in the gothic font, not system numerics.
- **D-03:** Download and self-host as woff2 in `/static/fonts/`. Update `@font-face` and `--font-sans`. No CDN dependency.
- **D-04:** Bodoni Moda stays as-is — nav brand mark only. No change to `--font-display` usage.

### Card Hierarchy (TYPO-02)
- **D-05:** Item name goes UP; price goes DOWN. Specific targets: name ~22–24px / weight 400–500; price ~16–18px / weight 300–400.
- **D-06:** Price becomes a supporting detail under the name — not the visual hero of the card. This inverts the current 18px/400 name vs 28px/600 price relationship.
- **D-07:** Update `--text-title` and `--text-price` tokens in `:root`. The utility classes `.text-title` and `.card-price` inherit from these — no template changes needed for cards.

### Detail Page + Modals (TYPO-03)
- **D-08:** Font swap propagates automatically via `--font-sans` — no per-template changes needed for the font itself.
- **D-09:** Item detail page: item name is `h1.text-heading` (24px). Already outranks listing prices visually. No size changes needed — font swap delivers TYPO-03 here.
- **D-10:** Add/Edit modals are form UIs (not name/price surfaces) — their headings get the gothic font via inheritance, no explicit hierarchy work needed.

### Claude's Discretion
- Exact weight values within the specified ranges (name 400–500, price 300–400) — choose what reads best with the gothic font
- Whether Gothic A1 specifically or a close equivalent (e.g. Barlow Light, DM Sans Light) — select based on woff2 availability and visual match to the gothic brief
- Numeric letterform quality — prioritise fonts with strong tabular numeral rendering for prices

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §TYPO-01, §TYPO-02, §TYPO-03 — Acceptance criteria for this phase

### Codebase — change surfaces
- `static/style.css` lines 10–24 — `@font-face` declarations (Bodoni Moda, Inter); new gothic font goes here
- `static/style.css` lines 91–103 — Typography tokens in `:root` (`--text-title`, `--text-price`, `--font-sans`, etc.)
- `static/style.css` lines 532–551 — Typography utility classes (`.text-title`, `.card-price`, `.text-price`)
- `templates/base.html` lines 7–8 — Font preload links; must be updated to point to new gothic woff2
- `templates/index.html` lines 186–188 — Card markup (`h3.text-title` + `span.card-price price-best`); inherits from CSS tokens
- `templates/item_detail.html` line 33 — Item name (`h1.text-heading`, 24px); inherits font via `--font-sans`

### Prior phase context
- `.planning/phases/16-visual-foundation/16-CONTEXT.md` — Warner Music aesthetic direction (restraint, stark white on black, no decorative additions)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `--font-sans` CSS variable: single token controls body font across all surfaces — gothic swap is a one-variable change plus `@font-face` block
- Inter Variable woff2 at `/static/fonts/Inter-VariableFont_opsz,wght.woff2` — can be removed or kept as fallback
- Typography token system already in place (`--text-title`, `--text-price`, etc.) — hierarchy change is a token value update, not a refactor

### Established Patterns
- All templates use CSS variables exclusively (no hardcoded font stacks in templates)
- Font loading uses `font-display: swap` for body — same strategy for gothic replacement
- CRATE design system expects `--font-sans` to be the primary body font; changing it updates all body text site-wide

### Integration Points
- `h3.text-title` on cards (index.html:186) and the bottom-right scan summary card (index.html:186) both use `.text-title` — token change covers both
- `span.card-price` on cards and `.text-price` on item detail listings both pull from CSS token — one update covers both surfaces
- `templates/base.html` preload hints must be updated to the new font filename; stale preloads for Inter can be removed

</code_context>

<specifics>
## Specific Ideas

- Gothic A1 was named explicitly as a reference point — it's a Google Font with Light (300) and Regular (400) weights, clean geometric sans-serif with Korean/Latin coverage. If sourcing as woff2, use the Latin subset only for file size.
- "This should be for the numbers as well" — the gothic font must handle price rendering, not fall back to system fonts for numerals. Verify the chosen font has full numeral coverage.

</specifics>

<deferred>
## Deferred Ideas

- **Item detail artwork 2–3× enlargement** — User wants the record artwork on the item detail page to be much larger (2–3× current width/height). This is a layout restructuring task, not typography. Out of scope for Phase 17. Candidate for Phase 18 or a dedicated layout phase after Phase 18.

</deferred>

---

*Phase: 17-typography-overhaul*
*Context gathered: 2026-04-15*
