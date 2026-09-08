# Phase 4: UI Polish — Research

**Researched:** 2026-04-03
**Domain:** CSS design token update, Jinja2 template text edits, Discogs release endpoint artwork upgrade
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Rename the application to **CRATE**. The name is literal — the dashboard simulates a record crate, a collection of records you're hunting for.
- **D-02:** Update all page titles, nav, and any headings that reference the old name.
- **D-03:** Replace the current blue-tinted slate palette with a near-black neutral scheme. No blue cast — sleek and slick, Apple dark mode / Vercel dashboard territory.
  - `--color-bg`: `#0a0a0a`
  - `--color-surface`: `#111111`
  - `--color-border`: `#222222`
  - `--color-text`: `#f5f5f5`
  - `--color-text-muted`: `#777777`
- **D-04:** Replace amber/gold (`#f59e0b`) with **white** as the accent colour.
  - `--color-accent`: `#ffffff`
  - `--color-accent-hover`: `#e0e0e0`
  - `--color-cta-bg`: `#ffffff`
  - `--color-cta-text`: `#0a0a0a`
- **D-05:** All type badges and source badges must be audited — amber/gold references removed and updated to use the white accent or neutral variants.
- **D-06:** Sharp edges everywhere — no rounded excess.
  - Cards: `border-radius: 0`
  - Containers, modals, panels: `border-radius: 0`
  - Buttons: `border-radius: 2px`
  - Badges: `border-radius: 2px`
- **D-07:** Compress spacing overall — denser grid, more records visible at once.
  - Card padding: `12px` (was `16px`)
  - Grid gap: `12px` (was `16px`)
  - Section gap: `20px` (was `24px`)
- **D-08:** Nav title displays as `C R A T E` — all caps, letter-spacing `0.25em`, font-weight `700`.
- **D-09:** Upgrade artwork fetching from Discogs search thumbnail to full-res image via the Discogs release endpoint. `artwork_url` should point to `images[0].uri` rather than the search result `cover_image` thumbnail.

### Claude's Discretion

- Exact font-size and line-height for the CRATE wordmark in the nav
- Badge colour variants after amber removal (white-tinted, grey-tinted, or purely neutral)
- Any hover/focus state adjustments needed after palette swap

### Deferred Ideas (OUT OF SCOPE)

- Discogs manual release selection (pin a specific release ID per wishlist item; new UI + model field). Defer to a future phase.
</user_constraints>

---

## Summary

Phase 4 is a focused visual polish pass on an already-functional Jinja2 + FastAPI application. All UI work is CSS token replacement and template text edits — no new HTML structure, no new JavaScript, no new Python dependencies. The design system is already tokenised (CSS custom properties on `:root`); the executor's primary job is updating those token values and replacing all `border-radius` rules to enforce sharp edges.

The only backend change is in `app/services/discogs.py`: upgrade the artwork capture path from the search `cover_image` thumbnail to `images[0].uri` from the release endpoint. The release endpoint is already being called in the album scan loop (`/releases/{release_id}`) — the artwork is right there in the response. The change is to extract `images[0].uri` from that detail response and attach it as the cover image, rather than pulling `cover_image` from the search result.

The UI-SPEC (04-UI-SPEC.md) is fully resolved and provides all exact values. Research confirms the spec is implementable as written with no surprises.

**Primary recommendation:** Work file-by-file in a single wave: (1) `static/style.css` token updates + radius + keyframe + `.nav-brand`, (2) `templates/base.html` rename + wordmark class, (3) `templates/index.html` empty state copy, (4) `templates/item_detail.html` rename + delete button copy, (5) `app/services/discogs.py` artwork upgrade.

---

## Standard Stack

### Core

No new dependencies. Phase 4 uses only what Phase 3 established.

| Library | Version | Purpose | Note |
|---------|---------|---------|------|
| CSS Custom Properties | Native | Design token layer | All colour/spacing changes are variable updates only |
| Jinja2 | 3.1.4 | Template engine | Text edits only — no structural changes |
| Discogs REST API | v2 | Release endpoint for artwork | Already in use; `images` field confirmed present with auth token |

### No Additions Required

No `npm install`, no `pip install`, no new imports.

