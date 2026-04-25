# Phase 26: Shopify Store Expansion - Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Add five standard Shopify stores to the STORES list in `app/services/shopify.py`, and add Heartland Records with a products.json fallback (their suggest endpoint is disabled). No new adapter file. No UI changes.

</domain>

<decisions>
## Implementation Decisions

### Standard stores
- **D-01:** Add Wax Museum Records, Red Eye Records, Rockaway Records, Happy Valley Shop, and Rare Records as new entries in the `STORES` list. Same dict shape: `key`, `name`, `base_url`. These use the existing `_search_store` path — no code changes needed beyond adding the entries.

### Heartland fallback design
- **D-02:** Heartland Records uses a separate `_search_store_products_json` function. Do NOT branch inside `_search_store` — keep the existing function untouched to avoid regression risk on the 6 working stores.
- **D-03:** Heartland's store dict gets a `"search_type": "products_json"` field. `search_and_get_listings` checks this flag and routes Heartland to the separate function instead of `_search_store`.
- **D-04:** All other stores (including the 5 new ones) have no `search_type` field — they continue through the existing `_search_store` path.

### products.json match strategy
- **D-05:** Single request: `GET /products.json?limit=250`. No pagination — one request per scan, consistent with every other store being one request.
- **D-06:** Client-side filtering: simple substring match — `query.lower() in product["title"].lower()`. Same approach as what suggest.json does under the hood.
- **D-07:** Cap results at `max_results` (same default 5 as other stores).

### Claude's Discretion
- Exact store `key` slug format (follow existing snake_case pattern)
- Field extraction from products.json response shape (title, price, handle, available, images)
- Error handling shape for products.json path (follow existing try/except pattern in `_search_store`)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Source Expansion — SRC-07 through SRC-12 acceptance criteria

### Existing implementation
- `app/services/shopify.py` — Full file: STORES list, `_search_store`, `search_and_get_listings` — all code to modify lives here
- `.planning/ROADMAP.md` §Phase 26 — Success criteria, constraint "no new adapter file"

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_search_store(client, store, query, max_results)` — existing suggest.json path, stays unchanged
- `search_and_get_listings` — entry point; currently fans out to all STORES via `_search_store`; needs routing logic for Heartland
- `_HEADERS` dict — reuse for products.json requests

### Established Patterns
- Store dict shape: `{"key": str, "name": str, "base_url": str}` — add `"search_type": "products_json"` only for Heartland
- Error handling: `except httpx.HTTPError` + `except Exception` with `print(f"[Shopify] ...")` — follow same pattern in new function
- Result dict shape: `source`, `title`, `price`, `currency`, `ships_from`, `url`, `condition`, `is_in_stock`, `seller`, `image_url` — must match exactly

### Integration Points
- `search_and_get_listings` fans out via `asyncio.gather` — Heartland needs to be included in the gather but routed to the new function
- `max_results` param flows through from scanner — pass through to products.json function the same way

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for store URLs (planner to verify correct Shopify base URLs for each store during research).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 26-shopify-store-expansion*
*Context gathered: 2026-04-25*
