# Phase 10: UI Polish - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Final UI polish pass after phases 6-9. Design tool-driven improvement of the dashboard and detail page — audit the current UI with `/design-for-ai`, then implement improvements using `magic MCP`, `stitch`, and `ui-ux-pro-max`. Remaining mechanical fixes (card titles, H2 token, disabled buttons, token cleanup) are folded into the design-driven work. No new backend capabilities.

</domain>

<decisions>
## Implementation Decisions

### Design Tooling Workflow
- **D-01:** This phase is design tool-driven. Run `/design-for-ai` to audit the current UI and identify improvements. Then use `magic MCP` (`mcp__magic__*`), `stitch` (`mcp__stitch__*`), and `ui-ux-pro-max` skill to design and implement changes.
- **D-02:** The audit surfaces the scope — improvements go beyond the original UIP requirement list. The 4 remaining mechanical fixes are folded into the broader design work, not treated as the entire phase.

### Card Title Sizing (UIP-02)
- **D-03:** Claude's discretion — pick the simplest approach that bumps card titles from 14px (`--text-sm`) to 16px, meeting UIP-02.

### H2 Token Formalization (UIP-03, UIP-10)
- **D-04:** Create a new `--text-subheading` CSS custom property at 22px. Replace inline `style="font-size: 22px"` on detail page H2s with this token. Keeps H1 (`--text-heading`: 28px) and H2 visually distinct via the token system.

### Disabled Button Scope (UIP-06)
- **D-05:** Both "Scan Now" (detail page) and "Scan All" (dashboard) get `:disabled` styling (opacity: 0.5, cursor: not-allowed). Applied while a scan is running.