---

## Architecture Patterns

### Established Pattern: Token-First Updates

The existing `static/style.css` already follows a strict CSS custom properties pattern. All colour, spacing, and typography values flow from `:root` variables. This means:

- Palette changes require updating `:root` values only — every component that uses `var(--color-accent)` updates automatically.
- Radius changes require updating every `border-radius` property directly (the Phase 3 system did not tokenise radius — Phase 4 introduces `--radius-*` tokens).
- Spacing compression is a component-level override (not `:root` token change) because the global tokens stay at their Phase 3 values; only `.card-body`, `.card-grid`, and `.section-gap` are compressed.

### Token Inventory — What Exists vs What Changes

**Currently in `:root` (Phase 3 values), to be replaced:**

```css
/* Phase 3 → Phase 4 replacements */
--color-bg:           #0f172a  →  #0a0a0a
--color-surface:      #1e293b  →  #111111
--color-surface-alt:  #0f172a  →  #0a0a0a
--color-border:       #334155  →  #222222
--color-border-muted: #1e293b  →  #111111
--color-text:         #f8fafc  →  #f5f5f5
--color-text-muted:   #94a3b8  →  #777777
--color-text-faint:   #64748b  →  #555555
--color-accent:       #f59e0b  →  #ffffff
--color-accent-hover: #fbbf24  →  #e0e0e0
--color-accent-bg:    #78350f  →  rgba(255,255,255,0.08)
--color-accent-cta:   #f59e0b  →  #ffffff
--color-cta-text:     #0f172a  →  #0a0a0a
/* Badge tokens — replace amber tints with desaturated variants (per UI-SPEC) */
/* Source badge tokens — replace amber Discogs variant with neutral grey-white */
```

**New tokens to add (radius):**

```css
--radius-card:    0px;
--radius-modal:   0px;
--radius-btn:     2px;
--radius-badge:   2px;
--radius-input:   2px;
```

### Radius Audit — All Hardcoded Values in Phase 3 CSS

Phase 3 did not use radius tokens; all radius values are hardcoded in component rules. The executor must find and replace each:

| Rule/Selector | Phase 3 value | Phase 4 value |
|---|---|---|
| `.card` | `border-radius: 8px` | `border-radius: var(--radius-card)` → 0 |
| `.card-artwork` | `border-radius: 4px 4px 0 0` | `border-radius: 0` |
| `.modal-panel` | `border-radius: 12px` | `border-radius: var(--radius-modal)` → 0 |
| `.scan-card` | `border-radius: 12px` | `border-radius: 0` |
| `.scan-pill` | `border-radius: 9999px` | `border-radius: 2px` |
| `.table-container` | `border-radius: 12px` | `border-radius: 0` |
| `.btn-cta` | `border-radius: 6px` | `border-radius: var(--radius-btn)` → 2px |
| `.btn-secondary` | `border-radius: 6px` | `border-radius: var(--radius-btn)` → 2px |
| `.btn-destructive` | `border-radius: 6px` | `border-radius: var(--radius-btn)` → 2px |
| `.badge` | `border-radius: 9999px` | `border-radius: var(--radius-badge)` → 2px |
| `.form-input` | `border-radius: 6px` | `border-radius: var(--radius-input)` → 2px |
| `.empty-state` | `border-radius: 12px` | `border-radius: 0` |
| `.toast` | `border-radius: 8px` | `border-radius: 0` |
| `.spinner` | `border-radius: 50%` | KEEP 50% — spinners must remain circular |

**Note:** `.spinner` uses `border-radius: 50%` for its circular shape — this is functional, not decorative. Do NOT change it.

**Inline styles in templates:** `item_detail.html` line 22 and line 28 have `border-radius: 8px` inline on the artwork `<img>` elements. These must be updated to `border-radius: 0` as part of the template edit.

### Spinner Token Update

The `.spinner` uses hardcoded `#f59e0b` (amber) in its border colour:

```css
/* Phase 3 */
border: 2px solid rgba(245, 158, 11, 0.3);
border-top-color: #f59e0b;
```

Phase 4 replacement (white accent):

```css
border: 2px solid rgba(255, 255, 255, 0.2);
border-top-color: var(--color-accent);
```

