# Phase 3: UI Redesign — Research

**Researched:** 2026-04-03
**Domain:** Custom CSS design system, Jinja2 templates, FX conversion, artwork proxy, SQLAlchemy migration
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Remove Tailwind CDN entirely. Write hand-rolled CSS using CSS custom properties (design tokens). Ship as a single static CSS file. No CDN dependency at runtime.
- **D-02:** Use CSS custom properties (`--color-bg`, `--color-surface`, `--color-accent`, `--color-text`, etc.) as the design token layer. Existing amber-400/slate-900 palette continues — formalised into variables.
- **D-03:** Dashboard is an album grid — each wishlist item is a card where the record artwork fills the card face (Spotify-style).
- **D-04:** Below the artwork: item title and best AUD price only. No listing count, no last-scanned timestamp on the card.
- **D-05:** Clicking a card navigates to `item_detail.html`. No inline expansion.
- **D-06:** Scan polling UX (floating pill, progress panel) from Phase 1 is preserved and restyled to match the new design system.
- **D-07:** Artwork fetched during the existing background scan in the same background task — no separate enrichment pass.
- **D-08:** `artwork_url` stored as a new nullable `String` column on `WishlistItem`. Populated on first successful Discogs scan; NULL for items only found on non-Discogs sources.
- **D-09:** Artwork served via a local proxy endpoint (`GET /api/artwork?url=...`) — browser never hotlinks Discogs CDN directly.
- **D-10:** Placeholder for items without artwork: a vinyl record SVG. Delivery method is Claude's discretion.
- **D-11:** Each listing row shows: AUD total (prominent), then original currency price below it in smaller text (e.g. "£22 + £8 shipping"). Exchange rate is NOT shown in the UI.
- **D-12:** FX conversion applied to GBP and USD listings. AUD listings pass through unchanged.
- **D-13:** Use `exchangerate-api.com` free tier (no auth required). Fetch via `httpx` async call.
- **D-14:** Cache the rate dict in memory with a ~1 hour TTL using `cachetools.TTLCache`. One cache entry per currency pair (GBP→AUD, USD→AUD).
- **D-15:** FX conversion logic lives in the service layer (not the template). Route handler passes AUD-converted values to the template.
- **D-16:** No white backgrounds, no light-mode bleed. Dark palette via CSS custom properties.

### Claude's Discretion
- SVG placeholder delivery method (inline vs static file)
- Grid column count and card sizing (responsive breakpoints)
- Hover/focus states on cards
- Typography scale (font sizes and weights via design tokens)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UI-01 | Bootstrap removed; replaced with custom CSS using design tokens (CSS custom properties) for colours, spacing, typography | CSS token architecture in UI-SPEC.md; `static/style.css` becomes the full design system; `base.html` drops `<script src="https://cdn.tailwindcss.com">` |
| UI-02 | Dashboard displays wishlist items as a card grid where record cover artwork is the visual hero | Grid layout contract in UI-SPEC.md; `index.html` card section rewritten; `artwork_url` field on `WishlistItem` drives `<img>` src |
| UI-03 | Album art fetched from Discogs at scan time, stored as URL in DB, served via local proxy — Discogs CDN never hotlinked | `cover_image` field confirmed present in Discogs search response; `WishlistItem.artwork_url` column added; `/api/artwork` proxy route added |
| UI-04 | Each listing shows landed cost breakdown: base price + shipping + AUD equivalent | FX service layer with TTLCache; `_enrich_item` / `item_detail` route updated to pass AUD-converted values; template renders per UI-SPEC D-11 |
| UI-05 | Dark colour palette consistently applied across all pages | All Tailwind utility classes replaced with CSS custom property equivalents defined in UI-SPEC token table |
| UI-06 | iOS Shortcut API contract (`POST /api/wishlist` with `X-API-Key`) preserved unchanged | `api_router` and `require_api_key` logic in `wishlist.py` untouched; `WishlistItemResponse` schema unchanged; new `artwork_url` field is nullable so old callers are unaffected |
</phase_requirements>

---

## Summary

