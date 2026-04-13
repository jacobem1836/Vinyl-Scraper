# Feature Research

**Domain:** Vinyl wishlist price tracker — v1.1 UX Polish & Album Selection
**Researched:** 2026-04-05
**Confidence:** HIGH (Discogs API fields confirmed from codebase + WebSearch; email patterns from official sources; font guidance from current typography sources; UI analysis from ui-to-improve.txt)

> **Scope note:** This document covers only the v1.1 feature areas: Discogs typeahead, image source prioritisation, HTML email redesign, and brand font upgrade. The v1.0 baseline features (scraping, scoring, AU landing costs) are documented in the original FEATURES.md and remain unchanged.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that must exist for the v1.1 experience to feel correct. Missing any of these = the feature area feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Typeahead fires within 300ms of typing pause | Users treat autocomplete as instant; lag makes it feel broken | LOW | 300ms debounce is industry standard (Algolia, most production implementations) |
| Dropdown shows: cover thumb + "Artist — Title" + year + label | Vinyl has hundreds of pressings; users need enough data to pick the right one | LOW | All fields returned by Discogs `/database/search`: `thumb`, `title`, `year`, `label[0]`, `id` |
| Keyboard navigation in typeahead dropdown | Arrow keys + Enter + Escape is the universal autocomplete contract | LOW | Up/Down to navigate, Enter to select, Escape to dismiss; selected item highlighted |
| Typeahead only active for "Album" type | Artist/label queries are fuzzy by nature; only album selection benefits from release pinning | LOW | Conditional: show autocomplete when `type === "album"` is selected; disable otherwise |
| Store-sourced images shown when available | Store images (Shopify, eBay product pages) are higher resolution and more specific than Discogs thumbs | MEDIUM | Requires `image_url` column on `Listing` + adapter updates; scanner sets `artwork_url` from best source |
| Fallback to Discogs `artwork_url` when no store image | Already stored; graceful degradation | LOW | Existing `artwork_url` on `WishlistItem` is the correct fallback anchor; no template change needed |
| Fallback to SVG placeholder when both sources fail | User sees something rather than a broken img tag | LOW | Already implemented via `onerror` in templates; keep as-is |
| Email body max-width 600px | Standard container width; wider breaks on most email clients and mobile | LOW | Pure CSS/attribute change to `<table>` wrapper |
| All email body styles inline | Email clients (Gmail, Outlook) strip `<style>` blocks in the body | LOW | Inline every `style=""` attribute; one `<style>` in `<head>` for media queries only |
| CTA "View listing" as a styled button-link | Plain `<a>` link is undersized and hard to tap on mobile | LOW | Table-based button: `<td style="background:#fff; padding:10px 20px"><a href="...">View listing</a></td>` |
| Email scannable in under 3 seconds | Deal alert must communicate: what album, what price, where to buy — before the user decides to delete | LOW | Hierarchy: item name (large) → best price (very large) → source table |
| Dark mode `@media (prefers-color-scheme: dark)` in email | Most iOS/macOS users have dark mode; broken dark mode email looks unprofessional | MEDIUM | Requires `<meta name="color-scheme">` + `@media` block in `<style>` in `<head>` |
| Focus-visible on all buttons | Keyboard users get no visual feedback currently; WCAG A failure | LOW | `box-shadow: 0 0 0 2px var(--color-accent)` on `:focus-visible` for all `.btn-*` classes |
| Active + disabled button states | Press confirmation (`:active`) and scan-in-progress feedback (`:disabled`) | LOW | `transform: scale(0.98)` on `:active`; `opacity: 0.5; cursor: not-allowed` on `:disabled` |
| text-faint contrast fix | #555555 on #0a0a0a is ~3.6:1 — fails WCAG AA for 14px text | LOW | Bump to #686868 (~4.5:1); secondary info (price sub-labels, timestamps) becomes readable |
| 3-column grid breakpoint at 1024px | 2 columns from 768–1279px is a large dead zone; most laptops sit in this range | LOW | `@media (min-width: 1024px) { .card-grid { grid-template-columns: repeat(3, 1fr); } }` |
| Card title hierarchy fix | Album title is 14px (smaller than body text); price should visually dominate the card | LOW | `text-sm` → 16px normal weight for title; price stays 14px/600 or bumps to 18px |
| Bug: overlapping buttons bottom-right | Reported positional bug; must fix before shipping | LOW | CSS positioning fix; no logic change |
| Bug: scan log "no artist results" shown for album type | Wrong type label in log message | LOW | One-line fix in scanner.py |

### Differentiators (Valued but Not Expected)