### pulse-border Keyframe Update

```css
/* Phase 3 */
@keyframes pulse-border {
  0%, 100% { border-color: rgba(245, 158, 11, 0.3); }
  50%       { border-color: rgba(245, 158, 11, 0.7); }
}

/* Phase 4 */
@keyframes pulse-border {
  0%, 100% { border-color: rgba(255, 255, 255, 0.2); }
  50%       { border-color: rgba(255, 255, 255, 0.6); }
}
```

### nav-brand CSS Rule Update

The existing `.nav-brand` rule uses `font-size: var(--text-heading)` (24px). The UI-SPEC revises this to `16px` with `letter-spacing: 0.25em` and `text-transform: uppercase` to achieve the wordmark effect.

```css
/* Phase 4 .nav-brand */
.nav-brand {
  font-size: var(--text-body);      /* 16px */
  font-weight: 600;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  line-height: 1;
  color: var(--color-accent);       /* white */
}
```

Template text remains `CRATE` (single word) — `text-transform: uppercase` and `letter-spacing` do the visual work.

### Discogs Artwork Upgrade Pattern

The current flow in `scanner.py`:
1. Search returns `results[0].get("thumb")` — low-res thumbnail
2. This is attached as `_cover_image` on the first listing dict
3. `scanner.py` pops `_cover_image` and sets `item.artwork_url`

The Phase 4 upgrade path: when the album scan already calls `/releases/{release_id}` for price data, extract `images[0].uri` from that same response and use it instead of the search `thumb`.

**Key implementation detail:** The release endpoint is already called inside `_get_album_listings()`, `_get_artist_listings()`, and `_get_label_listings()`. The `detail` dict from each release call already contains the `images` array when the request is authenticated. The change is to extract `images[0].uri` from the first result's detail response and return it as `_cover_image`.

Confirmed: `images[0].uri` requires a valid Discogs auth token (already present via `_get_headers()`). Without auth, the field is empty. Since the project already authenticates all Discogs calls, this is not a risk.

**Fallback:** If `images` is empty or missing, fall back to the search `thumb` (current behaviour). If `thumb` is also absent, `_cover_image` is not set and artwork remains `None` (existing graceful degradation preserved).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSS design tokens | New token system | Existing `:root` custom properties | Already tokenised — just update values |
| Letter-spaced wordmark | SVG logo, icon font | CSS `letter-spacing` + `text-transform` | Pure CSS, no asset dependency, matches UI-SPEC |
| High-res artwork | New proxy endpoint, new model column | Existing `artwork_url` column + proxy endpoint | Already in place from Phase 3 — only the source URL changes |
| Radius system | Per-component utility classes | CSS custom property `--radius-*` tokens on `:root` | Consistent with existing token architecture |

---

## Common Pitfalls

### Pitfall 1: Changing Global Spacing Tokens Instead of Component Classes

**What goes wrong:** Editor changes `--space-md` from 16px to 12px in `:root`, breaking all padding/gap that should remain at 16px (nav, modal, forms, stats bar).
**Why it happens:** D-07 says "card padding 12px" — easy to interpret as a token change.
**How to avoid:** The UI-SPEC is explicit: global `--space-*` tokens are unchanged. Only three component rules get the compressed value: `.card-body { padding: 12px; }`, `.card-grid { gap: 12px; }`, and any `.section-gap` rule. Apply literal pixel values, not token references.

### Pitfall 2: Removing border-radius: 50% from .spinner

**What goes wrong:** Sweeping "set all border-radius to 0" approach removes the circular spinner shape.
**Why it happens:** Radius removal is a blanket decision across the design.
**How to avoid:** `.spinner` uses 50% for geometry, not aesthetics. It is explicitly excluded from the radius change. Verify `.spinner` still has `border-radius: 50%` after edits.

### Pitfall 3: Missing Inline border-radius Values in Templates

**What goes wrong:** CSS is updated but `item_detail.html` still has `border-radius: 8px` inline on the artwork `<img>` elements (lines 22 and 28).
**Why it happens:** Inline styles are invisible to a CSS-only search.
**How to avoid:** Search templates for `border-radius` after updating CSS. Two instances in `item_detail.html` must be set to `0`.

