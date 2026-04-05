# Architecture Research

**Domain:** Subsequent milestone additions to existing FastAPI + Jinja2 + SQLAlchemy 2 app
**Researched:** 2026-04-05
**Confidence:** HIGH — based on direct codebase inspection + FastAPI/Discogs official docs

---

## System Overview (Current v1.0 State)

```
Browser / iOS Shortcut
        |
        v
┌───────────────────────────────────────────────────────────┐
│  FastAPI app  (app/main.py)                                │
│                                                            │
│  web_router  (GET /, GET /item/{id}, POST /wishlist/add…)  │
│  api_router  (POST /api/wishlist, DELETE /api/wishlist/{})  │
│  GET /api/artwork  — image proxy                           │
│  POST /api/scan/start, GET /api/scan/status               │
│  GET /api/health                                          │
└──────────────────────┬────────────────────────────────────┘
                       |
          ┌────────────┼────────────┐
          v            v            v
   scanner.py      notifier.py   fx.py / shipping.py
   (coordinates    (email HTML    (price calculations)
    adapters)       + SMTP)
          |
   ┌──────┴─────────────────────┐
   | Adapter registry           |
   | discogs  shopify  ebay     |
   | discrepancy  juno  bandcamp|
   └──────┬─────────────────────┘
          |
          v
   SQLAlchemy ORM
   WishlistItem  Listing
          |
   PostgreSQL (Railway) / SQLite (dev)
```

Templates:  base.html / index.html / item_detail.html  (Jinja2, server-rendered)
CSS:        static/style.css  (~545 lines, CRATE design system)
JS:         inline in base.html + index.html + item_detail.html (no build step)

---

## v1.1 Feature Integration Map

### Feature 1: Discogs Typeahead

**What it is:** As the user types in the "query" field of the add/edit form, fetch matching album names from Discogs `/database/search` and show a dropdown of suggestions. Selecting a suggestion fills the form field with the precise Discogs release title.

**New component:** One new endpoint, one block of inline JS.

**New endpoint — `GET /api/discogs/search`** in `app/routers/wishlist.py` (or a small new router if preferred):

```
GET /api/discogs/search?q=dark+side&type=album
→ JSON: [{"title": "Pink Floyd - The Dark Side Of The Moon", "year": "1973", "thumb": "https://..."}, ...]
```

- No authentication required (internal UI call only, no iOS Shortcut contract).
- Calls `discogs.py`'s existing `_get_headers()` and the `/database/search` endpoint directly. The logic is almost identical to the first few lines of `_get_album_listings()` — search with `type=release&format=Vinyl`, return the top 5 results as lightweight JSON (title, year, thumb URL).
- Do NOT call the full `search_and_get_listings()` — that makes follow-up release detail calls and is too slow for typeahead (~3-6s). A single search call returns in ~300ms.
- Rate limit: Discogs allows 60 requests/min per authenticated token. Typeahead fires on keystroke; debounce at ~350ms in JS to avoid overwhelming the limit.

**Integration point — `app/services/discogs.py`:**

Add a new public function `async def search_suggestions(query: str, item_type: str, limit: int = 6) -> list[dict]`. This function calls `/database/search` once and returns lightweight dicts. The existing `search_and_get_listings` is untouched.

**Integration point — `app/routers/wishlist.py`:**

Add the GET endpoint. No changes to existing routes. No auth dependency needed (this is a browser-only call from the add/edit form).

**Integration point — `templates/index.html`:**

Add `<div class="typeahead-dropdown">` beneath the query `<input>` in both the Add modal and the Edit modal. The JS listens to `input` events on the query field, debounces at 350ms, fetches `/api/discogs/search?q=...&type=...`, and populates a dropdown list. Selecting a result writes to the input and hides the dropdown. No changes to form submit logic — the typeahead only populates the field.

**Data flow:**

```
User types in query input
  → JS debounce (350ms)
    → GET /api/discogs/search?q=...&type=...
      → discogs.search_suggestions()
        → Discogs /database/search API
          → returns [{title, year, thumb}]
            → JS renders dropdown
              → user clicks suggestion
                → input.value = suggestion.title
                  → dropdown hidden
                    → form submits normally (POST /wishlist/add)
```

**Component summary:**

| Component | Change type | Details |
|-----------|-------------|---------|
| `app/services/discogs.py` | ADD function | `search_suggestions(query, item_type, limit)` — single Discogs search call |
| `app/routers/wishlist.py` | ADD endpoint | `GET /api/discogs/search` — calls `search_suggestions`, returns JSON |
| `templates/index.html` | MODIFY | Typeahead dropdown markup + JS in Add and Edit modals |

---

### Feature 2: Image Source Prioritisation

