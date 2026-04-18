# Phase 16: Visual Foundation - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Shift the visual foundation to a true black, Warner Music–inspired aesthetic and style scrollbars to match. No backend/data changes. Affects `static/style.css` only — all templates use CSS variables.

</domain>

<decisions>
## Implementation Decisions

### True Black (VIS-01)
- **D-01:** `--color-bg`, `--color-surface`, and `--color-surface-alt` all go to `#000000`
- **D-02:** Separation between page and card surfaces is achieved via `--color-border: #222222` (unchanged) — no surface elevation, no near-black fallbacks
- **D-03:** Skeleton pulse animation in `.card-artwork-wrapper` uses `#0a0a0a` / `#141414` (slightly lifted from #000 so the animation is still visible)

### Scrollbar Styling (VIS-02)
- **D-04:** Full rework — width drops to `4px`, track goes `transparent`, thumb is `rgba(255,255,255,0.2)` at rest and `rgba(255,255,255,0.4)` on hover
- **D-05:** Apply to both global page-level scrollbar AND in-component scrollers: `.typeahead-dropdown` and `.table-container` (these have `overflow-y: auto` / `overflow-x: auto` today)
- **D-06:** Firefox scrollbar updated to match: `scrollbar-color: rgba(255,255,255,0.2) transparent`

### Warner Music Aesthetic Direction (VIS-03)
- **D-07:** Accent color stays white (`#ffffff`) — no shift to gold or red; Warner Music's digital editorial direction is stark white-on-black (confirmed by reference screenshot)
- **D-08:** "Restraint" means no new decorative additions. Existing spacing scale and border-radius tokens are unchanged.
- **D-09:** Warner Music direction is expressed through the flat black surface change (D-01/D-02) rather than any new accent, texture, or animation

### Claude's Discretion
- Minor border color tweaks (e.g. `--color-border-muted`) if the shift to #000 makes them invisible
- Whether skeleton pulse colors (D-03) read correctly — adjust if animation disappears against #000

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §VIS-01, §VIS-02, §VIS-03 — Acceptance criteria for this phase

### Design reference
- Reference screenshot: Warner Music website (vinyl product grid) — true black, stark white text, no card chrome, editorial restraint

### Codebase
- `static/style.css` — Entire change surface; `:root` variables (section 1) control bg/surface; section 19 controls scrollbars
- `templates/base.html`, `templates/index.html`, `templates/item_detail.html` — Templates; all colors via CSS vars, no hardcoded hex

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `static/style.css` section 1 (`:root`): all colour tokens are already CSS custom properties — VIS-01 is a 3-line variable swap
- `static/style.css` section 19: scrollbar CSS exists for both WebKit and Firefox; full rework replaces these blocks

### Established Patterns
- All templates use CSS variables exclusively (no hardcoded hex in templates)
- CRATE design system uses 0px border-radius throughout — Warner Music direction is compatible
- `--color-surface-alt` is used as the background for form inputs, nav bar, and typeahead dropdown — going to #000 keeps it consistent

### Integration Points
- `.card-artwork-wrapper` has a skeleton animation that uses `#1a1a1a` / `#2a2a2a` — these are hardcoded in `style.css` section 15, not variables; they will need updating to be visible against #000
- `.typeahead-dropdown` has `overflow-y: auto` and no explicit scrollbar styling — VIS-02 scope should add matching scrollbar rules here
- `.table-container` has `overflow-x: auto` — same treatment needed for VIS-02 scope

</code_context>

<specifics>
## Specific Ideas

- Reference: Warner Music website (vinyl product grid screenshot shared during discussion) — shows #000 background, artwork directly on black, no card chrome/borders, stark white text below. The "no card chrome" approach is what the v1.3 milestone calls "restraint".
- The existing border-only separation (D-02) already matches the Warner Music reference more than surface elevation would.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 16-visual-foundation*
*Context gathered: 2026-04-14*