Phase 3 replaces the Tailwind CDN dependency with a hand-rolled CSS design system and evolves the dashboard from a text-heavy list into a Spotify-style album grid. Three backend changes accompany the visual work: (1) a new `artwork_url` column on `WishlistItem` populated during Discogs scans, (2) an artwork proxy endpoint that shields the browser from Discogs CDN hotlinking, and (3) a FX service that converts USD/GBP listing prices to AUD before the template receives them.

All decisions are locked in CONTEXT.md and fully specified in UI-SPEC.md. The UI-SPEC is the authoritative source for every token value, layout dimension, copy string, and animation duration — the planner should reference it directly rather than re-deriving values. The design tokens map directly from the existing Tailwind palette (slate-900, amber-400) so no colour research is needed; the colour hex values are confirmed in UI-SPEC.md.

The iOS Shortcut API contract (`POST /api/wishlist` + `X-API-Key`) is unaffected. The new `artwork_url` column is nullable and the existing `WishlistItemResponse` Pydantic schema does not need a breaking change — only an additive nullable field if desired.

**Primary recommendation:** Execute in four ordered waves: (1) CSS design system + Tailwind removal, (2) model migration + Discogs artwork capture + proxy endpoint, (3) FX service + template landed cost display, (4) dashboard card grid rewrite and detail page polish.

---

## Standard Stack

### Core (already installed — no new packages unless noted)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cachetools | 7.0.5 (installed) | TTLCache for FX rate | Already used for dashboard cache; identical pattern |
| httpx | 0.28.0 (installed) | Async HTTP for FX fetch and artwork proxy | Already used for all external requests |
| SQLAlchemy | 2.0.36 (installed) | `artwork_url` column via `add_column` migration | Existing ORM |
| FastAPI | 0.115.0 (installed) | `/api/artwork` proxy endpoint | Existing framework |
| Jinja2 | 3.1.4 (installed) | Template rewrites | Existing templating |

### New Package (one addition)

No new packages required. All needed libraries are already in `requirements.txt`.

### External API

| Service | Endpoint | Auth | Notes |
|---------|---------|------|-------|
| exchangerate-api.com | `https://open.er-api.com/v6/latest/USD` | None | Confirmed working 2026-04-03; returns `rates.AUD`, `rates.GBP`; `time_eol: None` (not deprecated) |
| Discogs API | existing `/database/search` | Token (already configured) | `cover_image` field confirmed in search response — no extra API call needed |

**Installation:** No new packages. Requirements.txt is unchanged.

---

## Architecture Patterns

### Recommended Work Breakdown

```
Wave 1: CSS Design System (UI-01, UI-05)
  static/style.css          ← full design token system replaces micro-overrides
  templates/base.html       ← drop Tailwind CDN script tag; update class references

Wave 2: Artwork (UI-02, UI-03)
  app/models.py             ← add artwork_url column
  app/database.py           ← add_column migration guard
  app/services/discogs.py   ← capture cover_image in _get_album_listings (and _get_artist_listings / _get_label_listings)
  app/services/scanner.py   ← write artwork_url back to WishlistItem after scan
  app/routers/wishlist.py   ← add GET /api/artwork proxy route
  static/vinyl-placeholder.svg ← new file

Wave 3: FX + Landed Cost (UI-04)
  app/services/fx.py        ← new module; TTLCache(maxsize=1, ttl=3600); async get_rates(); convert_to_aud()
  app/routers/wishlist.py   ← _enrich_item and item_detail pass aud_price, orig_price, orig_currency, shipping_display
  templates/item_detail.html ← render landed cost breakdown per UI-SPEC D-11

Wave 4: Dashboard + Detail Polish (UI-02, UI-05)
  templates/index.html      ← album grid card rewrite
  templates/item_detail.html ← header with artwork thumbnail, listing table polish
```

### Pattern 1: CSS Custom Property Token System

