# Roadmap: Vinyl Wishlist Manager

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-04-05)
- ✅ **v1.1 UX Polish & Album Selection** — Phases 6–12 (shipped 2026-04-12)
- ✅ **v1.2 Signal Intelligence & Notifications** — Phases 13–15 (shipped 2026-04-14)
- ✅ **v1.3 Visual Overhaul** — Phases 16–19 (shipped 2026-04-18)
- ✅ **v1.4 Quality & Gaps** — Phases 20–24 (shipped 2026-04-21)
- 🔄 **v1.5 Coverage & Sources** — Phases 25–27 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–5) — SHIPPED 2026-04-05</summary>

- [x] Phase 1: Infrastructure (3/3 plans) — completed 2026-04-02
- [x] Phase 2: New Sources (4/4 plans) — completed 2026-04-03
- [x] Phase 3: UI Redesign (4/4 plans) — completed 2026-04-03
- [x] Phase 4: UI Polish (3/3 plans) — completed 2026-04-05
- [x] Phase 5: Improve UI/UX (3/3 plans) — completed 2026-04-05

</details>

<details>
<summary>✅ v1.1 UX Polish & Album Selection (Phases 6–12) — SHIPPED 2026-04-12</summary>

- [x] Phase 6: Discogs Typeahead (3/3 plans) — completed 2026-04-09
- [x] Phase 7: Image Priority + Scan Fix (2/2 plans) — completed 2026-04-09
- [x] Phase 8: Brand Font Upgrade (1/1 plan) — completed 2026-04-09
- [x] Phase 9: Email Redesign (2/2 plans) — completed 2026-04-09
- [x] Phase 10: UI Polish (3/3 plans) — completed 2026-04-11
- [x] Phase 11: UI Fixes (5/5 plans) — completed 2026-04-11
- [x] Phase 12: UI Fixes Round 2 (2/2 plans) — completed 2026-04-11

</details>

<details>
<summary>✅ v1.2 Signal Intelligence & Notifications (Phases 13–15) — SHIPPED 2026-04-14</summary>

- [x] Phase 13: Signal Filters (3/3 plans) — completed 2026-04-13
- [x] Phase 14: Feedback Primitives UI Hint (1/1 plan) — completed 2026-04-13
- [x] Phase 15: Notification Expansion (4/4 plans) — completed 2026-04-13

</details>

<details>
<summary>✅ v1.3 Visual Overhaul (Phases 16–19) — SHIPPED 2026-04-18</summary>

- [x] Phase 16: Visual Foundation (2/2 plans) — completed 2026-04-15
- [x] Phase 17: Typography Overhaul (3/3 plans) — completed 2026-04-15
- [x] Phase 18: UI Consistency Fixes (2/2 plans) — completed 2026-04-18
- [x] Phase 19: Card Layout Expansion (1/1 plan) — completed 2026-04-18

See archive: `.planning/milestones/v1.3-ROADMAP.md`

</details>

<details>
<summary>✅ v1.4 Quality & Gaps (Phases 20–24) — SHIPPED 2026-04-21</summary>

- [x] Phase 20: Cleanup & Config (1/1 plan) — completed 2026-04-18
- [x] Phase 21: Bug Fixes (1/1 plan) — completed 2026-04-19
- [x] Phase 22: Resend Email (1/1 plan) — completed 2026-04-18
- [x] Phase 23: Discogs Release Selection (1/1 plan) — completed 2026-04-20
- [x] Phase 24: Per-Item Notification Thresholds (1/1 plan) — completed 2026-04-21

See archive: `.planning/milestones/v1.4-ROADMAP.md`

</details>

### v1.5 Coverage & Sources (Phases 25–27)

- [x] **Phase 25: eBay Credentials** — Wire eBay credentials to config and verify adapter returns results (completed 2026-04-25)
- [ ] **Phase 26: Shopify Store Expansion** — Add 5 Shopify stores to STORES list plus Heartland fallback logic
- [ ] **Phase 27: Clarity Records Adapter** — New BigCommerce HTML scraper for clarityrecords.com.au

## Phase Details

### Phase 25: eBay Credentials
**Goal**: The eBay adapter is wired to real credentials and returns AU listings for wishlist items
**Depends on**: Nothing (standalone config + credential wiring)
**Requirements**: EBAY-01, EBAY-02
**Success Criteria** (what must be TRUE):
  1. A scan against an active wishlist item returns eBay AU listings alongside Discogs and Shopify results
  2. The `.env.example` file documents EBAY_APP_ID, EBAY_CERT_ID, and EBAY_DEV_ID with descriptions
  3. Starting the app without eBay credentials logs a visible warning, but the app still starts
