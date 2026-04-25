# Phase 26: Shopify Store Expansion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-25
**Phase:** 26-shopify-store-expansion
**Areas discussed:** Heartland fallback design, products.json match strategy

---

## Heartland Fallback Design

| Option | Description | Selected |
|--------|-------------|----------|
| A — Flag + branch in `_search_store` | Add `use_products_json: True` to store dict; branch inside existing function | |
| B — Separate `_search_store_products_json` function | Route from `search_and_get_listings` based on `search_type` flag; keep `_search_store` clean | ✓ |
| C — `fallback_endpoint` field | Store dict carries fallback URL; `_search_store` tries suggest then falls back | |

**User's choice:** B (on Claude recommendation)
**Notes:** User asked for recommendation. Claude recommended B to avoid regression risk on 6 existing stores — `_search_store` stays untouched. Route via `search_type: "products_json"` flag on Heartland's store dict.

---

## products.json Match Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| 1 — First page + substring | Single `?limit=250` request, `query.lower() in title.lower()` | ✓ |
| 2 — All pages + substring | 4–5 requests to cover full catalog, same filter | |
| 3 — All pages + word-overlap | Full catalog load, smarter multi-word matching | |

**User's choice:** 1 (on Claude recommendation based on existing implementation)
**Notes:** User asked "what do you recommend based on my current implementation." Claude noted existing `_search_store` does one request per store and caps at `max_results=5`. Loading all pages for one fallback store would be inconsistent. First page (250 products) sufficient for a vinyl-specialist store.

---

## Claude's Discretion

- Exact store `key` slug format
- Field extraction from products.json response shape
- Error handling shape for products.json path

## Deferred Ideas

None.
