# Architecture Research

**Project:** Vinyl Wishlist Manager
**Researched:** 2026-04-02
**Scope:** Subsequent milestone — existing FastAPI monolith, four architectural questions

---

## Adapter Pattern for New Sources

### Current State

The existing codebase has an implicit adapter contract: every source module exposes one top-level async function:

```python
async def search_and_get_listings(query: str, item_type: str) -> list[dict]:
    ...
```

`scanner.py` hard-codes imports of `discogs` and `shopify` and calls them explicitly in `asyncio.gather()`. Adding Juno/Bandcamp/eBay requires editing `scanner.py` every time.

### Recommended: typing.Protocol (structural interface)

Use `typing.Protocol` to define the adapter contract, then register adapters in a list that the scanner iterates. No inheritance required — any module that implements the right signature satisfies the protocol automatically (structural subtyping, PEP 544).

**Why Protocol over ABC:**
- Existing adapters satisfy it without modification (no base class to add retroactively)
- No import coupling between `scanner.py` and specific adapter modules
- mypy/pyright can enforce the contract at type-check time

**Adapter protocol definition** (`app/services/adapter.py`):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SourceAdapter(Protocol):
    async def search_and_get_listings(
        self, query: str, item_type: str
    ) -> list[dict]:
        ...
```

But because the existing adapters are modules (not class instances), the simplest pattern is a callable-level protocol — a type alias for the function signature — combined with a registry list:

```python
# app/services/registry.py
from app.services import discogs, shopify

ADAPTERS = [
    discogs.search_and_get_listings,
    shopify.search_and_get_listings,
    # add: juno.search_and_get_listings
    # add: bandcamp.search_and_get_listings
]
```

**Scanner becomes source-agnostic:**

```python
# app/services/scanner.py
from app.services.registry import ADAPTERS

async def scan_item(db, item):
    results = await asyncio.gather(
        *[adapter(item.query, item.type) for adapter in ADAPTERS],
        return_exceptions=True,
    )
    all_results = []
    for r in results:
        if isinstance(r, Exception):
            print(f"[Scanner] Adapter error: {r}")
        else:
            all_results.extend(r)
    ...
```

**Adding a new source:** create `app/services/juno.py` with `search_and_get_listings(query, item_type) -> list[dict]`, then add one line to `registry.py`. Scanner never changes.

### Standardised Listing Dict

Codify the expected keys as a `TypedDict` so new adapters know exactly what to return:

```python
# app/services/adapter.py
from typing import TypedDict

class ListingDict(TypedDict, total=False):
    source: str       # required
    title: str        # required
    url: str          # required (dedup key)
    price: float | None
    currency: str
    condition: str | None
    seller: str | None
    ships_from: str | None
    is_in_stock: bool
```

**Confidence:** HIGH — pattern is structural, requires no new dependencies, validated against existing code.

---

## Scan Decoupling Pattern

### Current Problem

Both the web form (`POST /wishlist/add`) and the iOS Shortcut API (`POST /api/wishlist`) call `await scanner.scan_item(db, item)` synchronously before returning the response. A full scan takes several seconds (multiple Discogs API calls with `asyncio.sleep(0.5)` between them). The user stares at a spinner; the iOS Shortcut times out at its configured limit.

### Recommended: FastAPI BackgroundTasks with its own DB session

`BackgroundTasks` is built into FastAPI/Starlette. Tasks run in the same process, in the same async event loop, **after** the HTTP response is sent. Zero extra dependencies.

**The DB session pitfall:** the `db: Session = Depends(get_db)` session is closed at end-of-request. The background task cannot use it. The task must open its own session from `SessionLocal` directly.

**Pattern:**

```python
# In route handler
from fastapi import BackgroundTasks

