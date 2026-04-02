# Requirements: Vinyl Wishlist Manager

**Defined:** 2026-04-02
**Core Value:** Show me the cheapest way to buy the records I want, right now.

## v1 Requirements

### Performance

- [ ] **PERF-01**: Adding a wishlist item returns an HTTP response immediately; scanning runs as a background task after the response is sent
- [ ] **PERF-02**: Dashboard load uses selectinload (or equivalent) to batch-fetch listings in a single query rather than N+1 per item
- [ ] **PERF-03**: Dashboard enrichment result is cached with a TTL of ~5 minutes; cache is invalidated on any wishlist mutation or scan completion
- [ ] **PERF-04**: Concurrent scan requests across all sources are rate-limited via a semaphore (max 3–5 simultaneous Discogs requests) to prevent 429 errors

### Sources

- [ ] **SRC-01**: eBay AU adapter queries the eBay Browse API (not HTML), filters buy-it-now only, targets `EBAY_AU` marketplace, and returns results in the standard listing dict format
- [ ] **SRC-02**: Discrepancy Records adapter scrapes the Discrepancy Records storefront (Neto platform) and returns standard listing dicts with AUD prices
- [ ] **SRC-03**: Clarity Records adapter scrapes the Clarity Records storefront (BigCommerce platform) and returns standard listing dicts with AUD prices
- [ ] **SRC-04**: Juno Records adapter scrapes Juno Records HTML search results (with correct User-Agent header) and returns standard listing dicts
- [ ] **SRC-05**: Bandcamp adapter performs artist/label search and returns physical vinyl listings (merch/records only, not digital); scope-limited to search — not general marketplace scraping
- [ ] **SRC-06**: All new sources are registered in a central adapter registry; adding or removing a source requires only a change to the registry, not to the scanner

### UI

- [ ] **UI-01**: Bootstrap is removed and replaced with custom CSS using design tokens (CSS custom properties) for colours, spacing, and typography
- [ ] **UI-02**: Dashboard displays wishlist items as a card grid where record cover artwork is the visual hero of each card
- [ ] **UI-03**: Album art is fetched from the Discogs API at scan time, stored as a URL in the database, and served via a local proxy endpoint — Discogs CDN is never hotlinked directly from the browser
- [ ] **UI-04**: Each listing shows a clear landed cost breakdown: base price + estimated shipping + AUD equivalent (with FX rate noted)
- [ ] **UI-05**: Dark colour palette applied consistently across all pages (background, cards, text, accents)
- [ ] **UI-06**: Existing iOS Shortcut API contract (`POST /api/wishlist` with `X-API-Key`) is preserved unchanged through all UI and backend changes

## v2 Requirements

### Data Quality

- **DATA-01**: Per-item condition filter — user can set minimum condition (e.g. VG+) per wishlist item; listings below that condition are excluded from best-price and deal alerts
- **DATA-02**: Historical price tracking — "typical price" baseline computed from sold prices (Popsike or similar) rather than active listings only

### Sources (Deferred)

- **SRC-07**: Egg Records adapter (Common Ground platform) — deferred pending platform API investigation
- **SRC-08**: International stores beyond Juno (e.g. Boomkat, Forced Exposure) — defer until AU sources are stable

### Notifications

- **NOTIF-01**: In-app deal badge on dashboard cards (highlight items with new listings below threshold, without requiring email)

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / multi-user | Personal tool — single user only |
| Mobile app | iOS Shortcut handles mobile adds; web is desktop-first |
| Purchasing / bidding | Discovery only — not transactional |
| Import duty / GST modelling | Too complex for marginal accuracy gain; note as approximation |
| Juno selectors (if blocked) | Requires live browser inspection; defer to execution phase — may fall back to v2 |
| Bandcamp general marketplace search | No public search API; only artist/label-targeted search is feasible |
| Redis / Celery / task queue | Overkill for single-user tool; BackgroundTasks + APScheduler sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PERF-01 | Phase 1: Infrastructure | Pending |
| PERF-02 | Phase 1: Infrastructure | Pending |
| PERF-03 | Phase 1: Infrastructure | Pending |
| PERF-04 | Phase 1: Infrastructure | Pending |
| SRC-06 | Phase 1: Infrastructure | Pending |
| SRC-01 | Phase 2: New Sources | Pending |
| SRC-02 | Phase 2: New Sources | Pending |
| SRC-03 | Phase 2: New Sources | Pending |
| SRC-04 | Phase 2: New Sources | Pending |
| SRC-05 | Phase 2: New Sources | Pending |
| UI-01 | Phase 3: UI Redesign | Pending |
| UI-02 | Phase 3: UI Redesign | Pending |
| UI-03 | Phase 3: UI Redesign | Pending |
| UI-04 | Phase 3: UI Redesign | Pending |
| UI-05 | Phase 3: UI Redesign | Pending |
| UI-06 | Phase 3: UI Redesign | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-02*
*Last updated: 2026-04-02 after roadmap creation*
