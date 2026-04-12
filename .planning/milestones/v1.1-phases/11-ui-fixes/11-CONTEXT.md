# Phase 11: UI Fixes - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Visual overhaul and UX fixes for the CRATE dashboard and detail page. New logo, font selection, B&W palette enforcement, dynamic interactions via Magic MCP, and functional fixes (image loading, scrollbars, overlapping buttons, default item type, email branding). No new backend capabilities — listing quality fixes (irrelevant results, digital listings, Discogs location) are Phase 12.

</domain>

<decisions>
## Implementation Decisions

### Logo
- **D-01:** Add an image/icon logo — abstract vinyl-on-shelf concept. Diagonal lines evoking records standing side-on in a crate. Generate options via AI tooling and present to user for selection.
- **D-02:** Craft an AI generation prompt for the logo during planning. Present multiple options before committing.

### Colour Palette
- **D-03:** Site goes B&W at rest — only album artwork has colour. All UI elements (cards, badges, text, borders) are black, white, and greys when not interacted with.
- **D-04:** Functional colour (muted green for deals, muted red for destructive) appears ONLY on hover/interaction states — never at rest. Accents are desaturated/subtle, not vibrant.
- **D-05:** Background shifts to warm dark (#0d0b0a) instead of current #0a0a0a. Cards stay slightly lighter for contrast.

### Card System
- **D-06:** Deal indicators (badge "DEAL -X%") hidden at rest, fade in on card hover. No coloured left border — badge only.
- **D-07:** Empty/no-listing cards use minimal ghost treatment: 30-40% opacity, no border, art faded. Use a new placeholder asset file (user will provide) instead of current vinyl-placeholder.svg.
- **D-08:** Cards fill more of the viewport — reduce side margins so grid goes closer to edge-to-edge.

### Typography
- **D-09:** Revert text sizes to pre-Phase 10 scale (14→16→20→24px) or equivalent that keeps album covers as the visual hero. Text should be subordinate to artwork.
- **D-10:** New page font — Claude recommends font options during planning, user chooses. Must fit the brutalist B&W aesthetic.
- **D-11:** Email template (from Phase 9) updated to use same logo and title font as the main page.

### Dynamic UI
- **D-12:** Add hover effects, page transitions, and micro-interactions throughout. Energy level: subtle & refined base with occasional brutalist sharpness (instant cuts, no bounce/elastic easing). Think Linear's calm polish with raw edges.
- **D-13:** Magic MCP (21st.dev) MUST be used for all dynamic UI decisions. Present proposals to user before implementation — do not commit without sense-checking.
- **D-14:** No decorative animation. All motion must serve a purpose (reveal information, confirm action, guide attention).

### Functional Fixes
- **D-15:** Fix overlapping boxes/buttons in bottom-right of dashboard (BUG-01).
- **D-16:** Faster image loading — add loading state while waiting for artwork. After adding a new item, image should appear without requiring page reload.
- **D-17:** Custom scrollbar styling — fix gross scrollbar in typeahead dropdown, add styled scrollbar on main page. Keep consistent with B&W palette.
- **D-18:** Default item type to "album" in add form.

### Claude's Discretion
- Exact opacity values for ghost cards (within 30-40% range)
- Scrollbar styling details (width, track/thumb colours)
- Loading state design (skeleton, spinner, or fade)
- Warm dark background exact hex value (near #0d0b0a)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Templates (primary files to modify)
- `app/templates/index.html` — Dashboard: card grid, stats bar, modals, typeahead
- `app/templates/item_detail.html` — Detail page: headings, listings, scan button
- `app/templates/base.html` — Base template: nav, logo, shared scripts/styles

### Styles
- `static/style.css` — Main CSS: all design tokens, card classes, grid, modal styles

### Email
- `app/templates/deal_alert.html` — Email template (Phase 9 output) — needs logo + font update

### Prior phase context
- `.planning/phases/04-ui-polish/04-CONTEXT.md` — CRATE naming, dark palette, sharp edges
- `.planning/phases/10-ui-polish/10-CONTEXT.md` — Design token system, card tiers, typography scale (being reverted)

### Design audit
- `ui-to-improve.txt` — Original UI analysis (reference only, not the driver for this phase)

### Requirements
- `.planning/REQUIREMENTS.md` — BUG-01 (overlapping buttons)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- CSS custom properties layer (`--color-*`, `--text-*`, `--space-*`) — all changes go through tokens
- Card tier classes (`.card--deal`, `.card--empty`, `.card--scanning`) — need modification for B&W-at-rest
- Button states (`:focus-visible`, `:active`, `:disabled`) already implemented
- Typeahead JS in `static/typeahead.js`
- Bodoni Moda Bold font already self-hosted at `static/fonts/`

### Established Patterns
- Design tokens as CSS custom properties
- Jinja2 templates with inline `<script>` blocks
- Dark-only theme (now shifting to warm dark B&W)

### Integration Points
- Card grid in `index.html` — margin/width changes for fuller viewport
- Deal badge visibility — currently always-on, needs hover-only CSS
- Typeahead dropdown in `index.html` — scrollbar styling
- Image loading in card template — needs loading state + JS refresh after add
- Nav logo area in `base.html` — new icon logo placement

</code_context>

<specifics>
## Specific Ideas

- Logo concept: "vinyl on a shelf from side on" — abstract diagonal lines like records standing in a crate. AI-generated, multiple options presented for user choice.
- Dynamic UI must be sense-checked with user before implementation. Use Magic MCP (21st.dev) for inspiration and component patterns.
- "Focus on album covers" — typography and layout should make artwork the dominant element. Text is utilitarian.
- B&W at rest with colour-on-hover creates a "gallery wall" feel — clean monochrome that comes alive when you engage.
- Font recommendations needed during planning — user will choose from options. Must fit brutalist B&W aesthetic.

</specifics>

<deferred>
## Deferred Ideas

### Phase 12: Listing Quality (new phase)
- Too many irrelevant results under listings (different named releases)
- Filter out digital-only listings
- Discogs listings always have no location data

### Reviewed Todos (not folded)
- **Add manual selection of Discogs link or album** — TYPE-05/TYPE-06, belongs in v2
- **Fix typeahead spinner not clearing** — folded into Phase 10, verify it's resolved

</deferred>

---

*Phase: 11-ui-fixes*
*Context gathered: 2026-04-10*