async def _scan_in_background(item_id: int):
    """Opens its own DB session — never uses the request-scoped one."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        item = db.query(WishlistItem).filter_by(id=item_id).first()
        if item:
            new_listings = await scanner.scan_item(db, item)
            if item.notify_email and new_listings:
                await notifier.send_deal_email(item, new_listings)
    except Exception as e:
        print(f"[BG scan] Error for item {item_id}: {e}")
    finally:
        db.close()

@web_router.post("/wishlist/add")
async def add_wishlist_item_web(
    ...,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    item = WishlistItem(...)
    db.add(item)
    db.commit()
    db.refresh(item)
    background_tasks.add_task(_scan_in_background, item.id)   # fire and forget
    return RedirectResponse(url="/?toast=Item+added%2C+scanning+in+background", status_code=303)
```

The same pattern applies to `create_wishlist_item_api` — pass `scan=True` as a flag, still fire the task in background and return the unscannd item immediately.

### Why not asyncio.create_task()?

`asyncio.create_task()` starts the coroutine immediately in the current event loop iteration, before the response is sent. There is also no reference kept to the task, which creates a garbage collection race — Python may cancel it. You would need to store the task reference explicitly. `BackgroundTasks` handles this lifecycle correctly and is the FastAPI-native approach for this exact use case.

### Why not Celery/Redis?

Overkill for a single-user personal tool on Railway. Adds two new services (broker + worker) with operational overhead. `BackgroundTasks` runs in-process; for a scan that takes 3-10 seconds and only fires on item add, that is exactly the right tool.

**Confidence:** HIGH — documented FastAPI pattern; DB session pitfall verified from official docs and community discussion.

---

## In-Process Caching Pattern

### Current Problem

Every `GET /` request calls `_enrich_item()` for every wishlist item. Each call iterates `item.listings` (already loaded by SQLAlchemy relationship) and computes `compute_typical_price()`. This is pure CPU work on data that only changes when a scan runs, but it runs on every page load.

### Recommended: cachetools TTLCache

`functools.lru_cache` has no TTL — the cached enrichment would never expire between scans. `cachetools.TTLCache` solves this with a configurable expiry.

**Install:** `pip install cachetools` (tiny, no infrastructure, actively maintained — v7.0.5 current as of 2025).

**Pattern — cache the full enriched dashboard:**

```python
# app/services/cache.py
from cachetools import TTLCache
from cachetools.keys import hashkey

_dashboard_cache: TTLCache = TTLCache(maxsize=1, ttl=300)  # 5 minutes

def get_cached_dashboard(db) -> list[dict] | None:
    key = hashkey("dashboard")
    return _dashboard_cache.get(key)

def set_cached_dashboard(db, data: list[dict]) -> None:
    key = hashkey("dashboard")
    _dashboard_cache[key] = data

def invalidate_dashboard_cache() -> None:
    _dashboard_cache.clear()
```

Call `invalidate_dashboard_cache()` at the end of `scan_item()` and after any wishlist mutation (add, edit, delete). Dashboard route checks cache first; only re-computes on miss.

**Alternative — cache per item:**

```python
_item_cache: TTLCache = TTLCache(maxsize=200, ttl=300)

@cached(cache=_item_cache, key=lambda item, *a: hashkey(item.id))
def enrich_item_cached(item: WishlistItem) -> dict:
    return _enrich_item(item)
```

Per-item cache is finer grained but requires invalidating individual keys after scan. Whole-dashboard cache (maxsize=1) is simpler — one key, one clear call. Use whole-dashboard for the MVP; per-item if the wishlist grows large.

### What not to do

Do not use `functools.lru_cache` on `_enrich_item` — the `WishlistItem` ORM object is not hashable by default and the cache never expires. Do not try to add Redis for this — a 5-minute in-process TTL is sufficient for a single-user personal tool.

**Confidence:** HIGH — cachetools is well-established, pattern is straightforward; invalidation approach verified against the data flow in scanner.py.

---

## Frontend Approach

### Goal

Spotify-like aesthetic: record artwork as the visual anchor, dark background, minimal chrome, information hierarchy that leads with the album cover rather than text. Server-rendered Jinja2 — no React, no build step.

### Recommended Stack: Custom CSS (no Bootstrap)

Bootstrap is the source of the current "generic/bootstrap-ish" look. Remove it entirely. Write ~200 lines of custom CSS using:

- CSS custom properties (variables) for the design token layer (colours, spacing, type scale)
- CSS Grid for the card layout
- `aspect-ratio: 1 / 1` for artwork squares
- `object-fit: cover` on `<img>` for artwork fill

No JavaScript framework. Minimal vanilla JS only where strictly needed (toast dismissal, optimistic UI feedback on scan trigger).

### CSS Variable Layer (design tokens)

```css
:root {
  --bg-base: #121212;
  --bg-elevated: #1e1e1e;
  --bg-highlight: #2a2a2a;
  --accent: #1db954;          /* Spotify green — swap for any accent */
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --text-muted: #6a6a6a;
  --radius-card: 8px;
  --gap: 1.5rem;
}
```

### Card Layout

```css
.record-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--gap);
}

.record-card {
  background: var(--bg-elevated);
  border-radius: var(--radius-card);
  padding: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.record-card:hover { background: var(--bg-highlight); }

.record-card__art {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 4px;
  background: var(--bg-highlight);   /* placeholder when no art */
}

.record-card__title {
  font-weight: 700;
  margin-top: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.record-card__meta {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
```

### Artwork Sourcing

This is the hardest part. Options in priority order:

1. **Discogs cover image** — the Discogs API returns `cover_image` URLs in search results. Store this URL on `WishlistItem` as `cover_url` column. Populate during scan.
2. **MusicBrainz Cover Art Archive** — free, public API, no auth. `https://coverartarchive.org/release/{mbid}/front`. Requires MBID lookup but very reliable for well-known releases.
3. **Placeholder SVG** — a vinyl disc SVG as the default when no art found. Keep it CSS-drawn rather than an image asset.

Store `cover_url` (nullable) on `WishlistItem`. Template conditionally renders `<img src="{{ item.cover_url }}">` or falls back to the placeholder. Do not proxy images through the app — link directly to Discogs CDN.

### Jinja2 Template Structure

Keep the `base.html` / `index.html` / `item_detail.html` split that already exists. Add:

- `templates/components/record_card.html` — Jinja2 macro for a single card, pulled into `index.html` via `{% from 'components/record_card.html' import record_card %}`
- `templates/components/listing_row.html` — macro for a single listing row in the detail view

Macros keep the logic in one place; the grid template stays clean.

### Minimal JS (vanilla, no framework)

Three specific interactions that benefit from JS:

1. **Toast auto-dismiss** — `setTimeout(() => toast.remove(), 3000)` on any `?toast=` query param message
2. **Scan button state** — disable button and show spinner text after click to prevent double-submit
3. **Artwork error fallback** — `<img onerror="this.src='/static/placeholder.svg'">` or a tiny inline handler

All three are < 20 lines total. Do not reach for Alpine.js or HTMX unless scan feedback becomes an explicit requirement.

### What to Avoid

- Bootstrap or any CSS framework — they produce the generic look you are escaping
- Inline styles in templates — use CSS classes and the variable layer
- JavaScript for layout — CSS Grid handles it entirely
- Lazy-loading artwork via AJAX — server renders the URL; browser fetches it directly

**Confidence:** MEDIUM-HIGH — CSS patterns are well-established; artwork sourcing depends on Discogs API response structure which needs verification when implementing the artwork column.

---

## Cross-Cutting Notes for Roadmap

| Concern | Interaction |
|---------|-------------|
| Scan decoupling + adapter registry | Both change `scanner.py` — do in same phase |
| Cover art column | Requires DB migration (`cover_url` on `WishlistItem`) — bundle with UI phase |
| Cache invalidation | Must be added when scan decoupling is added — otherwise stale dashboard after background scan |
| iOS Shortcut compatibility | `POST /api/wishlist` response changes if `scan=True` returns before scan completes — item will have no listings yet. Shortcut only checks HTTP 200/201; no impact on contract. |

---

## Sources

- [FastAPI Background Tasks — official docs](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [BackgroundTasks blocks entire FastAPI — community discussion](https://github.com/fastapi/fastapi/discussions/11210)
- [cachetools documentation](https://cachetools.readthedocs.io/en/stable/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python Protocols — mypy docs](https://mypy.readthedocs.io/en/stable/protocols.html)
- [TTL LRU Cache in FastAPI — Medium](https://medium.com/@priyanshu009ch/ttl-lru-cache-in-python-fastapi-2ca2a39258dc)
- [Spotify-inspired layout with CSS Grid — CodePen](https://codepen.io/sheelah/pen/qYPwBK)