**What:** All visual values expressed as `--token-name` on `:root`. No utility classes from Tailwind.
**When to use:** Every HTML element uses `var(--color-bg)` etc. instead of class-based styling.
**Example:**
```css
/* static/style.css — replaces entire file */
:root {
  --color-bg:          #0f172a;
  --color-surface:     #1e293b;
  --color-accent:      #f59e0b;
  --color-text:        #f8fafc;
  --color-text-muted:  #94a3b8;
  --space-md:          16px;
  --space-lg:          24px;
  --text-sm:           14px;
  --text-body:         16px;
  --text-heading:      24px;
  --text-price:        20px;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--text-body);
  min-height: 100vh;
}
```
Source: UI-SPEC.md — CSS Token Architecture section

### Pattern 2: Album Card Grid

**What:** CSS Grid responsive card layout, artwork as `aspect-ratio: 1/1` img filling card face.
**When to use:** Dashboard `index.html` card section.
**Example:**
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--space-lg);
}
@media (min-width: 768px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1280px) {
  .card-grid { grid-template-columns: repeat(4, 1fr); }
}
.card-artwork {
  aspect-ratio: 1 / 1;
  width: 100%;
  object-fit: cover;
  border-radius: 4px 4px 0 0;
  display: block;
}
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
```
Source: UI-SPEC.md — Dashboard Grid layout contract

### Pattern 3: Artwork Proxy Endpoint

**What:** Thin httpx passthrough — fetches Discogs image URL server-side, streams bytes to browser.
**When to use:** Every `<img src="/api/artwork?url=...">` in templates.
**Example:**
```python
# In api_router (wishlist.py)
from fastapi.responses import StreamingResponse

@api_router.get("/artwork")
async def proxy_artwork(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, headers={"User-Agent": "VinylWishlist/1.0"})
            return StreamingResponse(
                r.aiter_bytes(),
                media_type=r.headers.get("content-type", "image/jpeg"),
            )
    except Exception:
        raise HTTPException(status_code=502, detail="artwork fetch failed")
```
Source: CONTEXT.md D-09; pattern derived from existing httpx usage in adapters

### Pattern 4: FX Rate Service

**What:** Module-level TTLCache; async fetch from `open.er-api.com`; pure conversion function.
**When to use:** Called from `_enrich_item` and `item_detail` route before passing values to template.
**Example:**
```python
# app/services/fx.py
import httpx
from cachetools import TTLCache

_fx_cache: TTLCache = TTLCache(maxsize=2, ttl=3600)

async def get_rate(from_currency: str, to_currency: str = "AUD") -> float | None:
    key = f"{from_currency}-{to_currency}"
    if key in _fx_cache:
        return _fx_cache[key]
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"https://open.er-api.com/v6/latest/{from_currency}")
            data = r.json()
            rate = data.get("rates", {}).get(to_currency)
            if rate:
                _fx_cache[key] = rate
            return rate
    except Exception:
        return None

def convert_to_aud(amount: float, currency: str, rate: float | None) -> float | None:
    if currency == "AUD":
        return amount
    if rate is None:
        return None
    return round(amount * rate, 2)
```
Source: CONTEXT.md D-13, D-14; confirmed API response: `open.er-api.com/v6/latest/USD` returns `{"result":"success","base_code":"USD","rates":{"AUD":1.44,...}}`

### Pattern 5: artwork_url Migration Guard

**What:** Additive column added via SQLAlchemy `add_column` in `run_migrations`, guarded by try/except (existing pattern in codebase).
**When to use:** `app/database.py` migration function, same pattern as any prior column additions.
**Example:**
```python
# In run_migrations() — add_column guard
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN artwork_url VARCHAR"))
        conn.commit()
except Exception:
    pass  # column already exists
