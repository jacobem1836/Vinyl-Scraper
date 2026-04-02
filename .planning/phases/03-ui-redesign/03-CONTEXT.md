# Phase 3: UI Redesign - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the current Tailwind CDN-based UI with a hand-rolled custom CSS design system, a Spotify-style album-grid dashboard where record artwork is the visual hero, and proper AUD cost breakdown across all listing currencies. The iOS Shortcut API contract is untouched.

</domain>

<decisions>
## Implementation Decisions

### CSS Approach (UI-01)
- **D-01:** Remove Tailwind CDN entirely. Write hand-rolled CSS using CSS custom properties (design tokens) for colours, spacing, and typography. Ship as a single static CSS file served by FastAPI/Railway. No CDN dependency at runtime.
- **D-02:** Use CSS custom properties (`--color-bg`, `--color-surface`, `--color-accent`, `--color-text`, etc.) as the design token layer. Existing amber-400/slate-900 palette continues — just formalised into variables.

### Dashboard Card Layout (UI-02)
- **D-03:** Dashboard is an album grid — each wishlist item is a card where the record artwork fills the card face (like a Spotify album tile).
- **D-04:** Below the artwork: item title and best AUD price only. Minimal. No listing count, no last-scanned timestamp on the card itself.
- **D-05:** Clicking a card navigates to `item_detail.html` (the existing detail page, also redesigned). No inline expansion.
- **D-06:** The scan polling UX (floating pill, progress panel) built in Phase 1 is preserved and restyled to match the new design system.

### Record Artwork (UI-03)
- **D-07:** Artwork is fetched during the existing background scan, in the same background task — no separate enrichment pass. The Discogs adapter captures the first release image URL as part of its normal scan call.
- **D-08:** `artwork_url` is stored as a new nullable `String` column on `WishlistItem`. Populated on first successful Discogs scan; `NULL` for items only found on non-Discogs sources.
- **D-09:** Artwork is served via a local proxy endpoint (e.g. `GET /api/artwork?url=...`) — browser never hotlinks Discogs CDN directly.
- **D-10:** Placeholder for items without artwork: a vinyl record SVG (dark, tasteful). Embedded as inline SVG or served as a static file — Claude's discretion on delivery method.

### Landed Cost Breakdown (UI-04)
- **D-11:** Each listing row in the detail view shows: AUD total (prominent), then original currency price below it in smaller text (e.g. "£22 + £8 shipping"). Exchange rate is NOT shown in the UI.
- **D-12:** FX conversion is applied to GBP and USD listings. AUD listings pass through unchanged.

### FX Rate (Phase 2 deferred)
- **D-13:** Use `exchangerate-api.com` free tier (no auth required for base rates). Fetch via `httpx` async call.
- **D-14:** Cache the rate dict in memory with a ~1 hour TTL (same `cachetools.TTLCache` pattern used elsewhere). One cache entry per currency pair needed (GBP→AUD, USD→AUD).
- **D-15:** FX conversion logic lives in the service layer (not the template). The route handler passes AUD-converted values to the template.

### Dark Colour Palette (UI-05)
- **D-16:** No white backgrounds, no light-mode bleed. Dark palette carries over from existing slate-900/amber-400 scheme — formalised via CSS custom properties.

### Claude's Discretion
- SVG placeholder delivery method (inline vs static file)
- Grid column count and card sizing (responsive breakpoints)
- Hover/focus states on cards
- Typography scale (font sizes and weights via design tokens)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §UI-01 through UI-06 — full acceptance criteria for this phase

### Existing Code
- `templates/base.html` — current Tailwind CDN base; this file is being replaced
- `templates/index.html` — dashboard template; card grid goes here
- `templates/item_detail.html` — detail page template; also being redesigned
- `static/style.css` — current micro-overrides; becomes the full design system file
- `app/models.py` — `WishlistItem` model; needs `artwork_url` column added
- `app/services/discogs.py` — Discogs adapter; needs to capture `image_url` from search results
- `app/routers/wishlist.py` — route handlers; FX conversion and AUD values passed to templates here

### No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Scan polling JS (base.html) — floating pill + progress panel; keep, restyle
- Toast notification (base.html) — keep, restyle to match new design tokens
- Modal (index.html) — add-item modal; keep, restyle
- `cachetools.TTLCache` pattern (scanner.py) — reuse for FX rate cache

### Established Patterns
- `cachetools.TTLCache(maxsize=1, ttl=300)` for in-memory caching — extend for FX rates with TTL=3600
- `asyncio.to_thread()` for blocking I/O (notifier.py) — usable if FX fetch needs it
- Listing dict schema already has `currency`, `price`, `shipping_cost`, `ships_from` fields — FX conversion reads these

### Integration Points
- `WishlistItem` model → add `artwork_url: Column(String, nullable=True)`
- Discogs adapter `_build_listing()` / search response → extract `cover_image` field from Discogs release
- `_enrich_item()` in wishlist router → pass `artwork_url` through to template context
- New `/api/artwork` proxy endpoint → thin httpx passthrough, no auth needed for Discogs image CDN

</code_context>

<specifics>
## Specific Ideas

- Spotify album-grid as the visual reference — artwork fills the card, minimal text below
- AUD total is the headline number; original currency shown smaller below (no FX rate label)
- Dark vinyl SVG for the placeholder — fits the aesthetic without resorting to text tiles

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-ui-redesign*
*Context gathered: 2026-04-03*