**What it is:** Currently, `scanner.py` takes the first `_cover_image` it finds across all adapter results and assigns it to `item.artwork_url`. All adapters except Discogs return no `_cover_image` at all (the key is only set in `discogs.py`). The feature asks: if a non-Discogs store adapter scrapes a product image, prefer that over the Discogs thumbnail.

**Current state (scanner.py lines 29–36):**

```python
cover_image = None
for r in all_results:
    ci = r.pop("_cover_image", None)
    if ci and not cover_image:
        cover_image = ci
for r in all_results:
    r.pop("_cover_image", None)
```

This takes the first `_cover_image` found. Since `asyncio.gather` returns adapters in registry order, and Discogs is first in the registry, Discogs currently wins by position — not by priority rule.

**No store adapters currently emit `_cover_image`.** Shopify's `suggest.json` endpoint does return a `featured_image` field. Bandcamp product pages and Juno product pages have cover art in HTML. eBay returns item images. However, none of the current adapters extract or forward image URLs — they return only price/stock/URL data.

**What actually needs to change:**

1. **Store adapters that have cover images:** Shopify's `suggest.json` returns `{"featured_image": {"url": "...", "width": 300, "height": 300}}` per product. Shopify store adapters can extract `product.get("featured_image", {}).get("url")` and include `"_cover_image": url` in the result dict. This is 2 lines per product in `shopify.py`.

2. **Priority logic in scanner.py:** Replace "first wins" with "store image wins over Discogs". Classify by source: images from non-Discogs sources are "store images" (usually higher resolution, store-specific). Discogs images are the fallback.

**Recommended priority logic:**

```python
cover_image = None
discogs_fallback = None
for r in all_results:
    ci = r.pop("_cover_image", None)
    source = r.get("source", "")
    if ci:
        if source == "discogs":
            if discogs_fallback is None:
                discogs_fallback = ci
        else:
            if cover_image is None:
                cover_image = ci
# Use store image if found; fall back to Discogs
final_cover = cover_image or discogs_fallback
```

**Note:** The `_cover_image` key is a sidecar on result dicts (not stored in `Listing`). The pop/discard pattern already ensures it never reaches the DB. Scanner then conditionally sets `item.artwork_url`. This logic change is entirely within `scanner.py`.

**Component summary:**

| Component | Change type | Details |
|-----------|-------------|---------|
| `app/services/scanner.py` | MODIFY | Replace first-wins with store-first fallback logic (~8 lines) |
| `app/services/shopify.py` | MODIFY | Extract `featured_image.url` from product dicts, set `_cover_image` on results |
| Other adapters (bandcamp, juno, ebay) | OPTIONAL | Can add `_cover_image` later; scanner handles gracefully with/without |

---

### Feature 3: CRATE Font Upgrade

**What it is:** Swap the `--font-sans` CSS variable from the system font stack to a custom web font. The CRATE design uses system fonts today (`-apple-system, BlinkMacSystemFont, "Segoe UI", …`). The upgrade introduces a brand-appropriate typeface loaded as a `@font-face` or via Google Fonts CDN link.

**Integration points — static assets + CSS only. No Python changes.**

**Option A: Variable font from Google Fonts (CDN):**

Add one `<link>` in `templates/base.html` head, then update `--font-sans` in `static/style.css`:

```html
<!-- base.html <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
```

```css
/* style.css */
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
```

**Option B: Self-hosted `@font-face` (no CDN dependency):**

Place the font files in `static/fonts/`. Reference via `@font-face` at the top of `style.css`. No base.html changes required.

**Recommendation:** Self-hosted. The app already serves from Railway with static files. A CDN dependency adds a network round-trip on every page load and a privacy risk (Google Fonts logs IPs). Self-hosting 2 WOFF2 files (~50KB each) is trivial and faster.

**Component summary:**

| Component | Change type | Details |
|-----------|-------------|---------|
| `static/style.css` | MODIFY | Update `--font-sans`, add `@font-face` if self-hosting |
| `static/fonts/` | ADD | Font files (WOFF2) if self-hosting |
| `templates/base.html` | MODIFY | Add `<link>` only if using Google Fonts CDN |

---

### Feature 4: Email HTML Redesign

**What it is:** Replace the current plain `<table border="1">` email HTML in `notifier.py` with a designed, CRATE-branded HTML email template.

**Current state in `notifier.py`:**

The `html_body` is built inline in `send_deal_email()` via string concatenation. There is no template file — it is a raw Python string. The result is a generic HTML table with inline CSS, visually inconsistent with the CRATE UI.

**Integration options:**

**Option A: Jinja2 template for email (recommended)**

