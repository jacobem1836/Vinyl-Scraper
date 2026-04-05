# Milestones

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
