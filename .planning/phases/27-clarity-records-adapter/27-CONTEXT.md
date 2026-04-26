# Phase 27: Clarity Records Adapter - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Clarity Records as a new scraping source. Deliver a `clarity.py` adapter module, register it in `adapter.py`, and return standard `ListingDict` results. No UI changes — the existing item detail listing table already handles `is_in_stock: False` with opacity + "Sold Out" label.

</domain>

<decisions>
## Implementation Decisions

### Scraping approach
- **D-01:** Use BigCommerce search URL (`/search.php?search_query={query}`) — query-driven, consistent with every other adapter
- **D-02:** Fetch page 1 only — sufficient for targeted artist/album queries; pagination is not needed for single-store searches

### Store identity
- **D-03:** `ships_from: "Australia"`, `currency: "AUD"` — Clarity Records is an Australian store

### Stock handling
- **D-04:** Parse `is_in_stock` from BigCommerce HTML and include all listings (in-stock and sold-out). The item detail UI already renders `is_in_stock: False` rows at `opacity: 0.5` with a "Sold Out" badge — no UI changes required.

### Claude's Discretion
- CSS selectors for title, price, URL, image, and stock status (inspect BigCommerce HTML structure)
- Rate limiting / semaphore value (follow juno/bandcamp pattern of `Semaphore(1)`)
- Whether to use `lxml` or `html.parser` for BeautifulSoup
- Error handling and logging format (follow `[Clarity]` prefix convention)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing adapter patterns
- `app/services/juno.py` — primary reference: BeautifulSoup HTML scraping, Semaphore(1), rate-limit sleep, selector-based extraction
- `app/services/bandcamp.py` — secondary reference: same HTML scraping pattern, stock filtering approach
- `app/services/shopify.py` — reference for `ships_from`, `currency`, and `ListingDict` field population

### Adapter registration
- `app/services/adapter.py` — `ADAPTER_REGISTRY` — add import + entry here to wire the new adapter

### Return schema
- `app/services/adapter.py` — `ListingDict` TypedDict defines required and optional fields

### UI stock rendering (read-only, no changes needed)
- `templates/item_detail.html` lines 124–146 — existing `is_in_stock` opacity + "Sold Out" label

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- BeautifulSoup + httpx pattern: already in `juno.py` and `bandcamp.py` — copy structure directly
- `_HEADERS` dict with User-Agent: copy from juno/bandcamp
- `asyncio.Semaphore(1)`: rate limit pattern used by all HTML scrapers

### Established Patterns
- All HTML adapters: `async with _semaphore:` wrapping the httpx call
- All adapters: `print(f"[AdapterName] ...")` for logging
- All adapters: catch `httpx.HTTPError` and broad `Exception`, return `[]` on failure
- `ListingDict` fields: `source` (adapter key string), `title`, `url`, `price` (float), `currency`, `ships_from`, `is_in_stock` (bool)

### Integration Points
- New file: `app/services/clarity.py`
- Register in: `app/services/adapter.py` — add `from app.services import clarity` and entry in `ADAPTER_REGISTRY`

</code_context>

<specifics>
## Specific Ideas

- Sold-out listings should appear in item detail (not filtered) — the UI already renders them grayed out at opacity 0.5 with a "Sold Out" label via `is_in_stock: False`

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 27-clarity-records-adapter*
*Context gathered: 2026-04-26*