**Plans**: 1 plan
- [x] 25-01-PLAN.md — Document eBay credentials in .env.example and wire startup warning; verify live scan returns AU listings

### Phase 26: Shopify Store Expansion
**Goal**: Five additional AU Shopify stores and Heartland Records are queryable through the existing scanner
**Depends on**: Phase 25
**Requirements**: SRC-07, SRC-08, SRC-09, SRC-10, SRC-11, SRC-12
**Success Criteria** (what must be TRUE):
  1. Scanning a well-known album returns results from Wax Museum, Red Eye, Rockaway, Happy Valley, and Rare Records when those stores carry it
  2. Scanning an album carried by Heartland Records returns Heartland listings (via products.json fallback path)
  3. No new adapter file is introduced — all five standard stores are entries in the STORES list; Heartland uses a store-level fallback flag
**Plans**: 2 plans
- [ ] 26-01-PLAN.md — Add 5 standard Shopify stores to STORES list (SRC-07 through SRC-11)
- [ ] 26-02-PLAN.md — Add Heartland Records via products.json fallback path (SRC-12)

### Phase 27: Clarity Records Adapter
**Goal**: Clarity Records (Adelaide) is a queryable source and returns vinyl listings via HTML category page scraping
**Depends on**: Phase 26
**Requirements**: SRC-13
**Success Criteria** (what must be TRUE):
  1. Scanning a title stocked by Clarity Records returns at least one Clarity listing with price, title, and URL
  2. The adapter paginates through `/vinyl/` category pages and does not miss results that appear only on page 2+
  3. The adapter is registered in the adapter registry and participates in normal scheduled scans without extra config
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure | v1.0 | 3/3 | Complete | 2026-04-02 |
| 2. New Sources | v1.0 | 4/4 | Complete | 2026-04-03 |
| 3. UI Redesign | v1.0 | 4/4 | Complete | 2026-04-03 |
| 4. UI Polish | v1.0 | 3/3 | Complete | 2026-04-05 |
| 5. Improve UI/UX | v1.0 | 3/3 | Complete | 2026-04-05 |
| 6. Discogs Typeahead | v1.1 | 3/3 | Complete | 2026-04-09 |
| 7. Image Priority + Scan Fix | v1.1 | 2/2 | Complete | 2026-04-09 |
| 8. Brand Font Upgrade | v1.1 | 1/1 | Complete | 2026-04-09 |
| 9. Email Redesign | v1.1 | 2/2 | Complete | 2026-04-09 |
| 10. UI Polish | v1.1 | 3/3 | Complete | 2026-04-11 |
| 11. UI Fixes | v1.1 | 5/5 | Complete | 2026-04-11 |
| 12. UI Fixes Round 2 | v1.1 | 2/2 | Complete | 2026-04-11 |
| 13. Signal Filters | v1.2 | 3/3 | Complete | 2026-04-13 |
| 14. Feedback Primitives UI Hint | v1.2 | 1/1 | Complete | 2026-04-13 |
| 15. Notification Expansion | v1.2 | 4/4 | Complete | 2026-04-13 |
| 16. Visual Foundation | v1.3 | 2/2 | Complete | 2026-04-15 |
| 17. Typography Overhaul | v1.3 | 3/3 | Complete | 2026-04-15 |
| 18. UI Consistency Fixes | v1.3 | 2/2 | Complete | 2026-04-18 |
| 19. Card Layout Expansion | v1.3 | 1/1 | Complete | 2026-04-18 |
| 20. Cleanup & Config | v1.4 | 1/1 | Complete | 2026-04-18 |
| 21. Bug Fixes | v1.4 | 1/1 | Complete | 2026-04-19 |
| 22. Resend Email | v1.4 | 1/1 | Complete | 2026-04-18 |
| 23. Discogs Release Selection | v1.4 | 1/1 | Complete | 2026-04-20 |
| 24. Per-Item Notification Thresholds | v1.4 | 1/1 | Complete | 2026-04-21 |
| 25. eBay Credentials | v1.5 | 1/1 | Complete    | 2026-04-25 |
| 26. Shopify Store Expansion | v1.5 | 0/1 | Not started | - |
| 27. Clarity Records Adapter | v1.5 | 0/1 | Not started | - |

*Last updated: 2026-04-21 — v1.5 Coverage & Sources roadmap created*
