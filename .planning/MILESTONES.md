# Milestones

## v1.5 Coverage & Sources (Shipped: 2026-04-27)

**Phases completed:** 3 phases (25–27), 4 plans
**Timeline:** 2026-04-25 → 2026-04-27 (2 days)

**Key accomplishments:**

- eBay credentials documented in .env.example with startup warning when creds are absent (Phase 25)
- 5 AU Shopify stores added (Wax Museum, Red Eye, Rockaway, Happy Valley, Rare Records) — expanded from 6 to 11 stores (Phase 26)
- Heartland Records added as 12th store via products.json fallback path (first non-suggest.json Shopify store) (Phase 26)
- Clarity Records BigCommerce HTML scraper re-implemented (`clarity.py`, 131 lines) and registered as 7th adapter with AUD pricing and stock detection (Phase 27)

---

## v1.3 Visual Overhaul (Shipped: 2026-04-18)

**Phases completed:** 4 phases (16–19), 6 plans
**Timeline:** 2026-04-14 → 2026-04-18 (4 days)

**Key accomplishments:**

- True black (#000) palette across all surfaces — dashboard, cards, detail, modals (Phase 16)
- Custom 4px translucent-white scrollbars with hover brightening (Phase 16)
- Warner Music–inspired aesthetic: stark white-on-black, editorial restraint (Phase 16)
- Gothic A1 self-hosted font (Light/Regular/Medium woff2) replaces Inter; loaded via @font-face preload (Phase 17)
- Item name visibly larger and heavier than price across cards, detail, and modals (Phase 17)
- Post-add toast unified with scan toast via `window.showToast()` — no more separate scan panel (Phase 18)
- Item detail placeholder swapped to empty vinyl PNG asset (Phase 18)
- Card grid expanded to 3-col max with wider gap and tighter container margins (Phase 19)

---

## v1.2 Signal Intelligence & Notifications (Shipped: 2026-04-14)

**Phases completed:** 3 phases (13–15), 8 plans

**Key accomplishments:**

- Relevance scoring + digital listing filter — suppress noise, rank by match quality
- `ships_from` enriched via Discogs marketplace API on every scan
- Relevance threshold applied at query time in dashboard and detail routes
- Consistent toast feedback system: all UI actions use single `#toast` primitive
- Add-item modal always opens with Type = "album" (capture-phase reset)
- Back-in-stock and price-drop detection with prev snapshot columns
- Cooldown deduplication prevents repeat sends within configurable window
- Collect-then-dispatch scheduler: one unified digest email per scan run
- 9 unit tests covering all notification scenarios (NOTIF-01 through NOTIF-04)

---

## v1.1 UX Polish & Album Selection (Shipped: 2026-04-12)

**Phases completed:** 7 phases, 16 plans, 19 tasks

**Key accomplishments:**

- One-liner:
- Discogs typeahead dropdown in add/edit modals with debounced search, keyboard nav, and artist/label support
- Hide typeahead spinner in all user-initiated exit paths (selectResult, resetTypeahead, type change)
- One-liner:
- One-liner:
- One-liner:
- 1. D-13 — JetBrains Mono font skipped
- 1. [Rule 2 - Missing] text-sm in JS innerHTML strings (base.html)
- One-liner:
- One-liner:
- Placeholder 28x28 logo SVG saved and wired into CRATE nav bar left of Bodoni Moda wordmark; user to swap SVG for final design
- One-liner:
- One-liner:

---

## v1.0 MVP (Shipped: 2026-04-05)

**Phases completed:** 5 phases, 17 plans, 18 tasks

**Key accomplishments:**

- Scan decoupled from HTTP via BackgroundTasks; dashboard N+1 fixed with selectinload; TTLCache added; scheduler parallelized with asyncio.gather + semaphore(3)
- One-liner:
- CSS spinner + JS polling on dashboard cards auto-refreshes when background scan produces listings, completing the PERF-01 scan-decoupling UX loop
- eBay AU Browse API adapter with OAuth token caching and FIXED_PRICE filter; global scan_semaphore replaced by per-adapter Semaphore(5) in ebay.py
- HTML scrapers for two Australian vinyl stores using BeautifulSoup: Discrepancy Records (Neto, live and working) and Clarity Records (BigCommerce, disabled pending DNS resolution)
- HTML scrapers for Juno Records (GBP, artist page approach) and Bandcamp (USD, vinyl title filter); full 7-adapter registry complete
- Clarity Records gap closure blocked by NXDOMAIN — domain clarityrecords.com.au does not resolve; adapter stays disabled pending site recovery
- 545-line hand-rolled CSS design system replaces Tailwind CDN; base.html rewritten with semantic class names, all JS functionality preserved
- Discogs thumb URL capture pipeline: artwork_url column + migration, _cover_image sentinel key, scanner write-back, /api/artwork streaming proxy, and vinyl placeholder SVG
- app/services/fx.py
- index.html:
- Task 1 — CSS Design System (static/style.css)
- Upgraded Discogs artwork capture from search thumbnail to full-res images[0].uri via release endpoint in all three search functions, with first_thumb fallback
- Fixed IntegrityError on scan by changing listings unique constraint from global url to composite (wishlist_item_id, url), and removed artwork_url early-exit guard so every scan overwrites with latest Discogs high-res cover
- P5 — Typography hierarchy:
- Task 1 — Modal accessibility:

---