Features that enhance the experience beyond baseline expectations.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Typeahead shows 8 results, not just top 1 | Vinyl has original pressings, reissues, remasters — user needs to distinguish | LOW | `per_page=8` in the search call; show all 8 in dropdown |
| Supplementary `discogs_release_id` stored on WishlistItem | Enables future precise-by-ID scanning rather than text query | LOW | Optional new column; doesn't affect existing scan logic |
| Email subject line includes best price | `[CRATE] Dark Side of the Moon — $28.50 AU` vs `[Vinyl Wishlist] New deal` — price in subject = immediate triage | LOW | Compute `_landed(notify_listings[0])` and inject into subject |
| Email shows landed cost breakdown (not just total) | Core value prop of the app — "$22 + $8 shipping = $30 AU" — should appear in email too | LOW | Already computed in `_landed()`; format clearly in the table row |
| Reduce email columns from 8 → 5 | 8 columns in a 600px table is unreadable on mobile; drop Condition and Seller columns | LOW | Keep: Title, Landed AU, Ships From, Source, View button |
| Brand mark font upgrade (CRATE wordmark) | System font wordmark reads as generic; one loaded display font creates visual identity at zero cost to the user | LOW | One `<link>` in `<head>`, one CSS rule on `.brand`; no other element affected |
| Deal badge on dashboard cards | Visual hierarchy signal: which card has the best deal right now? Currently all cards look identical regardless of deal status | MEDIUM | Requires `typical_price` per item in dashboard route query; CSS modifier `--deal` on card |
| Inline delete confirmation | Replace native `confirm()` with in-place "Are you sure? / Cancel" — consistent with CRATE aesthetic | LOW | JavaScript state toggle on the button; no new modal |

### Anti-Features (Do Not Build)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-select the first Discogs result on type | Feels like a time-saver | Vinyl has hundreds of pressings; silent wrong selection is worse than no selection | Require explicit user action to confirm a result |
| 0ms debounce / per-keystroke API calls | Maximally responsive | Discogs rate limit is 60 req/min for authenticated users; fast typing will hit 429 errors immediately | 300ms debounce + AbortController to cancel in-flight requests |
| Discogs cover art embedded in email | Looks premium | Discogs image URLs require an `Authorization` header; embedded auth tokens in email are a security risk and most clients will block external images anyway | Text-focused email with a styled dark header bar; no external image dependencies |
| Full HTML email framework (MJML, Foundation for Emails) | Faster template development | Adds a Node.js build step to a pure-Python project; over-engineered for a single transactional template | Hand-crafted ~100-line table email with inline CSS; entirely maintainable |
| Storing `discogs_release_id` as the primary scan identifier | More precise than text query | The 5 non-Discogs adapters (eBay, Shopify, Bandcamp, Juno, Discrepancy) cannot search by Discogs ID — the text query must remain the primary scan anchor | Store `discogs_release_id` as optional supplementary field; `query` remains the scan parameter |
| Animated email content | Modern CSS animation feels engaging | CSS animation support in email is <50% across major clients; fallback is visually broken | Static design that renders correctly in all clients |
| Applying the brand font to more than `.brand` | Typographic consistency | Loading a display font for body text degrades legibility and page performance; system font stack is correct for UI text | One font, one selector, maximum impact |

---

## Feature Dependencies

```
[Discogs typeahead]
    └──requires──> [New API route: GET /api/discogs/search?q=&type=release]
                       └──requires──> [Existing discogs_token in settings — already present]
    └──requires──> [Frontend: debounced fetch + dropdown render in index.html JS]
    └──optionally stores──> [discogs_release_id on WishlistItem — new optional column]

[Store image priority]
    └──requires──> [image_url = Column(String, nullable=True) on Listing model]
    └──requires──> [adapter updates: shopify.py, ebay.py return image_url in listing dict]
    └──requires──> [scanner.py: after scan, compute best image → update item.artwork_url]
    └──fallback chain──> [item.artwork_url → listing.image_url → Discogs cover → placeholder SVG]

[Email UI redesign]
    └──requires──> [Existing notifier.py send_deal_email() — no structural change needed]
    └──enhances──> [Existing _landed() and compute_typical_price() — no changes]

[Brand font upgrade]
    └──requires──> [Google Fonts link in base.html <head>]
    └──affects──> [.brand CSS selector only — one rule]

[UI polish pack]
    └──requires──> [Existing CRATE CSS custom properties — no new variables needed for most fixes]
    └──affects──> [crate.css button states, text-faint token, card-grid media query, card-body typography]

[Bug fixes]
    └──independent of all other features — fix in isolation]
```

### Dependency Notes