Create `templates/email_deal.html`. In `notifier.py`, instantiate Jinja2 directly (not via FastAPI's `templates` object — notifier has no access to the request context):

```python
from jinja2 import Environment, FileSystemLoader

_env = Environment(loader=FileSystemLoader("templates"))

def _render_email(item, listings) -> str:
    template = _env.get_template("email_deal.html")
    return template.render(item=item, listings=listings)
```

This separates HTML from logic, makes the template editable without touching Python, and keeps `notifier.py` clean.

**Option B: Inline HTML string (current approach, improved)**

Keep string building but add proper inline CSS. No new files required. Faster to implement but harder to maintain.

**Recommendation:** Jinja2 template (Option A). The template file is easy to iterate, designer-readable, and the Jinja2 dependency already exists in the project.

**Email HTML constraints:**
- Use inline CSS only — email clients strip `<style>` blocks and do not support external stylesheets.
- Avoid CSS custom properties — not supported in most email clients.
- Stick to table layout for the listing rows — email clients (particularly Outlook) do not support CSS Grid or Flexbox reliably.
- Dark mode in email is unreliable; use a light background (#ffffff or near-white) with dark text for maximum compatibility, even if the web UI is dark.

**Component summary:**

| Component | Change type | Details |
|-----------|-------------|---------|
| `app/services/notifier.py` | MODIFY | Replace inline HTML string with Jinja2 template render |
| `templates/email_deal.html` | ADD | CRATE-branded HTML email template with inline CSS |

---

### Feature 5: UI Polish (CSS + Markup)

**What it is:** A set of targeted CSS fixes to `static/style.css` and minor markup corrections in `templates/`. All documented in `ui-to-improve.txt` (the full UI analysis in the project root).

**These are CSS/HTML-only changes. No Python changes.**

**Changes are isolated to two files:**

| File | Changes |
|------|---------|
| `static/style.css` | Type scale, button states (`:focus-visible`, `:active`, `:disabled`), color contrast fix (`--color-text-faint` → `#686868`), 3-column grid breakpoint at 1024px, card hover shadow fix, spacing system cleanup |
| `templates/index.html` | Fix overlapping buttons (layout/z-index), card title hierarchy (`text-sm` → slightly larger), scan log type label fix (Python scan_status template variable) |
| `templates/item_detail.html` | H1/H2 visual distinction, table row border removal |

**Scan log type label fix** ("no artist results" → correct type label) is in the JS `renderStatus()` function in `base.html` — the `c.type` display in the scan active panel. This is a one-line JS change.

---

## Build Order

Dependencies between features determine order. The typeahead endpoint must exist before JS can call it; scanner image changes are independent; CSS/HTML are all independent.

```
Phase 1: Discogs Typeahead Endpoint
  discogs.py (add search_suggestions)
    → wishlist.py (add GET /api/discogs/search)
      → index.html (add typeahead JS + dropdown markup)

Phase 2: Image Source Prioritisation
  shopify.py (emit _cover_image from featured_image)
    → scanner.py (store-first priority logic)

Phase 3: CRATE Font Upgrade
  static/fonts/ (add WOFF2 files)
    → static/style.css (update --font-sans, add @font-face)

Phase 4: Email HTML Redesign
  templates/email_deal.html (new template)
    → notifier.py (switch to Jinja2 render)

Phase 5: UI Polish
  static/style.css (all CSS fixes)
  templates/index.html (button layout, card hierarchy, scan log)
  templates/item_detail.html (heading scale, table)
  templates/base.html (scan log type label JS fix)
```

**Rationale for this order:**
- Typeahead first: it adds a new backend endpoint and new frontend interaction, touching the most files. Getting it working validates the Discogs search function shape before the email phase touches notifier.
- Image prioritisation second: scanner.py change is independent of all UI work; it produces correct data before any display work happens.
- Font and email are isolated: neither depends on anything else, and neither is depended upon. They can run in any order or be done in the same session.
- UI polish last: after all logic changes are in place, a single CSS pass cleans up everything visible at once. Polish after content is stable.

---

## Component Change Summary

| Component | Change Type | Why |
|-----------|------------|-----|
| `app/services/discogs.py` | ADD function | `search_suggestions()` for typeahead — separate from full scan path |
| `app/routers/wishlist.py` | ADD endpoint | `GET /api/discogs/search` — lightweight, no auth |
| `app/services/shopify.py` | MODIFY | Emit `_cover_image` from Shopify `featured_image` field |
| `app/services/scanner.py` | MODIFY | Store-first cover image priority (~8 lines) |
| `app/services/notifier.py` | MODIFY | Replace inline HTML string with Jinja2 template render |
| `templates/email_deal.html` | ADD | CRATE-branded email template (inline CSS only) |
| `templates/index.html` | MODIFY | Typeahead dropdown markup + JS in both modals |
| `templates/base.html` | MODIFY (minor) | Font CDN link (if CDN) or no change (if self-hosted); scan log JS fix |
| `templates/item_detail.html` | MODIFY | Heading scale, table border |
| `static/style.css` | MODIFY | Type scale, button states, contrast fix, 3-col breakpoint, spacing |
| `static/fonts/` | ADD | WOFF2 font files (if self-hosting) |

**Not changed:** `app/models.py`, `app/database.py`, `app/main.py`, `app/scheduler.py`, `app/config.py`, all other service adapters (bandcamp, ebay, juno, discrepancy). No migrations required — no new columns.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Typeahead calling full scan path

**What people do:** Wire the typeahead to call `search_and_get_listings()` or even `/api/scan/start`, since that function already searches Discogs.

**Why it's wrong:** `search_and_get_listings()` makes sequential Discogs API calls with `asyncio.sleep(0.5)` between each release detail request — it takes 3–8 seconds. A typeahead needs a response in under 500ms. The full scan path is designed for completeness, not latency.

**Do this instead:** `search_suggestions()` calls `/database/search` once and returns immediately. No follow-up release detail calls.

### Anti-Pattern 2: Email template using CSS custom properties

**What people do:** Apply the CRATE design system CSS variables (`var(--color-bg)`, etc.) to the email template, since they already exist in `style.css`.

**Why it's wrong:** Email clients (Gmail, Apple Mail, Outlook) do not support CSS custom properties. The email will render with no colors.

**Do this instead:** Inline all color values as hex literals in the email template. Maintain a small comment block at the top of `email_deal.html` mapping token names to hex values for readability.

### Anti-Pattern 3: Modifying `Listing` model to store cover image

**What people do:** Add an `image_url` column to `Listing` so each listing carries its own artwork reference.

**Why it's wrong:** The cover image is a property of the album (the `WishlistItem`), not of an individual store listing. Storing it on `Listing` means the same artwork would be duplicated across every listing for an item, requiring a migration with no benefit.

**Do this instead:** Keep `artwork_url` on `WishlistItem` where it already lives. The `_cover_image` sidecar on adapter result dicts is a transient key that never reaches the DB.

### Anti-Pattern 4: Typeahead calling Discogs on every keystroke

**What people do:** Add an `addEventListener('input', fetch(...))` with no debounce.

**Why it's wrong:** A fast typist hits 5–8 keystrokes per second. Without debounce, 5 rapid keystrokes trigger 5 simultaneous Discogs API calls. Discogs rate-limits at 60 req/min per token; this burns through the quota quickly and the last response may arrive out of order (the first query "dark" resolves after "dark side").

**Do this instead:** Debounce at 350ms. Only send the request when the user has paused typing. Cancel any pending fetch if the input changes before the timer fires.

---

## Integration Points

### Existing Boundary: Discogs token in settings

`discogs.py` reads `settings.discogs_token`. The new `search_suggestions()` function uses the same token and the same `_get_headers()` helper. No new config keys needed.

### Existing Boundary: `/api/artwork` proxy

The typeahead suggestions include `thumb` URLs from Discogs. These can be displayed inline in the dropdown by the browser directly (no proxy needed — thumbnail URLs are public CDN). The `/api/artwork` proxy is only needed for the full-resolution artwork stored on `WishlistItem.artwork_url`, where it handles auth headers and caching. Keep the boundary as-is.

### Existing Boundary: `_cover_image` sidecar protocol

The `_cover_image` key on adapter result dicts is an undeclared but effective protocol between adapters and `scanner.py`. The `ListingDict` TypedDict in `adapter.py` does not include it (it is a transient key for `scanner.py` to consume and discard). No change needed to `ListingDict` — document the sidecar as a scanner-level convention, not a typed contract.

### New Boundary: `/api/discogs/search` endpoint visibility

This endpoint has no auth. It is intended only for use by the browser UI. If the app were ever made multi-user or public, this endpoint would expose unmetered Discogs API usage. For a single-user personal tool on a private Railway deployment this is acceptable. Note it in a comment at the route definition.

---

## Sources

- Discogs API — `/database/search` response structure: https://www.discogs.com/developers/#page:database,header:database-search
- Discogs rate limits (60 req/min authenticated): https://support.discogs.com/hc/en-us/articles/360001676934
- FastAPI endpoint routing — official docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- HTML email CSS support matrix: https://www.caniemail.com/
- Jinja2 standalone Environment (without Flask/FastAPI): https://jinja.palletsprojects.com/en/3.1.x/api/#basics
- Shopify Storefront suggest.json — featured_image field: confirmed in `shopify.py` existing call structure

---

*Architecture research for: Vinyl Wishlist Manager v1.1 — UX Polish & Album Selection*
*Researched: 2026-04-05*
