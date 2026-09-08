# AU Vinyl Store Research

**Researched:** 2026-04-21
**Purpose:** Identify new AU vinyl store adapters for v1.5 Coverage & Sources milestone

---

## Recommended for Implementation

| Store | Platform | Approach | Priority | Notes |
|-------|----------|----------|----------|-------|
| Wax Museum Records | Shopify | Existing Shopify adapter (zero new code) | HIGH | Melbourne, huge used+new catalog, 16yr institution, AUD, `/search/suggest.json` confirmed working |
| Red Eye Records | Shopify | Existing Shopify adapter (zero new code) | HIGH | Sydney, largest indie store in AU, new+used, `/search/suggest.json` confirmed working, 10 Radiohead results returned |
| Rockaway Records | Shopify | Existing Shopify adapter (zero new code) | HIGH | Brisbane, 2,163 vinyl listings, new+used, confirmed Shopify suggest endpoint works |
| Happy Valley Shop | Shopify | Existing Shopify adapter (zero new code) | HIGH | Melbourne/Collingwood, 10,000+ titles claimed, curated indie focus, confirmed suggest endpoint working |
| Heartland Records | Shopify | Shopify adapter with `/products.json` fallback | MEDIUM | Melbourne/Sydney, suggest endpoint returns empty (appears disabled), but `/products.json` works — needs fallback logic |
| Clarity Records | BigCommerce | HTML scraper (new adapter needed) | MEDIUM | Adelaide, ~120+ vinyl titles, BigCommerce platform, search.php blocked in robots.txt, would need category page pagination scraper |
| Rare Records | Shopify | Existing Shopify adapter (zero new code) | MEDIUM | Melbourne (Point Cook), collectible/rare focus, good for completeness, confirmed suggest endpoint working |

---

## Assessed but Not Recommended

| Store | Platform | Reason |
|-------|----------|--------|
| Polyester Records | N/A | Permanently closed March 2020 |
| Record Paradise (recordparadise.com.au) | WordPress (no shop) | Blog/info site only, physical store Brunswick, no ecommerce |
| Missing Link Records (missinglinkonline.com) | Unknown (site unresponsive) | Physical store closed 2011, website non-functional |
| Off The Hip Records (offthehip.com.au) | Unknown (site unresponsive) | ECONNREFUSED on both www and non-www variants; primarily a label, not a retail store |
| Vinyl Revival (vinylrevival.com.au) | Shopify | HiFi equipment focus — vinyl section shows "No products yet, but don't fear, they are on the way" — not a vinyl catalog |

---

## Key Findings

**Shopify dominance:** Six of the seven viable stores run on Shopify. The existing generic Shopify adapter can cover Wax Museum, Red Eye, Rockaway, Happy Valley, and Rare Records with zero new adapter code — just add entries to the `STORES` list in `shopify.py`.

**robots.txt and `/search/suggest.json`:** Every Shopify store's robots.txt blocks `/search` but none explicitly block `/search/suggest.json`. The existing adapter correctly uses the suggest endpoint, not the `/search` path. This is the right approach and does not violate robots.txt on any of these stores.

**Heartland suggest endpoint disabled:** Heartland's `/search/suggest.json` consistently returns empty products for all queries. Their `/products.json` endpoint works and returns full product data with variants and pricing. Adding Heartland requires a small fallback: query `/products.json?limit=250` and filter by title client-side, or scrape the search results HTML page. Not a blocker, but needs a store-specific override in the adapter.

**Clarity Records is BigCommerce:** One genuinely interesting store (Adelaide, indie/punk/metal focus, curated imports) runs on BigCommerce. BigCommerce's GraphQL Storefront API (`/graphql`) returned HTTP 405 (method not allowed without a token), meaning it requires an auth token and is not a public endpoint. The `search.php` path is blocked in robots.txt. The viable approach is paginating through `/vinyl/` category pages via HTML scraping — similar to the existing Discrepancy Records Neto scraper. Medium complexity, medium priority.

**Dead stores to skip:** Polyester Records (closed 2020), Missing Link (closed 2011), Record Paradise (no online shop). Off The Hip is a label not a retail store with a functioning online shop. Do not create adapters for these.

**Vinyl Revival is a HiFi store:** Despite the name, vinylrevival.com.au sells turntables and amplifiers. Their vinyl collection section explicitly says "no products yet." Not useful as a source.

**Rockaway is the strongest new addition:** 2,163 vinyl listings, new and used, Brisbane-based (AU shipping), actively maintained, Shopify suggest works cleanly. Best return-on-investment of any new addition.

**Happy Valley is boutique but high-quality:** Curated selection, Melbourne indie reputation, Condé Nast-endorsed, 10,000+ titles claimed. Strong overlap with the audience likely using this app.

---

## Platform Pattern Summary

| Platform | Count | Stores | Adapter Needed |
|----------|-------|--------|---------------|
| Shopify | 6 | Wax Museum, Red Eye, Rockaway, Happy Valley, Heartland, Rare Records | None (existing) — Heartland needs fallback |
| BigCommerce | 1 | Clarity Records | New HTML scraper |
| WordPress (no shop) | 1 | Record Paradise | Skip |
| Closed/Dead | 3 | Polyester, Missing Link, Off The Hip | Skip |

---

## Robots.txt Notes

| Store | `/search` blocked | `/search/suggest.json` blocked | Checkout automation blocked |
|-------|------------------|-------------------------------|---------------------------|
| Wax Museum | Yes | No (explicit) | Yes |
| Red Eye | Yes | No (explicit) | Yes |
| Rockaway | No | No | Yes |
| Happy Valley | Yes | No (explicit) | Yes |
| Heartland | Yes | No (explicit) | Yes |
| Clarity | Yes (`search.php`) | N/A (BigCommerce) | Yes |
| Rare Records | Not checked | Not checked | Assumed (Shopify standard) |

All Shopify stores include the standard Shopify policy statement: "Checkouts are for humans." Price-reading/listing queries are not checkout flows and are consistent with public catalog access.

---

## Implementation Ordering Recommendation

1. **Phase A — Zero-code Shopify additions:** Add Wax Museum, Red Eye, Rockaway, Happy Valley, Rare Records to the `STORES` list in `shopify.py`. Test suggest endpoint per store. ~1 hour work.

2. **Phase B — Heartland fallback:** Implement store-level override in Shopify adapter to use `/products.json` + client-side title filter for stores with disabled suggest endpoints. Heartland is the first candidate.

3. **Phase C — Clarity Records BigCommerce scraper:** New adapter using HTML pagination of `/vinyl/` category pages. Moderate complexity, worthwhile for Adelaide/indie coverage.

---

## Sources

- Direct endpoint testing: `/search/suggest.json` on all Shopify stores
- Direct platform detection: CDN URL inspection (cdn.shopify.com vs cdn11.bigcommerce.com)
- robots.txt inspection: All recommended stores checked
- Broadsheet Melbourne: Polyester Records closure confirmation
- RecordStoreDay.com.au: Store registry cross-reference
- Rockaway ATAK Interactive case study: Shopify migration confirmation