```
Source: existing `run_migrations` pattern in `app/database.py`

### Pattern 6: Discogs cover_image Capture

**What:** The `cover_image` field is already returned in the `/database/search` results response (confirmed by live API test). No extra API call needed — extract from the `result` dict already fetched in `_get_album_listings`.
**When to use:** In `_get_album_listings`, `_get_artist_listings`, `_get_label_listings` — extract `result.get("cover_image")` alongside title and id.
**Example:**
```python
# In _get_album_listings, inside the results loop:
cover_image = result.get("cover_image")  # or result.get("thumb") as fallback
listing = _build_listing(title=title, release_id=release_id, lowest_price=lowest_price)
# Return cover_image alongside listings so scanner can write it to WishlistItem
```
The scanner then calls `item.artwork_url = cover_image` (if not already set) after scanning. This is a one-time write: once `artwork_url` is populated it is not overwritten on subsequent scans.

Source: Confirmed by live Discogs API call (2026-04-03): `cover_image` key present in search response with token auth. Field is a full-resolution JPEG URL.

### Anti-Patterns to Avoid
- **Hotlinking Discogs CDN in templates:** `<img src="{{ item.artwork_url }}">` directly is forbidden (D-09). Always go through `/api/artwork?url=...`.
- **FX conversion in Jinja2 template:** arithmetic in templates is fragile and untestable. All conversions happen in Python before the template context is built (D-15).
- **Re-fetching artwork on every scan:** once `artwork_url` is populated, skip the write. Guard with `if not item.artwork_url`.
- **Blocking FX fetch:** `get_rate()` is async; do not use `asyncio.to_thread()` — it is already async via httpx.
- **Replacing JS logic in scan polling:** the floating pill JS is plain DOM manipulation. It has no Tailwind dependency — only the CSS classes on the HTML elements need updating. Do not rewrite the JS.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FX rate caching | Custom TTL dict with `time.time()` checks | `cachetools.TTLCache` | Already in requirements; thread-safe; expiry automatic |
| Artwork streaming proxy | Manual `requests` blocking response | `httpx.AsyncClient` + `StreamingResponse` | Non-blocking; consistent with rest of codebase |
| CSS grid responsive layout | JS-based layout calculation | CSS Grid + `@media` breakpoints | Native, zero JS, defined in UI-SPEC |
| Vinyl placeholder | External icon CDN | Inline or `static/vinyl-placeholder.svg` | No CDN dependencies allowed (D-01) |
| SQLite column migration | Full `create_all` replacement | `ALTER TABLE ... ADD COLUMN` inside try/except | Pattern already established in `run_migrations()` |

**Key insight:** Every "new" need in this phase has a directly applicable existing pattern in the codebase. The work is applying known patterns to new problems, not introducing new approaches.

---

## Common Pitfalls

### Pitfall 1: Tailwind Class Bleed After CDN Removal
**What goes wrong:** After removing `<script src="https://cdn.tailwindcss.com">`, any Tailwind class left in a template renders as unstyled. Dashboard and detail page will look broken until all classes are replaced.
**Why it happens:** Templates have ~200 Tailwind utility classes across three files. Easy to miss some.
**How to avoid:** Do the CSS system first (Wave 1), then template rewrites (Wave 4). Do not remove the Tailwind CDN line until Wave 4 templates are complete, or remove it and do all three template files atomically.
**Warning signs:** Visual inspection — any element with no styling at all.

### Pitfall 2: Modal JS Uses Tailwind Class Toggles
**What goes wrong:** `base.html` modal JS uses `classList.add('opacity-0', 'translate-y-4')` and `classList.remove('hidden')`. These are Tailwind class names embedded in the JavaScript. When Tailwind is removed, toggling these classes does nothing visually.
**Why it happens:** The modal open/close animation relies on Tailwind's `opacity-0`, `translate-y-4`, and `hidden` classes. These need CSS equivalents in `style.css`.
**How to avoid:** Define `.hidden { display: none }`, `.opacity-0 { opacity: 0 }`, `.translate-y-4 { transform: translateY(1rem) }` — or rename the JS to use custom class names. Simplest: keep the same class names in CSS.
**Warning signs:** Modal does not open, or opens without animation.

### Pitfall 3: Edit Modal `data-*` Attributes and JS References
**What goes wrong:** `index.html` edit modal relies on `data-edit-item`, `data-edit-backdrop`, `data-close-edit-modal` attributes and JS that reads them. These have no Tailwind dependency — but the card redesign will restructure the HTML and the `data-edit-item` button may move or be removed if cards become purely clickable artwork tiles.
**Why it happens:** New card design (artwork fills card, click navigates to detail page per D-05) means the "Edit" button on the card face may need to be removed or repositioned. The edit modal JS assumes the button is present.
**How to avoid:** Decide where the Edit button lives in the new card design. If it is removed from the card (clean aesthetic), the edit functionality must still be accessible — the detail page already has its own edit pathway via `/wishlist/{id}/edit` form. Confirm this satisfies requirements before removing the card-level edit button. The planner should make this call explicit.

### Pitfall 4: FX Rate Fetch is Async — Router Context
**What goes wrong:** `_enrich_item()` is currently a sync function called from both sync and async contexts. Adding an async FX call inside it requires making it async, which cascades to callers.
**Why it happens:** `_enrich_item` is called in `main.py:index`, `main.py:item_detail`, and `wishlist.py:list_wishlist_items_api`. All are already async route handlers.
**How to avoid:** Make `_enrich_item` async and `await get_rate()` inside it. Or: resolve rates before calling `_enrich_item`, pass them in as a parameter (cleaner for testability). The pre-resolved approach is recommended: fetch rates once per request at the route handler level, pass into `_enrich_item`.
**Warning signs:** `RuntimeWarning: coroutine was never awaited` — this is a hard error that will surface immediately in testing.

### Pitfall 5: `cover_image` is Full-Resolution — Proxy Performance
**What goes wrong:** Discogs `cover_image` URLs are full-resolution JPEGs (500-600px). Streaming them through the artwork proxy on every page load will be slow for large wishlists.
**Why it happens:** No caching at the proxy layer is specified.
**How to avoid:** Use `thumb` (150px) for card grid thumbnails — it is in the same search response (`result.get("thumb")`). Store `thumb` URL as `artwork_url` (or store both). The detail page header can use `cover_image` if separately stored. For simplicity: store `thumb` — it is adequate for the 1:1 card grid and the 120px detail thumbnail. Add `Cache-Control: max-age=86400` response headers on the proxy endpoint to let the browser cache aggressively.
**Warning signs:** Slow dashboard load on wishlists with many items.

### Pitfall 6: artwork_url Column Missing from `_enrich_item` Dict
**What goes wrong:** `_enrich_item` constructs a plain dict from `WishlistItem` ORM fields. After adding `artwork_url` column, it will not appear in the enriched dict unless explicitly added.
**Why it happens:** The dict is built manually with listed fields — new ORM columns do not auto-appear.
**How to avoid:** Add `"artwork_url": item.artwork_url` to the returned dict in `_enrich_item`. Templates then reference `item.artwork_url`.

---

## Code Examples

### Landing Cost Display in Template (UI-04)
```html
<!-- item_detail.html — "All Listings" table, Landed (AU) column -->
<td class="px-4 py-3">
  {% if listing.aud_total is not none %}
    <span class="price-best">${{ '%.2f'|format(listing.aud_total) }}</span>
    <span class="text-muted" style="font-size: var(--text-sm); display: block;">
      {{ listing.orig_display }}
    </span>
  {% else %}
    <span class="text-faint">—</span>
  {% endif %}
