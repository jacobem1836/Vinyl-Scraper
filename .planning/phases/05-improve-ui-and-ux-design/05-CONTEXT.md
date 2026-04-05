# Phase 5: Improve UI and UX Design - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning
**Source:** PRD Express Path (ui-to-improve.txt)

<domain>
## Phase Boundary

This phase delivers a comprehensive UI/UX polish pass on both the dashboard (`index.html`) and detail page (`item_detail.html`). It addresses 10 prioritised issues identified by a detailed design audit — covering accessibility failures, missing interaction states, typography hierarchy problems, layout gaps, and color system fixes. No backend changes required; all work is CSS, HTML, and JavaScript in the frontend templates and static assets.

</domain>

<decisions>
## Implementation Decisions

### Priority 1 — Accessibility: text-faint contrast failure (WCAG AA)
- Bump `--color-text-faint` from `#555555` to `#686868` (achieves ~4.5:1 ratio on `#0a0a0a`)
- Affects all secondary info at 14px: "No listings found yet", price sub-labels, timestamps, separator pipes

### Priority 2 — Accessibility: No :focus-visible on buttons
- Add `box-shadow: 0 0 0 2px var(--color-accent)` to `.btn-cta:focus-visible`, `.btn-secondary:focus-visible`, `.btn-destructive:focus-visible`
- Form inputs already use this pattern — buttons must match

### Priority 3 — Accessibility: Modal focus management broken
- On modal open: move focus to first focusable element inside modal (`input, select, textarea, button`)
- On modal close: return focus to the trigger button (`openBtn.focus()`)
- Add `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to modal title

### Priority 4 — Accessibility: Touch targets below 44px
- Set `min-height: 44px` on `.btn-cta`, `.btn-secondary`, `.btn-destructive`
- `.btn-cta` currently has `min-height: 40px` — bump to 44px

### Priority 5 — Typography: H1 and H2 are visually identical
- Bump `--text-heading` (H1/page title) to 28–30px
- Keep H2 section headings at 22–24px (currently inline `style` attributes on detail page)
- Creates genuine distinction between page title and section titles

### Priority 6 — Layout: Missing 3-column grid breakpoint
- Add `@media (min-width: 1024px) { .card-grid { grid-template-columns: repeat(3, 1fr); } }`
- Currently jumps 2-col → 4-col at 1280px, skipping the laptop/tablet range (1024–1279px)

### Priority 7 — Spacing: 12px values outside the token system
- Replace `12px` hard-coded values in `.card-body` padding and `.card-grid { gap }` with `var(--space-sm)` (8px) or `var(--space-md)` (16px) depending on visual intent

### Priority 8 — Interaction: No :active state on buttons
- Add `transform: scale(0.97)` at `:active` to all three button classes
- Provides physical press feedback (100ms micro-interaction)

### Priority 9 — Color: Shadows invisible on near-black background
- `.card:hover { box-shadow: ... rgba(0,0,0,0.6) }` is undetectable on `#0a0a0a`
- Replace with `box-shadow: 0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0, 5, 20, 0.8)` for a subtle hover aura that reads on dark backgrounds

### Priority 10 — Interaction: Native confirm() for delete
- Replace `confirm()` browser dialog on delete actions with an inline confirmation state
- Button changes to "Confirm?" + "Cancel" inline pattern — no browser chrome, consistent with design language

### Claude's Discretion
- Exact pixel values for H2 (within 22–24px range)
- Whether to use `var(--space-sm)` or `var(--space-md)` for the 12px replacement (judge by visual output)
- Inline confirmation pattern implementation details (toggle state, timeout, or persistent until dismissed)
- Whether to update `.btn-cta:disabled` opacity/cursor as part of the disabled state work noted in the audit (mentioned in analysis but not in priority list — include if trivial, skip if complex)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Templates (primary files to modify)
- `app/templates/index.html` — Dashboard template (card grid, stats bar, scan panel, modal)
- `app/templates/item_detail.html` — Detail page template (H1/H2 headings, Best Deals, All Listings table)

### Styles
- `app/static/css/style.css` — Main CSS file; contains all design tokens, card styles, button classes, grid, modal

### JavaScript
- `app/static/js/main.js` — Client-side JS; contains modal open/close logic (focus management fix lives here)

### Design audit (source of truth for this phase)
- `ui-to-improve.txt` — Full in-depth UI analysis with exact hex values, contrast ratios, and code snippets

</canonical_refs>

<specifics>
## Specific Ideas

From the audit (exact values to use):

**Color fix:**
- `--color-text-faint: #686868` (from `#555555`)

**Shadow fix:**
```css
.card:hover {
  box-shadow: 0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0, 5, 20, 0.8);
}
```

**Focus-visible fix:**
```css
.btn-cta:focus-visible,
.btn-secondary:focus-visible,
.btn-destructive:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-accent);
}
```

**Active state:**
```css
.btn-cta:active,
.btn-secondary:active,
.btn-destructive:active {
  transform: scale(0.97);
}
```

**Modal focus pattern:**
```js
// On open:
modal.querySelector('input, select, textarea, button').focus();
// On close:
openBtn.focus();
```

**Grid breakpoint:**
```css
@media (min-width: 1024px) {
  .card-grid { grid-template-columns: repeat(3, 1fr); }
}
```

</specifics>

<deferred>
## Deferred Ideas

From the audit — noted but NOT in the priority fix list (do not implement in this phase):
- Monospace/slab typeface for prices (JetBrains Mono / Roboto Mono) — would add a new font dependency
- Fluid typography with `clamp()` — type is fixed pixels and works adequately at current sizes
- Warm/cool tint to surfaces for depth (`#0f1012` vs `#111111`) — palette temperature change
- Deal badge / visual hierarchy indicator on "best deal" card — information architecture change, larger scope
- Scan panel expand/collapse transition — not in priority list
- No-h1 on dashboard — personal tool, SEO irrelevant

</deferred>

---

*Phase: 05-improve-ui-and-ux-design*
*Context gathered: 2026-04-05 via PRD Express Path*
