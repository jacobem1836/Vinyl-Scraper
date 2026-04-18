# Phase 2: New Sources - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Add five new source adapters — eBay AU, Discrepancy Records, Clarity Records, Juno Records, and Bandcamp — and register each in the adapter registry (`app/services/adapter.py`). All adapters implement the existing `async def search_and_get_listings(query, item_type) -> list[dict]` contract.

This phase is backend-only. No UI changes, no FX conversion display, no dashboard redesign — those are Phase 3.

</domain>

<decisions>
## Implementation Decisions

### eBay AU Adapter (SRC-01)
- **D-01:** Use the eBay Browse API (not HTML scraping). Filter to buy-it-now listings only. Target `EBAY_AU` marketplace. Return standard listing dicts with AUD prices (eBay AU already prices in AUD — no conversion needed).
- **D-02:** Adapter requires an `EBAY_APP_ID` and `EBAY_CERT_ID` env var. If unset, adapter returns `[]` immediately (config guard). User has applied for eBay Developer Program; credentials not yet available.
- **D-03:** OAuth app token (client credentials flow) is cached at module level with a TTL of ~7000s (just under the 7200s expiry). Fetch once, reuse across scans. Avoids an extra round-trip on every scan.

### AU Store Adapters — Discrepancy Records (SRC-02) and Clarity Records (SRC-03)
- **D-04:** Both stores are AU-based and price in AUD. Set `ships_from: "Australia"` in the listing dict — the existing shipping table already has `Australia: 8.0` (AUD estimate).
- **D-05:** Discrepancy Records uses the Neto platform. Clarity Records uses BigCommerce. Both require HTML scraping. Return standard listing dicts.

### Juno Records Adapter (SRC-04)
- **D-06:** HTML scraping of Juno search results. Must set a correct `User-Agent` header to avoid being blocked (per SRC-04 requirement).
- **D-07:** Juno prices in GBP. Adapter returns native currency (`currency: "GBP"`, `ships_from: "United Kingdom"`). No conversion in Phase 2 — the existing shipping table handles GBP shipping estimate. FX conversion to AUD is deferred to Phase 3 UI.

### Bandcamp Adapter (SRC-05)
- **D-08:** Scrape `bandcamp.com/search?q={query}&item_type=p` (physical merch results page). Filter results to vinyl-only by checking merch type in response HTML.
- **D-09:** If no physical vinyl is found for a query, return `[]` silently. Digital-only results are not surfaced.
- **D-10:** Scope is search-based — not general marketplace scraping. Works for all item_type values (album, artist, label, subject).

### Currency Handling
- **D-11:** Adapters return native currency in the `currency` field. No FX conversion happens in Phase 2. Current listing dict already stores `currency` — nothing changes.
- **D-12:** Phase 3 will add AUD-equivalent display with live FX rates (fetched from a free API like exchangerate.host, cached with TTL). This is out of scope for Phase 2.
- **D-13:** `_landed()` in wishlist.py continues to use raw price + shipping estimate — both in the listing's native currency. This is consistent with existing Discogs (USD) behaviour.

### Per-Source Rate Limiting
- **Claude's Discretion:** Implement module-level semaphores in each adapter file rather than extending the registry schema. This is the production-appropriate approach: each adapter owns its own concurrency policy.
  - eBay: `asyncio.Semaphore(5)` — Browse API allows high concurrency
  - Discogs (existing): leave at global Semaphore(3)
  - HTML scrapers (Juno, Discrepancy, Clarity, Bandcamp): `asyncio.Semaphore(1)` + `asyncio.sleep(1–2s)` between requests
  - Remove the global scan_semaphore from `rate_limit.py` — each adapter self-limits. Scanner's `asyncio.gather()` across adapters remains unchanged.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, iOS Shortcut API contract, constraints
- `.planning/REQUIREMENTS.md` — SRC-01 through SRC-05 acceptance criteria (exact specs for each adapter)

### Phase 1 Decisions
- `.planning/phases/01-infrastructure/01-CONTEXT.md` — Adapter registry format (D-10 to D-12), scanner concurrency (D-09), listing dict contract

### Codebase
- `app/services/adapter.py` — Current registry (Discogs + Shopify entries). New adapters added here.
- `app/services/scanner.py` — How adapters are invoked (`asyncio.gather`, `return_exceptions=True`)
- `app/services/discogs.py` — Reference implementation of adapter interface
- `app/services/shopify.py` — Second reference implementation
- `app/services/shipping.py` — Shipping cost table (Australia, United Kingdom already present)
- `app/services/rate_limit.py` — Current global semaphore (will be replaced by per-adapter approach)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AdapterFn` type alias in `adapter.py`: `Callable[[str, str], Awaitable[list[dict]]]` — new adapters must match this signature
- `ListingDict` TypedDict in `adapter.py` — standardised return shape; all adapters use this
- `get_shipping_cost(ships_from)` in `shipping.py` — already handles Australia (8.0) and United Kingdom (18.0); no changes needed for Phase 2
- `asyncio.Semaphore` pattern in `rate_limit.py` — copy this pattern into each adapter module

### Established Patterns
- Adapters silently return `[]` on any error (logged to stdout with `[Source]` prefix)
- All adapters are async and use `httpx.AsyncClient(timeout=20.0)`
- Scanner calls `asyncio.gather(*[a["fn"](...) for a in adapters], return_exceptions=True)` — adapter errors are isolated
- Registry entries: `{"name": str, "fn": AdapterFn, "enabled": bool}` — add new entries at bottom of ADAPTER_REGISTRY list

### Integration Points
- `app/services/adapter.py:ADAPTER_REGISTRY` — add one dict per new source
- `app/config.py` — add `ebay_app_id`, `ebay_cert_id` settings (optional, no default); same pattern as `discogs_token`
- `app/services/rate_limit.py` — global semaphore to be retired in favour of per-adapter semaphores

</code_context>

<specifics>
## Specific Ideas

- eBay: user has applied for eBay Developer Program but credentials not yet available. The adapter should be fully implemented but gated behind a config check so it can be enabled by adding env vars to Railway once approved.
- Juno note from REQUIREMENTS.md out-of-scope section: "Juno selectors (if blocked) — Requires live browser inspection; defer to execution phase — may fall back to v2". Planner should note that Juno HTML selectors may need adjustment during execution.

</specifics>

<deferred>
## Deferred Ideas

- AUD display / FX conversion — Phase 3 UI work (live rate API, cached, shown alongside native price)
- Per-item condition filtering (DATA-01) — v2 requirement, not this phase
- Historical price tracking (DATA-02) — v2 requirement, not this phase
- Egg Records (SRC-07) and international stores beyond Juno (SRC-08) — explicitly deferred in REQUIREMENTS.md

</deferred>

---

*Phase: 02-new-sources*
*Context gathered: 2026-04-02*