</td>
<!-- Where listing.orig_display = "£22.00 + £8.00 shipping" computed in Python -->
```

### Artwork Image Tag in Card
```html
<!-- index.html — inside .card -->
{% if item.artwork_url %}
  <img
    class="card-artwork"
    src="/api/artwork?url={{ item.artwork_url | urlencode }}"
    alt="{{ item.query }} album cover"
    onerror="this.src='/static/vinyl-placeholder.svg'"
    loading="lazy"
  >
{% else %}
  <img
    class="card-artwork"
    src="/static/vinyl-placeholder.svg"
    alt="{{ item.query }} — no artwork available"
  >
{% endif %}
```

### TTLCache FX Pattern (extends existing cache.py pattern)
```python
# app/services/fx.py — mirrors TTLCache(maxsize=1, ttl=300) in cache.py
from cachetools import TTLCache
_fx_cache: TTLCache = TTLCache(maxsize=4, ttl=3600)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind CDN utility classes | CSS custom properties + semantic class names | This phase | Eliminates CDN dependency; stable, no version drift |
| USD-denominated landing prices | AUD-converted landing prices | This phase | Prices are directly meaningful to AU buyer |
| No artwork | Artwork from Discogs cover_image/thumb in search response | This phase | No extra API calls; field already returned in existing requests |

