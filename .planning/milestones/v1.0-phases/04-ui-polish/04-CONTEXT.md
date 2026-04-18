# Phase 4: UI Polish - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Redesign the visual aesthetic of the existing custom CSS design system — new dark non-blue palette, white accent, sharp edges, tighter spacing, app renamed to CRATE with a styled wordmark. Higher-res Discogs artwork via release endpoint. No new capabilities; all changes are within the existing Jinja2 templates and `static/style.css`.

</domain>

<decisions>
## Implementation Decisions

### App Name
- **D-01:** Rename the application to **CRATE**. The name is literal — the dashboard simulates a record crate, a collection of records you're hunting for.
- **D-02:** Update all page titles, nav, and any headings that reference the old name.

### Colour Palette
- **D-03:** Replace the current blue-tinted slate palette with a near-black neutral scheme. No blue cast — sleek and slick, Apple dark mode / Vercel dashboard territory.
  - `--color-bg`: `#0a0a0a`
  - `--color-surface`: `#111111`
  - `--color-border`: `#222222`
  - `--color-text`: `#f5f5f5`
  - `--color-text-muted`: `#777777`

### Accent Colour
- **D-04:** Replace amber/gold (`#f59e0b`) with **white** as the accent colour.
  - `--color-accent`: `#ffffff`
  - `--color-accent-hover`: `#e0e0e0`
  - `--color-cta-bg`: `#ffffff`
  - `--color-cta-text`: `#0a0a0a`
- **D-05:** All type badges (album, artist, label) and source badges must be audited — amber/gold references removed and updated to use the white accent or neutral variants.

### Border Radius
- **D-06:** Sharp edges everywhere — no rounded excess.
  - Cards: `border-radius: 0`
  - Containers, modals, panels: `border-radius: 0`
  - Buttons: `border-radius: 2px` (barely perceptible, functional only)
  - Badges: `border-radius: 2px`

### Spacing
- **D-07:** Compress spacing overall — denser grid, more records visible at once.
  - Card padding: `12px` (was `16px`)
  - Grid gap: `12px` (was `16px`)
  - Section gap: `20px` (was `24px`)

### Nav Title (Wordmark)
- **D-08:** Nav title displays as `C R A T E` — all caps, letter-spacing `0.25em`, font-weight `700`. Clean wordmark treatment, no logo mark or icon.

### Discogs Artwork Quality
- **D-09:** Upgrade artwork fetching from the Discogs search thumbnail to the full-res image via the Discogs release endpoint. The `artwork_url` stored on `WishlistItem` should point to the release image (typically `images[0].uri`) rather than the search result `cover_image` thumbnail.

### Claude's Discretion
- Exact font-size and line-height for the CRATE wordmark in the nav
- Badge colour variants after amber removal (white-tinted, grey-tinted, or purely neutral)
- Any hover/focus state adjustments needed after palette swap

</decisions>

<specifics>
## Specific Ideas

- "Super sleek and slick" — the target aesthetic. Think Linear, Vercel, Apple dark mode. Not warm, not vintage, not cozy.
- The dashboard is literally a record crate — CRATE is both a metaphor and the feature description.
- `C R A T E` wide-tracked wordmark: typography alone, no logo mark needed.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing design system
- `static/style.css` — Full current CSS design system; all token variable names are defined here. This is the primary file to modify.
- `templates/base.html` — Nav, page shell, scan polling JS; CRATE rename happens here.
- `templates/index.html` — Dashboard card grid.
- `templates/item_detail.html` — Detail page; listing rows and cost breakdown.

### Data model
- `app/models.py` — `WishlistItem.artwork_url` column; stores the Discogs image URL used by the proxy endpoint.
- `app/services/discogs.py` — Discogs adapter; artwork capture logic lives here. Release endpoint upgrade goes here.

### Prior phase context (design decisions already locked)
- `.planning/phases/03-ui-redesign/03-CONTEXT.md` — Phase 3 decisions: card grid layout, artwork proxy endpoint, FX cost breakdown, dark palette rationale. Phase 4 polishes on top of these — do not re-litigate them.

### No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `static/style.css` CSS custom properties layer — all colour and spacing changes are CSS variable updates only; no component logic changes needed for palette/spacing work.
- Scan polling JS in `base.html` — keep as-is, just restyled via updated tokens.
- Artwork proxy endpoint (`GET /api/artwork`) — keep as-is; only the URL stored in `artwork_url` changes (higher-res source).

### Established Patterns
- CSS custom properties (`--color-*`, `--space-*`) are the design token layer — downstream agents should update variables, not hardcoded values scattered in rules.
- `cachetools.TTLCache` pattern used for FX rates — not affected by this phase.

### Integration Points
- `WishlistItem.artwork_url` → Discogs adapter `_build_listing()` or search handler → switch from `cover_image` (thumbnail) to `images[0].uri` (full-res) via release endpoint call.
- Nav `base.html` title text → rename to CRATE + apply wordmark CSS class.

</code_context>

<deferred>
## Deferred Ideas

### Discogs manual release selection
Auto-match sometimes picks the wrong release (e.g. Hamilton soundtrack — wrong pressing/year). The user wants to be able to manually search Discogs and pin the correct release to a wishlist item (stores a Discogs release ID; artwork and listings pull from that pinned ID). This is a new UI capability — detail page changes + Discogs API search + new model field. Defer to a future phase.

</deferred>

---

*Phase: 04-ui-polish*
*Context gathered: 2026-04-03*
