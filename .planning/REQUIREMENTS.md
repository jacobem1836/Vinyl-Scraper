# Requirements: Vinyl Wishlist Manager — v1.5 Coverage & Sources

**Defined:** 2026-04-21
**Core Value:** Show me the cheapest way to buy the records I want, right now.

## v1.5 Requirements

Expand scraper coverage with new AU vinyl stores and get the eBay adapter working with real credentials. No UI changes — all backend adapter work.

### eBay Activation

- [ ] **EBAY-01**: eBay credentials (EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID) documented in `.env.example` and wired to `app/config.py` with startup warning when absent
- [ ] **EBAY-02**: eBay adapter returns listings for active wishlist items in production

### Source Expansion — Shopify (zero new code)

- [ ] **SRC-07**: User sees Wax Museum Records listings in scan results (Melbourne — new+used catalog)
- [ ] **SRC-08**: User sees Red Eye Records listings in scan results (Sydney — largest indie store AU)
- [ ] **SRC-09**: User sees Rockaway Records listings in scan results (Brisbane — 2,163 vinyl listings)
- [ ] **SRC-10**: User sees Happy Valley Shop listings in scan results (Melbourne — 10,000+ curated titles)
- [ ] **SRC-11**: User sees Rare Records listings in scan results (Melbourne — collectible/rare focus)

### Source Expansion — Shopify with fallback

- [ ] **SRC-12**: User sees Heartland Records listings in scan results (Melbourne/Sydney — products.json fallback required, suggest endpoint disabled)

### Source Expansion — New adapter

- [ ] **SRC-13**: User sees Clarity Records listings in scan results (Adelaide — BigCommerce, new HTML scraper via category page pagination)

## Future Requirements

See `.planning/FUTURE.md` for deferred work (auth, streaming integrations, mobile app + Spine View, notifications expansion, security audit).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Vinyl Revival | HiFi equipment store — vinyl section explicitly empty |
| Polyester Records | Permanently closed March 2020 |
| Missing Link Records | Physical store closed 2011, site non-functional |
| Off The Hip | Record label, not a retail store |
| Record Paradise | No ecommerce — physical store only |
| Collection / purchase tracking | Discogs already handles this better |
| UI changes | This milestone is pure backend adapter work |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| EBAY-01 | Phase 25 | Pending |
| EBAY-02 | Phase 25 | Pending |
| SRC-07 | Phase 26 | Pending |
| SRC-08 | Phase 26 | Pending |
| SRC-09 | Phase 26 | Pending |
| SRC-10 | Phase 26 | Pending |
| SRC-11 | Phase 26 | Pending |
| SRC-12 | Phase 26 | Pending |
| SRC-13 | Phase 27 | Pending |

**Coverage:**
- v1.5 requirements: 9 total
- Mapped to phases: 9 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-21*
*Last updated: 2026-04-21 — traceability filled after roadmap creation*
