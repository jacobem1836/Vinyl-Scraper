---
phase: 02-new-sources
plan: "02"
subsystem: scraping
tags: [beautifulsoup4, lxml, html-scraping, neto, bigcommerce, au-stores]

requires:
  - phase: 02-01
    provides: eBay AU adapter and adapter registry pattern established

provides:
  - Discrepancy Records HTML scraper adapter (Neto platform, AUD pricing)
  - Clarity Records HTML scraper adapter (BigCommerce platform, AUD pricing, disabled pending site confirmation)
  - beautifulsoup4 and lxml dependencies declared in requirements.txt

affects: [02-03, scanner, adapter-registry]

tech-stack:
  added: [beautifulsoup4==4.12.3, lxml==5.3.0]
  patterns: [HTML scraper adapter with Semaphore(1)+sleep rate limiting, BeautifulSoup lxml parser, returns [] on any error]

key-files:
  created:
    - app/services/discrepancy.py
    - app/services/clarity.py
  modified:
    - requirements.txt
    - app/services/adapter.py

key-decisions:
  - "Discrepancy search URL is /?kw={query} not /search?q={query} -- live HTML inspection revealed the correct Neto param"
  - "Discrepancy prices in p.funky inside .pei-bottom; some products render without price (null is valid)"
  - "Clarity Records set enabled=False in registry -- site unreachable (DNS failure) during implementation; BigCommerce standard selectors in place as best-effort"

patterns-established:
  - "AU store adapter: Semaphore(1) + asyncio.sleep(1.5) for rate limiting small independent stores"
  - "Zero-result warning logged when HTTP 200 but no products parsed, to catch selector drift"
  - "Absolute URL normalization: prepend BASE_URL if href starts with /"

requirements-completed: [SRC-02, SRC-03]

duration: 2min
completed: "2026-04-02"
---

# Phase 02 Plan 02: AU Stores (Discrepancy + Clarity) Summary

**HTML scrapers for two Australian vinyl stores using BeautifulSoup: Discrepancy Records (Neto, live and working) and Clarity Records (BigCommerce, disabled pending DNS resolution)**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-02T06:06:39Z
- **Completed:** 2026-04-02T06:09:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Discrepancy Records adapter scrapes live Neto storefront; returns AUD-priced listings with correct URL/title extraction from `.thumbnail` containers
- Clarity Records adapter implemented with BigCommerce standard selectors; set `enabled: False` because site was unreachable at DNS level during implementation
- beautifulsoup4 and lxml added to requirements.txt so Railway can install them for all HTML scrapers
- Both adapters registered in ADAPTER_REGISTRY; discrepancy enabled, clarity disabled with comment

## Task Commits

1. **Task 1: Discrepancy Records adapter** - `e6e652e` (feat)
2. **Task 2: Clarity Records adapter + registry wiring** - `0de10e2` (feat)

## Files Created/Modified

- `app/services/discrepancy.py` - Neto HTML scraper: /?kw= search, .thumbnail containers, p.funky prices
- `app/services/clarity.py` - BigCommerce HTML scraper: standard card/price selectors (disabled)
- `requirements.txt` - Added beautifulsoup4==4.12.3 and lxml==5.3.0
- `app/services/adapter.py` - Added discrepancy and clarity to ADAPTER_REGISTRY

## Decisions Made

- Discrepancy search URL discovered via live HTML inspection: `/?kw={query}` not `/search?q={query}` — the research notes had the wrong URL pattern
- Discrepancy prices are in `p.funky` inside `.pei-bottom` inside `.product-extra-info`; only ~14 of 32 search results had prices, rest have `price: None` (valid — products without prices are still listed)
- Clarity Records had DNS failure (`nodename nor servname provided`) — implemented with BigCommerce standard selectors as best-effort, set `enabled: False` per plan instructions; re-enable and verify selectors once site is reachable

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected Discrepancy search URL from research notes**
- **Found during:** Task 1 (live HTML inspection step)
- **Issue:** Research notes suggested `SEARCH_URL = "https://www.discrepancy-records.com.au/search"` with `?q=` param — this returns an empty page (JS-rendered). Real search uses `/?kw={query}` at root.
- **Fix:** Used `SEARCH_URL = "https://www.discrepancy-records.com.au/"` with `params={"kw": query}` as discovered by live inspection
- **Files modified:** app/services/discrepancy.py
- **Verification:** `asyncio.run(search_and_get_listings('radiohead', 'album'))` returned 10 results
- **Committed in:** e6e652e (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — incorrect URL from research)
**Impact on plan:** Essential fix for correctness; without it the adapter would always return 0 results.

## Issues Encountered

- Clarity Records unreachable at DNS level during implementation — handled per plan instructions (BigCommerce standard selectors, enabled=False)

## Known Stubs

- `clarity.py` — Selectors are BigCommerce standard patterns, unverified against live site. The adapter returns [] currently (DNS failure). Enable and test once clarityrecords.com.au is accessible.

## User Setup Required

None — no external service configuration required. To enable Clarity Records once the site is confirmed reachable:
1. Verify selectors by fetching `https://www.clarityrecords.com.au/search.php?q=radiohead`
2. Update selectors in `app/services/clarity.py` if needed
3. Change `"enabled": False` to `"enabled": True` in `app/services/adapter.py`

## Next Phase Readiness

- Phase 02-03 (Juno Records + Bandcamp) can proceed — adapter registry pattern established, beautifulsoup4/lxml available
- Discrepancy adapter live and producing results

---
*Phase: 02-new-sources*
*Completed: 2026-04-02*
