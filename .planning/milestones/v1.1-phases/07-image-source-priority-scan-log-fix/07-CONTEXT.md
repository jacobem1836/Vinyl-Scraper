# Phase 7: Image Source Priority + Scan Log Fix - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Record artwork shows the scraped store image when available, and scan log messages use the correct item type label. Three requirements: IMG-01, IMG-02, BUG-02.

</domain>

<decisions>
## Implementation Decisions

### Image storage model
- **D-01:** Add `image_url` column to the Listing model. Each listing stores its own product image URL from its source. Scanner picks the best image for `WishlistItem.artwork_url` at scan time using the priority rule below.

### Image priority rule
- **D-02:** Priority chain for `WishlistItem.artwork_url`: store image (first non-None from any store adapter) > Discogs `_cover_image` > existing value. Same pattern as current `_cover_image` pop logic in `scanner.py:32-40` — just extended to also check `image_url` on newly created Listing rows.

### Which scrapers to update
- **D-03:** Update all 6 non-Discogs adapters (eBay, Shopify stores, Discrepancy, Juno, Bandcamp, Clarity) to extract product image URLs where available. Each adapter already parses HTML/API responses — adding image extraction is incremental. Adapters that can't reliably find an image return `None` (no error).

### Scan log type label fix (BUG-02)
- **D-04:** Include `item_type` in `scan_status.item_finished()` log entries (currently only stores `query` + `new_listings`). Display type in the completed scan log in `base.html` alongside the query name.

### Claude's Discretion
- Image proxy caching strategy (current 24hr cache is fine, adjust if needed)
- Exact HTML selector / API field for each adapter's image extraction
- Scan log message format (as long as type label is correct)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Image pipeline
- `app/models.py` — WishlistItem.artwork_url (line 18), Listing model (lines 24-45) — add image_url here
- `app/services/scanner.py` — _cover_image pop logic (lines 32-40) — extend with store image priority
- `app/services/discogs.py` — _cover_image attachment pattern (lines 109, 182, 254, 326)
- `app/routers/wishlist.py` — /api/artwork proxy endpoint (lines 228-243)

### Store adapters (all need image extraction)
- `app/services/ebay.py`
- `app/services/shopify.py`
- `app/services/discrepancy.py`
- `app/services/juno.py`
- `app/services/bandcamp.py`
- `app/services/clarity.py`

### Scan log
- `app/services/scan_status.py` — item_finished() missing item_type (lines 32-40)
- `templates/base.html` — renderStatus() JS (lines 209-224) — completed log display

### Templates
- `templates/index.html` — Dashboard card image rendering (lines 151-165)
- `templates/item_detail.html` — Detail page image rendering (lines 15-28)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `/api/artwork` proxy endpoint already handles any image URL with caching — no changes needed for store images
- `_cover_image` pattern in result dicts is established — store adapters can use the same key or `image_url` directly on Listing
- `vinyl-placeholder.svg` exists as final fallback

### Established Patterns
- Adapters return standardized dicts; scanner pops special keys (`_cover_image`) before persisting
- `scan_status.py` uses simple dict-based state tracking
- All adapters already parse HTML/JSON responses — image extraction is additive

### Integration Points
- `scanner.py:scan_item()` — where image priority logic lives, needs to check store images first
- `scan_status.item_finished()` — needs `item_type` parameter added
- Each adapter's listing dict construction — add `image_url` key
- Alembic migration for Listing.image_url column

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-image-source-priority-scan-log-fix*
*Context gathered: 2026-04-07*