- **Typeahead requires a new thin backend route.** The existing `discogs.py` search functions are designed for full scan results (multiple API calls, 0.5s sleeps between requests). A typeahead endpoint must be a lightweight single-call: one GET to `/database/search`, return `[{id, title, year, label, thumb}]` immediately. Do not reuse the scan-path functions for this.
- **Store image priority requires a migration.** `image_url` is a new nullable column on the `Listing` model. The migration pattern in this codebase is handled in `main.py` startup hooks. No existing data breaks — all rows default to `NULL`, and the artwork fallback chain handles the null case correctly.
- **Scanner.py must update `item.artwork_url` logic.** Currently `artwork_url` is populated from the Discogs `_cover_image` returned in scan results. After this change, scanner.py should prefer the best `image_url` from a newly found listing if it exists, and only fall back to the Discogs cover image if no store image was found.
- **Email redesign is self-contained.** Only modifies `html_body` construction in `send_deal_email()`. No schema changes, no new routes, no test dependencies.
- **Font upgrade is fully isolated.** One `<link>` tag in `base.html`, one CSS rule. Cannot regress anything else.

---

## MVP Definition (v1.1 Ship List)

### Ship in v1.1

- [ ] Discogs typeahead for album type — highest-value new capability; enables precise release identification
- [ ] Store image priority (`image_url` column + fallback chain) — fixes the case where a better image is available but Discogs thumb is shown
- [ ] Email UI redesign — current email is an unstyled HTML table; functional improvement with no risk
- [ ] Brand font upgrade (CRATE wordmark only) — isolated, highest aesthetic ROI per line of code
- [ ] UI polish pack: button focus/active/disabled states, text-faint contrast, 3-col grid breakpoint, card title hierarchy — all CSS changes, bundle together
- [ ] Bug: overlapping buttons — must fix
- [ ] Bug: scan log type label — must fix

### Add After v1.1 (v1.2)

- [ ] Deal badge on dashboard cards — requires typical_price per item passed from route; worth doing but adds query complexity
- [ ] Discogs typeahead for artist and label types — extends proven pattern after album is stable
- [ ] Pinned release badge on card — depends on typeahead being used in practice first

### Future Consideration (v2+)

- [ ] Price history per item — significant data model and charting work; not core value for v1.x
- [ ] Email open tracking — overkill for personal tool

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Discogs typeahead (album) | HIGH | MEDIUM | P1 |
| Bug fixes (buttons, scan log) | HIGH | LOW | P1 |
| UI polish pack (CSS) | MEDIUM | LOW | P1 |
| text-faint contrast fix | MEDIUM | LOW | P1 |
| Email UI redesign | MEDIUM | LOW | P1 |
| Store image priority | MEDIUM | MEDIUM | P1 |
| Brand font upgrade | LOW | LOW | P1 |
| Deal badge on cards | MEDIUM | MEDIUM | P2 |
| Typeahead for artist/label | LOW | LOW | P2 |
| Pinned release badge | LOW | LOW | P3 |

---

## Implementation Notes by Feature Area

### 1. Discogs Typeahead

**Expected UX:**
- Input focused, type = album selected → user begins typing album name
- After 300ms pause: fire `GET /api/discogs/search?q={input}&type=release` (debounced, abort previous with AbortController)
- Dropdown renders below the input field with up to 8 results
- Each row: 32×32px thumbnail | "Artist — Title" | year | label (first value)
- Keyboard: Up/Down navigate, Enter selects highlighted result, Escape closes
- On select: input field value sets to the canonical `title` from Discogs; dropdown closes; optional hidden field stores `discogs_release_id`
- Typeahead is hidden/disabled when type is artist, label, or subject
- Min chars to trigger: 2 (avoid noise on single-char inputs)
- Dropdown disappears on outside click

**Backend route (`GET /api/discogs/search`):**
- Single call to `GET https://api.discogs.com/database/search?q={q}&type=release&format=Vinyl&per_page=8`
- Returns `[{id, title, year, label, thumb}]` — thin, no follow-up release detail calls
- Auth: existing `discogs_token` in settings
- Rate limit: 300ms debounce + 1 call per request = safe within 60 req/min limit
- No server-side cache needed for v1.1 (queries are per-keystroke and highly variable)

**Data available from Discogs `/database/search` response (confirmed):**
- `title` — format: "Artist - Album Title"
- `year` — release year string
- `label` — array; take `label[0]`
- `thumb` — small image URL (~150px square)
- `cover_image` — larger image (use as fallback if `thumb` is empty string)
- `id` — release ID integer

### 2. Image Source Prioritisation

**Fallback chain (priority order, highest to lowest):**
1. `listing.image_url` from the most recent active listing with a non-null image value — store images (Shopify product images, eBay item photos) are the highest quality and most specific
2. `wishlist_item.artwork_url` — already populated from Discogs `_cover_image` during scan; this is the existing behaviour
3. `/static/vinyl-placeholder.svg` — existing `onerror` handler in templates; keep as-is