### Pitfall 4: artwork_url Not Backfilled for Existing Items

**What goes wrong:** After deploying the Discogs release endpoint upgrade, existing items in the database still have the old thumbnail URLs. New scans get the high-res URL; existing items do not.
**Why it happens:** `scanner.py` only sets `artwork_url` when it is currently `None` — it does not overwrite existing URLs.
**How to avoid:** This is acceptable behaviour. The artwork upgrade is opportunistic — on next scan of an item with an existing `artwork_url`, it will not be updated (by design, to avoid unnecessary Discogs API calls). Document this limitation in the plan. If Jacob wants to force-refresh all artwork, that would be a separate one-off migration task outside this phase.

### Pitfall 5: White Accent on White Backgrounds

**What goes wrong:** After changing `--color-accent` to `#ffffff`, any element that uses `color: var(--color-accent)` on a light surface becomes invisible.
**Why it happens:** The entire palette is dark, so white text reads fine — but the CTA button uses white as its `background`, with `--color-cta-text` (`#0a0a0a`) for the label. If a developer accidentally sets both background and text to white, the button becomes unreadable.
**How to avoid:** The UI-SPEC is precise about where white is used (see "Accent reserved for" list). The CTA button uses `--color-accent-cta` as background and `--color-cta-text` (#0a0a0a) as the label. Verify CTA buttons remain readable after token update.

### Pitfall 6: Empty state copy not updated in index.html

**What goes wrong:** `templates/index.html` line 171 still says "Your wishlist is empty" after the rename.
**Why it happens:** Template text edits are easy to miss when focusing on CSS.
**How to avoid:** The copywriting contract in UI-SPEC specifies: empty state heading → "Your crate is empty". Treat template text changes as a checklist alongside CSS changes.

---

## Code Examples

### CSS Token Replacement Pattern (style.css)

The `:root` block is lines 10–75 of `static/style.css`. All token updates happen in that block.

```css
/* Source: 04-UI-SPEC.md — Colour tokens */
:root {
  --color-bg:           #0a0a0a;
  --color-surface:      #111111;
  --color-surface-alt:  #0a0a0a;
  --color-border:       #222222;
  --color-border-muted: #111111;
  --color-text:         #f5f5f5;
  --color-text-muted:   #777777;
  --color-text-faint:   #555555;
  --color-accent:       #ffffff;
  --color-accent-hover: #e0e0e0;
  --color-accent-bg:    rgba(255,255,255,0.08);
  --color-accent-cta:   #ffffff;
  --color-cta-text:     #0a0a0a;
  /* ... radius tokens, badge tokens appended here */
  --radius-card:    0px;
  --radius-modal:   0px;
  --radius-btn:     2px;
  --radius-badge:   2px;
  --radius-input:   2px;
}
```

### Discogs Artwork Upgrade Pattern (discogs.py)

The change is inside `_get_album_listings()` where `detail_resp` is already fetched. Currently:

```python
# Phase 3 — thumb from search result
first_thumb = results[0].get("thumb") if results else None
# ... later ...
if listings and first_thumb:
    listings[0]["_cover_image"] = first_thumb
```

Phase 4 upgrade: extract `images[0].uri` from the first detail response instead.

```python
# Phase 4 — full-res from release endpoint
cover_uri = None
# Inside the loop, after detail_resp is fetched:
if cover_uri is None:
    images = detail.get("images", [])
    if images:
        cover_uri = images[0].get("uri") or images[0].get("uri150")

# After loop:
if listings and cover_uri:
    listings[0]["_cover_image"] = cover_uri
elif listings and first_thumb:
    listings[0]["_cover_image"] = first_thumb  # fallback
```

This same pattern applies to `_get_artist_listings()` and `_get_label_listings()` (both also call the release endpoint).

### Nav Brand HTML (base.html)

```html
<!-- Phase 3 -->
<a href="/" class="nav-brand">Vinyl Wishlist</a>

<!-- Phase 4 -->
<a href="/" class="nav-brand">CRATE</a>
```

The `text-transform: uppercase` in CSS handles display; HTML text is the single word `CRATE`.

### Delete Button Copy (item_detail.html)

```html
<!-- Phase 3 -->
<form action="/wishlist/{{ item.id }}/delete" method="post"
      onsubmit="return confirm('Remove this item from your wishlist?')">
  <button type="submit" class="btn-destructive">Delete</button>
</form>

<!-- Phase 4 -->
<form action="/wishlist/{{ item.id }}/delete" method="post"
      onsubmit="return confirm('Remove this item from your crate?')">
  <button type="submit" class="btn-destructive">Remove from Crate</button>
</form>
```

---

## Implementation Change Summary

This is the exact scope the planner should decompose into tasks.

| File | Change Type | What Changes |
|---|---|---|
| `static/style.css` | Token update + radius + keyframes + nav-brand rule | `:root` colour tokens; `--radius-*` tokens added; all `border-radius` component rules; `.spinner` border colours; `pulse-border` keyframe; `.nav-brand` typography |
| `templates/base.html` | Text | Nav brand text → `CRATE`; `<title>` → `CRATE` |
| `templates/index.html` | Text | `<title>` block → `Dashboard · CRATE`; empty state heading → `Your crate is empty` |
| `templates/item_detail.html` | Text + inline style | `<title>` block → `CRATE — {item.query}`; delete button label → `Remove from Crate`; confirm copy → `Remove this item from your crate?`; inline `border-radius: 8px` → `0` on both artwork `<img>` elements |
| `app/services/discogs.py` | Backend | Extract `images[0].uri` from release detail response for artwork; applies to all three search functions (`_get_album_listings`, `_get_artist_listings`, `_get_label_listings`) |

---

## Environment Availability

Step 2.6: SKIPPED — Phase 4 is purely CSS/template/Python edits with no external tools, new services, or CLI utilities beyond what Phase 3 already used.

---

## Open Questions

1. **Existing items with Phase 3 artwork URLs**
   - What we know: `scanner.py` only writes `artwork_url` when it is currently `None`. Existing items keep their thumbnail URLs after the upgrade.
   - What's unclear: Whether Jacob wants a one-time backfill to replace thumbnails with high-res on existing items.
   - Recommendation: Do not add a migration to this phase. Note the limitation in the plan. If Jacob wants a force-refresh, that is a separate task (e.g., `UPDATE wishlist_items SET artwork_url = NULL WHERE artwork_url IS NOT NULL` then trigger a scan — or a dedicated migration script).

2. **`images[0].uri` availability for artist/label searches**
   - What we know: Artist and label search flows call the release endpoint for each release. The `images` array is present in authenticated release responses.
   - What's unclear: Whether some releases have `images: []` (no cover art uploaded to Discogs). The fallback to `first_thumb` handles this.
   - Recommendation: Implement with fallback to `cover_image` thumbnail as noted in the code example above.

---

## Sources

### Primary (HIGH confidence)
- `static/style.css` (read directly) — Phase 3 token values, component rules, existing radius values, spinner colours
- `templates/base.html`, `templates/index.html`, `templates/item_detail.html` (read directly) — current text, inline styles, class usage
- `app/services/discogs.py` (read directly) — current artwork capture logic, release endpoint call structure
- `app/services/scanner.py` (read directly) — `_cover_image` extraction and `artwork_url` assignment flow
- `.planning/phases/04-ui-polish/04-CONTEXT.md` (read directly) — locked decisions
- `.planning/phases/04-ui-polish/04-UI-SPEC.md` (read directly) — resolved token values, radius contract, copywriting contract

### Secondary (MEDIUM confidence)
- Discogs API `images[0].uri` field: verified via WebSearch — requires auth token, returns full-res URL in `images` array on release endpoint responses. Multiple forum sources confirm auth is required; the project already authenticates all Discogs calls.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing tools confirmed in place
- Architecture: HIGH — existing CSS token pattern verified by reading actual source files; change surface is fully enumerated
- Pitfalls: HIGH — derived from actual source code inspection, not assumptions
- Discogs `images[0].uri`: MEDIUM — confirmed via community sources; field structure well-documented in Discogs developer community though official API docs returned 403

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain — CSS and Jinja2 don't change; Discogs API v2 is stable)