**Deprecated after this phase:**
- `<script src="https://cdn.tailwindcss.com">` in `base.html` — replaced by `static/style.css`
- All Tailwind utility class names in templates (`bg-slate-800`, `text-amber-400`, etc.) — replaced by CSS custom property-based class names

---

## Open Questions

1. **Edit button on new card design**
   - What we know: Current card has an "Edit" button. New design has artwork as the full card face with only title + price below, and full card click navigates to detail page (D-05).
   - What's unclear: Is the edit button retained on the card (breaks the clean artwork tile aesthetic) or removed (edit is only accessible from the detail page)?
   - Recommendation: Remove edit button from card. The detail page route is the natural place for edit/delete. The planner should make this explicit as a task note so it does not look like an accidental omission.

2. **`cover_image` vs `thumb` for stored URL**
   - What we know: Discogs search returns both `cover_image` (full-res ~600px) and `thumb` (150px). Both are available from the same search call.
   - What's unclear: Which to store as `artwork_url`? Full-res is better quality but heavier through the proxy.
   - Recommendation: Store `thumb` as `artwork_url`. It is sufficient for the card grid and the 120px detail thumbnail. Avoids proxy performance issues. If the detail page needs higher resolution later, a second column can be added.

3. **FX fetch failure handling**
   - What we know: `get_rate()` returns `None` on failure. `convert_to_aud` passes through `None`.
   - What's unclear: How should the template handle `None` AUD price — show original currency price, or `—`?
   - Recommendation: If AUD conversion fails, display the original price with its currency symbol as fallback (e.g. "USD 22.00"). Never show a blank or crash. Log the failure with `print("[FX] rate fetch failed")`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| cachetools | FX rate TTLCache | Yes | 7.0.5 | — |
| httpx | FX fetch + artwork proxy | Yes | 0.28.0 | — |
| exchangerate-api.com free endpoint | FX conversion | Yes | `open.er-api.com/v6/latest/{code}` — confirmed live 2026-04-03 | Skip FX if unreachable; show original currency |
| Discogs API (`cover_image` field) | Artwork capture | Yes | Confirmed in search response with token auth 2026-04-03 | Use `thumb` as fallback |
| System-ui font stack | Typography | Yes | Browser native | — |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

`nyquist_validation` is set to `false` in `.planning/config.json`. This section is skipped.

---

## Sources

### Primary (HIGH confidence)
- Live Discogs API call (2026-04-03) — confirmed `cover_image` and `thumb` present in `/database/search` response with token auth
- Live `open.er-api.com/v6/latest/USD` call (2026-04-03) — confirmed `result: success`, `rates.AUD: 1.44`, `rates.GBP: 0.75`, `time_eol: null`
- `app/services/cache.py` — existing TTLCache pattern directly reused for FX cache
- `app/models.py` — confirms `artwork_url` column is absent and needs adding
- `static/style.css` — confirms current file is 37-line micro-overrides, not a full design system
- `templates/base.html` — confirms Tailwind CDN script tag to remove; modal JS class dependencies identified
- `templates/index.html` — confirms full list of Tailwind classes to replace; card structure to rewrite
- `templates/item_detail.html` — confirms listing table structure; landed price already exists as `landed_price` dict key
- UI-SPEC.md — all token values, layout dimensions, copy strings sourced from this document

### Secondary (MEDIUM confidence)
- [ExchangeRate-API free docs](https://www.exchangerate-api.com/docs/free) — endpoint URL pattern; no-auth confirmed

### Tertiary (LOW confidence)
- [Discogs Forum - cover_image fields](https://www.discogs.com/forum/thread/765569) — forum reports of empty cover_image (auth issue) — superseded by our live test which returned valid URL with token auth

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries installed and version-verified
- CSS architecture: HIGH — full token system specified in UI-SPEC.md; no unknowns
- Artwork capture: HIGH — `cover_image` confirmed live in Discogs search response
- FX service: HIGH — `open.er-api.com` confirmed live, response format verified
- Template migration: HIGH — full template audit completed; JS class dependencies identified
- Pitfalls: HIGH — all identified from direct code inspection, not speculation

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain; FX endpoint has no deprecation flag)
