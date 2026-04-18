---
phase: 02-new-sources
plan: 01
subsystem: api
tags: [ebay, oauth, rate-limiting, adapters, scraping]

# Dependency graph
requires:
  - phase: 01-infrastructure
    provides: adapter registry (ADAPTER_REGISTRY), scanner with semaphore, config pattern
provides:
  - eBay Browse API adapter with OAuth token caching and EBAY_AU marketplace targeting
  - Per-adapter rate limiting (global scan_semaphore removed; each adapter owns its concurrency)
  - Config guard pattern: adapters return [] when credentials are unset
affects: [02-02, 02-03, ui-redesign]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Config guard: if not settings.{service}_key: return [] — all optional-credential adapters use this"
    - "OAuth token caching with asyncio.Lock() prevents race conditions on concurrent token refresh"
    - "Per-adapter asyncio.Semaphore instead of global semaphore — each adapter owns its concurrency policy"

key-files:
  created:
    - app/services/ebay.py
  modified:
    - app/services/adapter.py
    - app/config.py
    - app/routers/wishlist.py
    - app/scheduler.py
  deleted:
    - app/services/rate_limit.py

key-decisions:
  - "Semaphore(5) for eBay Browse API — higher limit than Discogs, Browse API handles concurrent requests well"
  - "Token cached at module level with expiry - 60s buffer to avoid using a token that expires mid-request"
  - "ships_from hardcoded to 'Australia' for EBAY_AU — all listings are Australian sellers"
  - "Global scan_semaphore removed: per-adapter semaphores are the right home for concurrency policy"

patterns-established:
  - "Adapter config guard: check credentials at top of search_and_get_listings, return [] if missing"
  - "OAuth token cache: module-level _token, _token_expiry, _token_lock pattern for thread-safe refresh"

requirements-completed: [SRC-01]

# Metrics
duration: 3min
completed: 2026-04-02
---

# Phase 2 Plan 01: eBay Adapter + Rate Limit Migration Summary

**eBay AU Browse API adapter with OAuth token caching and FIXED_PRICE filter; global scan_semaphore replaced by per-adapter Semaphore(5) in ebay.py**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-02T05:58:50Z
- **Completed:** 2026-04-02T06:00:52Z
- **Tasks:** 2
- **Files modified:** 5 (plus 1 deleted, 1 created)

## Accomplishments
- eBay Browse API adapter targeting EBAY_AU marketplace with FIXED_PRICE filter, AUD pricing, and config guard
- OAuth 2.0 client credentials flow with module-level token caching and asyncio.Lock() for safe concurrent refresh
- Global scan_semaphore removed from wishlist.py, scheduler.py, and rate_limit.py deleted; each adapter now owns its concurrency policy

## Task Commits

Each task was committed atomically:

1. **Task 1: Rate limit migration and eBay config** - `2351449` (feat)
2. **Task 2: eBay Browse API adapter with OAuth and registry entry** - `a0bda59` (feat)

**Plan metadata:** (forthcoming)

## Files Created/Modified
- `app/services/ebay.py` - eBay Browse API adapter: OAuth token caching, EBAY_AU marketplace, FIXED_PRICE filter, Semaphore(5), config guard
- `app/services/adapter.py` - Added ebay import and registry entry
- `app/config.py` - Added ebay_app_id and ebay_cert_id Optional[str] = None fields
- `app/routers/wishlist.py` - Removed scan_semaphore import and async with wrappers
- `app/scheduler.py` - Removed scan_semaphore import and async with wrapper from _scan_one
- `app/services/rate_limit.py` - DELETED (no longer referenced anywhere)

## Decisions Made
- Semaphore(5) for eBay: Browse API is higher throughput than Discogs; 5 concurrent requests is safe
- Token expiry buffer of 60 seconds prevents edge case where token expires between fetch and use
- `ships_from = "Australia"` hardcoded for EBAY_AU — all results are AU-based sellers, simplifies shipping cost calc
- Removed global semaphore entirely rather than keeping it: per-adapter control is strictly better for future adapters

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed indentation error in scheduler.py after semaphore removal**
- **Found during:** Task 1 (Rate limit migration)
- **Issue:** Removing `async with scan_semaphore:` left the `if item.notify_email` block with one extra indent level, causing `IndentationError`
- **Fix:** Reduced indentation of the notify block back to correct level inside `_scan_one`
- **Files modified:** app/scheduler.py
- **Verification:** `from app.scheduler import setup_scheduler` succeeded without error
- **Committed in:** 2351449 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Required fix — indent error would have prevented app startup.

## Issues Encountered
- grep returning exit code 1 for "zero matches found" caused false verification failure; used negated grep (`! grep -q`) as the correct check.

## User Setup Required

**External services require manual configuration before eBay scans will return results.**

To enable eBay scanning, add the following to your `.env` file:

```
EBAY_APP_ID=your-ebay-app-id
EBAY_CERT_ID=your-ebay-cert-id
```

**How to get credentials:**
1. Go to https://developer.ebay.com/my/keys
2. Apply for the eBay Developer Program (if not already enrolled)
3. Create a production keyset
4. Copy the App ID (Client ID) and Cert ID (Client Secret)

**Verification:** Without credentials, `search_and_get_listings` returns `[]` immediately. With credentials, eBay listings will appear in scan results alongside Discogs and Shopify results.

## Next Phase Readiness
- Adapter registry contains: discogs, shopify, ebay
- Per-adapter concurrency pattern established — 02-02 (Juno/Bandcamp) can follow same pattern
- eBay adapter is live but gated by credentials; no user setup needed to keep app functional

---
*Phase: 02-new-sources*
*Completed: 2026-04-02*

## Self-Check: PASSED

- FOUND: app/services/ebay.py
- FOUND: app/services/adapter.py
- FOUND: app/config.py
- CONFIRMED DELETED: app/services/rate_limit.py
- FOUND: .planning/phases/02-new-sources/02-01-SUMMARY.md
- FOUND: commit 2351449
- FOUND: commit a0bda59