**What changes:**
- `Listing` model: add `image_url = Column(String, nullable=True)`
- `shopify.py` and `ebay.py`: include `image_url` in the returned listing dict where the adapter already has access to a product image
- `scanner.py`: after persisting listings, iterate the new listings and update `item.artwork_url` if any has a non-null `image_url` (prefer the first one found, as listings are already sorted by price)
- Templates: no change — `artwork_url` is the single source of truth that templates consume; the fallback chain changes happen server-side

### 3. HTML Email Design

**Table-stakes structure for a deal alert email:**
```
[Header row: dark background (#1a1a1a), CRATE in white, tracking info]
[Body: white or near-white background]
  H1: Album name — large, bold, dark text
  Deal price: very large, colour-accent (green), the "money shot"
  Table: 5 columns — Title | Landed AU | Ships From | Source | View button
[Footer: "You're watching N items" — light grey, small]
```

**Critical rules (all confirmed from official sources):**
- All styles inline on body content elements — Gmail strips `<head><style>` for body content
- One `<style>` block in `<head>` is acceptable for `@media` queries and dark mode only
- Max-width 600px on outer `<table>` — fits all preview panes
- Web-safe fonts for body: `Arial, Helvetica, sans-serif` — do not use Google Fonts in email
- CTA button = table-based: `<table><tr><td style="..."><a style="...">View listing</a></td></tr></table>`
- Dark mode: `<meta name="color-scheme" content="light dark">` + `@media (prefers-color-scheme: dark)` to prevent default inversion breaking the dark header

**Current email problems (from reading notifier.py):**
- `border="1"` table has no inline styling — renders with default browser table borders
- 8 columns at 600px width — unreadable on mobile (`Title | Landed Price (AU) | Ships From | Condition | Source | Link`)
- No subject line branding or price — `[Vinyl Wishlist] New deal for: {query}` is generic
- `<h2>` and `<p>` tags with no inline styles — Gmail renders these with browser defaults

**Reduce to 5 columns:** Title | Landed AU | Ships From | Source | View — drop Condition and Seller (Condition is often null; Seller is not useful without a link)

### 4. Brand Font Upgrade (CRATE wordmark)

**Requirements:**
- Geometric or grotesque sans-serif — matches the brutalist/utilitarian aesthetic
- Works at ~18–22px rendered (nav height)
- All-caps rendering via CSS (`text-transform: uppercase` already applied via `letter-spacing: 0.25em`)
- Available free on Google Fonts — zero build step, zero licensing complexity
- Apply to `.brand` selector only — no other element touched

**Recommendation: Space Grotesk, weight 600**
- Geometric grotesque with a technical, screen-native character
- Designed specifically for digital use; performs at small sizes
- Free on Google Fonts; variable font available (one HTTP request)
- Used in tech tools and dark UIs without being overused
- Distinctive from Inter/system font stack — the wordmark reads as intentional

**Alternative: Bebas Neue**
- All-caps condensed display font; extremely strong and raw
- Works only for all-caps (no lowercase, so zero risk of misuse outside `.brand`)
- Free on Google Fonts
- Risk: widely used in brutalist-adjacent design; less distinctive in 2026

**Decision guidance:** Space Grotesk for restraint and legibility; Bebas Neue for maximum typographic identity. Both are valid. Execute-phase decision after visual comparison.

---

## Sources

- Discogs API response fields: confirmed from codebase (`discogs.py` `/database/search` usage) + WebSearch result listing `thumb`, `title`, `year`, `label`, `cover_image`, `id`
- Typeahead debounce timing: [Algolia debouncing guide](https://www.algolia.com/doc/ui-libraries/autocomplete/guides/debouncing-sources) — 300ms is standard
- Typeahead UX patterns: [Smart Interface Design Patterns — Autocomplete UX](https://smart-interface-design-patterns.com/articles/autocomplete-ux/)
- HTML email best practices: [Mailtrap HTML Email Guide](https://mailtrap.io/blog/html-email/) — inline CSS, 600px width, table layout, web-safe fonts
- HTML email trends 2025: [TextMagic HTML Email Best Practices](https://www.textmagic.com/blog/html-email-best-practices/)
- Brutalist font characteristics: [Typewolf Top 10 Brutalist Fonts](https://www.typewolf.com/top-10-brutalist-fonts)
- Space Grotesk: [Google Fonts — Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk)
- UI audit findings: `ui-to-improve.txt` in project root — detailed per-element analysis of both templates
- Existing codebase: `app/services/notifier.py`, `app/services/discogs.py`, `app/models.py`, `templates/index.html`

---

*Feature research for: Vinyl Wishlist Manager v1.1 — UX Polish & Album Selection*
*Researched: 2026-04-05*
