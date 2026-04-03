# Roadmap: Vinyl Wishlist Manager

**Milestone:** v1 — Fast, Beautiful, More Sources
**Phases:** 3
**Requirements:** 16

---

## Phases

- [x] **Phase 1: Infrastructure** - Async scan decoupling, adapter registry, and dashboard caching so the foundation is solid before any new sources are added (completed 2026-04-02)
- [ ] **Phase 2: New Sources** - eBay AU, Discrepancy Records, Clarity Records, Juno Records, and Bandcamp adapters plugged into the registry
- [x] **Phase 3: UI Redesign** - Bootstrap removed, Spotify-like card layout with record artwork as the hero, custom CSS throughout (completed 2026-04-03)

---

## Phase Details

### Phase 1: Infrastructure
**Goal**: The app is fast and source-agnostic — adding a record returns immediately, the dashboard loads without N+1 queries, and new sources can be added by dropping in a file and updating one registry
**Depends on**: Nothing (first phase)
**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04, SRC-06
**Success Criteria** (what must be TRUE):
  1. Adding a wishlist item via the web form or iOS Shortcut returns a response in under 2 seconds; the background scan runs after the response is sent
  2. The dashboard loads noticeably faster than before; opening it does not fire a separate DB query for each wishlist item
  3. Visiting the dashboard twice within 5 minutes hits the cache; adding or scanning an item immediately shows fresh results on the next load
  4. The scanner does not fire more than 3–5 simultaneous Discogs requests; no 429 errors appear in logs during a full wishlist scan
  5. Adding a new scraping source requires only creating an adapter file and adding one entry to the registry — the scanner requires no changes
**Plans:** 3/3 plans complete

Plans:
- [x] 01-PLAN-1.md — Backend performance: scan decoupling, N+1 fix, cache, semaphore, scheduler parallelism
- [x] 01-PLAN-2.md — Adapter registry: source-agnostic scanner with registry pattern
- [x] 01-PLAN-3.md — Frontend polling UX: scanning spinner + dashboard auto-refresh

**UI hint**: no

### Phase 2: New Sources
**Goal**: The wishlist shows prices from eBay AU, two Australian record stores, Juno Records, and Bandcamp alongside existing Discogs and Shopify results
**Depends on**: Phase 1
**Requirements**: SRC-01, SRC-02, SRC-03, SRC-04, SRC-05
**Success Criteria** (what must be TRUE):
  1. Searching for a record on the dashboard returns listings from eBay AU (buy-it-now only, AUD landed cost shown)
  2. Discrepancy Records and Clarity Records listings appear for records they stock, with AUD prices and no shipping estimate required (AU-domestic)
  3. Juno Records listings appear for records they carry, with correct currency conversion to AUD
  4. Bandcamp listings appear for known artist/label searches where physical vinyl is available and in stock
  5. Each new source has its own rate limiting; a full wishlist scan completes without triggering bans or 429 errors on any source
**Plans:** 3/4 plans complete

Plans:
- [x] 02-01-PLAN.md — eBay Browse API adapter + rate limit migration to per-adapter semaphores
- [x] 02-02-PLAN.md — Discrepancy Records + Clarity Records AU HTML scrapers
- [x] 02-03-PLAN.md — Juno Records + Bandcamp international HTML scrapers
- [x] 02-04-PLAN.md — Gap closure: Clarity Records selector verification + enable adapter (SRC-03, SRC-06)

**UI hint**: no

### Phase 3: UI Redesign
**Goal**: The dashboard looks and feels like a polished personal tool — record artwork front and centre, dark palette, clean typography — and could be shown to someone without embarrassment
**Depends on**: Phase 2
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05, UI-06
**Success Criteria** (what must be TRUE):
  1. Bootstrap is gone; the layout holds up visually across all pages using only custom CSS and design tokens
  2. Each wishlist item on the dashboard is a card where the record cover artwork is the dominant visual element, with a graceful placeholder for items without art
  3. Every listing row shows a clear landed cost breakdown: base price, estimated shipping, AUD equivalent, and FX rate if applicable
  4. The entire app uses a consistent dark colour palette — no white backgrounds, no light-mode bleed
  5. The iOS Shortcut still adds records correctly; `POST /api/wishlist` with `X-API-Key` works unchanged
**Plans:** 4/4 plans complete

Plans:
- [x] 03-01-PLAN.md — CSS design system + Tailwind removal from base.html
- [x] 03-02-PLAN.md — Artwork pipeline: model column, Discogs capture, proxy endpoint, placeholder SVG
- [x] 03-03-PLAN.md — FX conversion service + AUD landed cost enrichment
- [x] 03-04-PLAN.md — Dashboard card grid + detail page rewrite + visual verification

**UI hint**: yes

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Infrastructure | 3/3 | Complete   | 2026-04-02 |
| 2. New Sources | 3/4 | Gap closure | - |
| 3. UI Redesign | 4/4 | Complete   | 2026-04-03 |