### Already Implemented (from Phase 5 — verify, don't reimplement)
- **D-06:** The following requirements were implemented in Phase 5 and survived through phases 6-9. Verify they still work; fix only if regressed:
  - UIP-01: `--color-text-faint: #686868` (WCAG AA contrast)
  - UIP-04: `:focus-visible` ring on all button classes
  - UIP-05: `:active` scale(0.97) micro-interaction
  - UIP-07: Modal `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus management
  - UIP-08: Inline delete confirmation (no native `confirm()`)
  - UIP-09: 3-column grid at 1024px breakpoint
  - BUG-01: Overlapping buttons (not reproduced in current code — verify visually)

### Design Audit Findings (from `/design-for-ai` checker + `ui-to-improve.txt`)

Three interconnected FLAGs: Typography (2), Composition (4), Visual Hierarchy (5) — all stem from the same root: compressed type scale and uniform spacing.

- **D-07:** Widen the type scale to a 3:4 proportional ratio. Recommended tokens:
  - `--text-label: 12px` (metadata, secondary labels)
  - `--text-sm: 14px` (backward compat, body-adjacent)
  - `--text-body: 16px` (unchanged)
  - `--text-title: 21px` (card album names — currently 14px, smaller than body)
  - `--text-price: 28px` (core value signal — was 20px)
  - `--text-heading: 36px` (page-level headings — was 28px)
  - `--text-heading-secondary: 21px` ("All Listings" — distinct from "Best Deals")
- **D-08:** Introduce 3-tier spacing hierarchy:
  - Intra-card: 6–8px
  - Inter-card: 16px
  - Inter-section: 40–48px
  - Currently everything is 24px — no grouping signal
- **D-09:** Create deal/no-deal visual distinction on dashboard cards:
  - **Tier 1 (deal cards):** Left border accent or highlighted background, price at 20–24px, deal percentage badge
  - **Tier 2 (normal cards):** Standard card, price readable but un-emphasized
  - **Tier 3 (no-listing / scanning cards):** Lower opacity (0.45–0.55), muted border or dashed — visually recedes
- **D-10:** Upgrade stats bar from 14px metadata to page-level summary prominence — stat values at 22–24px/600, stat labels at 11–12px/400 muted
- **D-11:** Strip table row borders (`border-top`) — rely on row padding (10–12px) and hover state. Right-align numeric columns. (Tufte 1+1=3 principle)
- **D-12:** Once size carries hierarchy, reduce card title weight from 600→500. Price stays 700. Weight *reinforces* size, not substitutes.
- **D-13:** Consider monospace/slab typeface for prices only (e.g., JetBrains Mono) — distinguishes data from labels within two-family limit. Claude's discretion on whether this adds enough value.

### Folded Todos
- **Fix typeahead spinner not clearing** — spinner visibility bug after keyboard selection or type change. Fix as part of this phase's UI cleanup.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — UIP-01 through UIP-10, BUG-01 requirement definitions with exact values

### Templates (primary files to modify)
- `app/templates/index.html` — Dashboard: card grid, stats bar, scan panel, modals, typeahead JS
- `app/templates/item_detail.html` — Detail page: H1/H2 headings, scan button, delete confirmation
- `app/templates/base.html` — Base template: nav, modal JS, shared scripts

### Styles
- `app/static/css/style.css` — Main CSS: all design tokens, button classes, grid, modal styles

### Prior phase context (design decisions already locked)
- `.planning/phases/04-ui-polish/04-CONTEXT.md` — Phase 4: CRATE naming, dark palette, sharp edges, spacing, wordmark
- `.planning/phases/05-improve-ui-and-ux-design/05-CONTEXT.md` — Phase 5: accessibility fixes, typography, grid, button states (most already implemented)

### Design audit sources
- `ui-to-improve.txt` — Original UI analysis with contrast ratios and code snippets
- `.planning/phases/10-ui-polish/10-DESIGN-AUDIT.md` — `/design-for-ai` checker results: 10-point audit, deep dives on typography/composition/hierarchy, recommended token changes, convergent intervention list

### Todo reference
- `.planning/todos/pending/2026-04-07-fix-typeahead-spinner-not-clearing.md` — Spinner bug details

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- CSS custom properties layer (`--color-*`, `--text-*`, `--space-*`) — all changes go through tokens
- Button classes (`.btn-cta`, `.btn-secondary`, `.btn-destructive`) already have `:focus-visible` and `:active` states
- Modal JS in `base.html` already has focus management

### Established Patterns
- Design tokens as CSS custom properties — no hardcoded values in component rules
- Jinja2 templates with inline `<script>` blocks for interactivity
- Dark-only theme (no light mode)

### Integration Points
- Card title class in `index.html` (`<h3 class="text-sm">`) — needs class change for UIP-02
- H2 inline styles in `item_detail.html` — need replacement with token-based class
- Scan button onclick handlers — need disabled state toggling during scan
- Typeahead JS in `index.html` — spinner clearing bug fix

</code_context>

<specifics>
## Specific Ideas

- Phase is design tool-driven: `/design-for-ai` audits first, then `magic MCP` + `stitch` + `ui-ux-pro-max` implement. The audit may surface improvements beyond the original UIP list.
- The CRATE aesthetic is locked: near-black neutral, white accent, sharp edges, dense spacing (Phase 4 decisions).
- "Majorly increase the impact of the UI" — this isn't just mechanical fixes, it's a design uplift.
- **Audit convergence:** All three FLAGs (typography, composition, visual hierarchy) point to the same 6 interventions — widen type scale, introduce spacing tiers, deal/no-deal card distinction, stats bar upgrade, section heading differentiation, strip table row borders.
- **Fix order from audit:** Spacing tiers first (zero cost, highest impact) → widen size range on price/stats → strip table borders → weight adjustments last.
- **Kadavy hierarchy order:** White space first, then weight, then size, then color, then ornamentation. Current design inverts this — weight doing all the work.

</specifics>

<deferred>
## Deferred Ideas

### Reviewed Todos (not folded)
- **Add manual selection of Discogs link or album** — this is a typeahead/Phase 6 feature extension, not UI polish. Belongs in v2 (TYPE-05/TYPE-06).

</deferred>

---

*Phase: 10-ui-polish*
*Context gathered: 2026-04-07 (updated 2026-04-08 with design audit)*
