---
phase: 02-new-sources
verified: 2026-04-03T00:00:00Z
status: gaps_found
score: 13/14 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 12/14
  gaps_closed:
    - "SRC-06 formally claimed by 02-04-PLAN.md (requirements: [SRC-03, SRC-06]) — orphan resolved"
  gaps_remaining:
    - "Clarity Records (SRC-03) — site clarityrecords.com.au confirmed NXDOMAIN on second check; adapter remains enabled=False; selectors unverified against live site"
  regressions: []
gaps:
  - truth: "Clarity Records adapter returns AUD-priced listing dicts for vinyl search queries"
    status: failed
    reason: "clarityrecords.com.au confirmed NXDOMAIN on both original implementation (02-02) and gap-closure attempt (02-04). Domain does not resolve. Adapter is structurally correct but registered as enabled=False and produces 0 results for all queries. The gap closure plan was executed and explicitly stopped per its own instructions when DNS failure was confirmed. No selector verification was possible."
    artifacts:
      - path: "app/services/clarity.py"
        issue: "Docstring still reads 'Site was unreachable during implementation' — selectors are BigCommerce standard patterns, unverified against live HTML. Registered enabled=False."
      - path: "app/services/adapter.py"
        issue: "Line 26: clarity entry has enabled=False; excluded from all scans"
    missing:
      - "clarityrecords.com.au must resolve via DNS before this adapter can be enabled"
      - "Once site is reachable: verify BigCommerce selectors match live HTML, then set enabled=True"
      - "Consider replacing with an alternative AU record store (e.g. Egg Records, Record Paradise) if site remains offline"
human_verification:
  - test: "Clarity Records site reachability (periodic check)"
    expected: "https://www.clarityrecords.com.au/search.php?q=radiohead returns HTTP 200 with BigCommerce product HTML"
    why_human: "Domain confirmed NXDOMAIN on two separate checks (2026-04-02). Cannot verify programmatically. Site may have moved or closed permanently."
  - test: "Discrepancy Records live scrape"
    expected: "search_and_get_listings('radiohead', 'album') returns at least 1 dict with source=discrepancy, currency=AUD, ships_from=Australia"
    why_human: "Depends on live site availability and selector stability. Verified at implementation time but external site may change."
  - test: "eBay live OAuth flow with real credentials"
    expected: "With EBAY_APP_ID and EBAY_CERT_ID set, search_and_get_listings returns AUD-priced buy-it-now listings from EBAY_AU marketplace"
    why_human: "Requires real eBay developer credentials. Config guard verified (returns [] without creds). Live OAuth flow cannot be tested without credentials."
---

# Phase 2: New Sources Verification Report

**Phase Goal:** Add eBay AU, Discrepancy Records, Clarity Records, Juno Records, and Bandcamp as adapter-pattern scrapers integrated with the existing scan pipeline.
**Verified:** 2026-04-03T00:00:00Z
**Status:** gaps_found (1 gap — Clarity Records site confirmed NXDOMAIN, not actionable without external site recovery)
**Re-verification:** Yes — after gap closure attempt (02-04)

---

## Re-verification Summary

| Previous Gap | Result |
|---|---|
| Clarity Records (SRC-03) — adapter enabled=False, site NXDOMAIN | REMAINS OPEN — 02-04 confirmed NXDOMAIN on second check; no changes made |
| Juno Records (SRC-04) — artist-page approach, partial coverage | ACCEPTED — documented known limitation, not re-opened |
| SRC-06 — orphaned requirement not claimed by any plan | CLOSED — 02-04-PLAN.md formally claims SRC-06 in requirements: field |

**Score improvement:** 12/14 → 13/14 (SRC-06 closure; Clarity gap unchanged)

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | eBay adapter returns standard listing dicts with AUD prices for buy-it-now vinyl queries | VERIFIED | `ebay.py` has `buyingOptions:{FIXED_PRICE}` filter, `EBAY_AU` marketplace header, `currency=AUD`, OAuth token caching |
| 2 | eBay adapter returns [] immediately when EBAY_APP_ID or EBAY_CERT_ID are unset | VERIFIED | `if not settings.ebay_app_id or not settings.ebay_cert_id: return []` at line 47; behavioral test confirmed |
| 3 | eBay scans do not fail or slow down when multiple wishlist items query eBay in same scan cycle | VERIFIED | `_semaphore = asyncio.Semaphore(5)` and `_token_lock = asyncio.Lock()` provide concurrent-safe token caching |
| 4 | Per-adapter rate limiting replaces the global scan_semaphore | VERIFIED | `rate_limit.py` deleted; zero occurrences of `scan_semaphore` or `rate_limit` in `wishlist.py` or `scheduler.py` |
| 5 | Existing scan routes and scheduler still work after rate_limit.py removal | VERIFIED | `from app.routers.wishlist import web_router` and `from app.scheduler import setup_scheduler` both import cleanly |
| 6 | Discrepancy Records adapter returns AUD-priced listing dicts for vinyl search queries | VERIFIED | `discrepancy.py` scrapes Neto platform, Semaphore(1)+sleep(1.5), source=discrepancy, currency=AUD, ships_from=Australia |
| 7 | Clarity Records adapter returns AUD-priced listing dicts for vinyl search queries | FAILED | `clarityrecords.com.au` confirmed NXDOMAIN on both implementation (02-02) and gap-closure check (02-04). Adapter code is structurally correct but `enabled=False` and produces 0 results. |
| 8 | Both AU adapters use Semaphore(1) + sleep to avoid hammering small AU stores | VERIFIED | Both `discrepancy.py` and `clarity.py` have `_semaphore = asyncio.Semaphore(1)` and `await asyncio.sleep(1.5)` |
| 9 | Both AU adapters return [] on any error (logged with [Source] prefix) | VERIFIED | Both have `except Exception as e: print(f"[Source] Error..."); return []` |
| 10 | beautifulsoup4 and lxml are declared in requirements.txt | VERIFIED | `requirements.txt`: `beautifulsoup4==4.12.3`, `lxml==5.3.0` |
| 11 | Juno Records adapter returns GBP-priced listing dicts for vinyl search queries | PARTIAL (accepted) | Adapter works and returns GBP dicts. Uses artist browse pages (`/artists/{query}/`) instead of search endpoint (JS-rendered, returns no static results). Only matches exact Juno artist slugs. Documented known limitation in SUMMARY. |
| 12 | Juno adapter sets a browser-like User-Agent header to avoid 403 blocks | VERIFIED | `_HEADERS` has full Mozilla/5.0 Chrome UA string; 403 detection at lines 37-39 |
| 13 | Bandcamp adapter returns listing dicts only for physical vinyl | VERIFIED | `if "vinyl" not in combined_text: continue` at line 68 of `bandcamp.py`; checks title + itemtype + subhead combined text |
| 14 | Bandcamp adapter returns [] when no physical vinyl matches exist | VERIFIED | Filter exhausts with empty `listings` list; explicit `return []` |

**Score: 13/14 truths verified** (1 failed — Clarity site NXDOMAIN, not fixable by code changes; Juno partial accepted as documented known limitation)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/services/ebay.py` | eBay Browse API adapter | VERIFIED | Exists, 93 lines, substantive implementation, registered enabled=True |
| `app/config.py` | eBay credential settings | VERIFIED | `ebay_app_id: Optional[str] = None` and `ebay_cert_id: Optional[str] = None` at lines 8-9 |
| `app/services/adapter.py` | All 7 adapters registered | VERIFIED | All 7 registered; ebay/discrepancy/juno/bandcamp enabled=True; clarity enabled=False |
| `requirements.txt` | beautifulsoup4 and lxml deps | VERIFIED | Both present: `beautifulsoup4==4.12.3`, `lxml==5.3.0` |
| `app/services/discrepancy.py` | Discrepancy Records HTML scraper | VERIFIED | Exists, 101 lines, live-verified selectors, wired in adapter.py |
| `app/services/clarity.py` | Clarity Records HTML scraper | STUB (external) | Exists, 116 lines, correct structure, but registered disabled; selectors unverified; site NXDOMAIN |
| `app/services/juno.py` | Juno Records HTML scraper | VERIFIED | Exists, 110 lines, artist-page approach, wired enabled=True |
| `app/services/bandcamp.py` | Bandcamp physical vinyl scraper | VERIFIED | Exists, 114 lines, vinyl filter, wired enabled=True |
| `app/services/rate_limit.py` | DELETED | VERIFIED | File does not exist; no references in wishlist.py or scheduler.py |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app/services/adapter.py` | `app/services/ebay.py` | `ebay.search_and_get_listings` | WIRED | Line 24: `{"name": "ebay", "fn": ebay.search_and_get_listings, "enabled": True}` |
| `app/services/ebay.py` | `app/config.py` | `settings.ebay_app_id`, `settings.ebay_cert_id` | WIRED | Lines 7, 47; `from app.config import settings` |
| `app/services/adapter.py` | `app/services/discrepancy.py` | `discrepancy.search_and_get_listings` | WIRED | Line 25: enabled=True |
| `app/services/adapter.py` | `app/services/clarity.py` | `clarity.search_and_get_listings` | WIRED (disabled) | Line 26: registered but `enabled=False` — excluded from all scans |
| `app/services/adapter.py` | `app/services/juno.py` | `juno.search_and_get_listings` | WIRED | Line 27: enabled=True |
| `app/services/adapter.py` | `app/services/bandcamp.py` | `bandcamp.search_and_get_listings` | WIRED | Line 28: enabled=True |
| `app/services/scanner.py` | `app/services/adapter.py` | `get_enabled_adapters()` | WIRED | Line 8: `from app.services.adapter import get_enabled_adapters`; used at line 16 |

---

### Data-Flow Trace (Level 4)

Adapters are service functions, not UI components. Data flows: adapter output → scanner → database → routes → dashboard. Scanner wiring is confirmed above.

| Adapter | Returns | Source | Produces Real Data | Status |
|---------|---------|--------|--------------------|--------|
| `ebay.py` | `list[dict]` AUD prices | eBay Browse API via OAuth | Real API (gated by credentials) | VERIFIED (gated) |
| `discrepancy.py` | `list[dict]` AUD prices | Live HTTP scrape discrepancy-records.com.au | Live scrape verified at implementation time | VERIFIED |
| `clarity.py` | `list[dict]` AUD prices | Live HTTP scrape clarityrecords.com.au | Site NXDOMAIN — returns [] always | HOLLOW (site down) |
| `juno.py` | `list[dict]` GBP prices | Live HTTP scrape juno.co.uk artist pages | Live scrape, limited to artist-slug queries | VERIFIED (limited) |
| `bandcamp.py` | `list[dict]` USD prices | Live HTTP scrape bandcamp.com | Live scrape with vinyl text filter | VERIFIED |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| eBay config guard returns [] | `asyncio.run(search_and_get_listings('test', 'album'))` with no env vars | `[]` | PASS |
| Registry contains all 7 adapters | `[a['name'] for a in ADAPTER_REGISTRY]` | `['discogs', 'shopify', 'ebay', 'discrepancy', 'clarity', 'juno', 'bandcamp']` | PASS |
| Enabled adapters are 6 (clarity excluded) | `get_enabled_adapters()` | `['discogs', 'shopify', 'ebay', 'discrepancy', 'juno', 'bandcamp']` | PASS |
| All adapter imports succeed | `from app.services.{x} import search_and_get_listings` for all 5 new adapters | All succeed without ImportError | PASS |
| App imports still work | `from app.routers.wishlist import web_router; from app.scheduler import setup_scheduler` | Both succeed | PASS |
| rate_limit.py deleted | `test -f app/services/rate_limit.py` | File does not exist | PASS |
| scan_semaphore absent from wishlist.py and scheduler.py | `grep -c "scan_semaphore" wishlist.py scheduler.py` | Both return 0 | PASS |
| eBay config fields present | `hasattr(settings, 'ebay_app_id')` and `hasattr(settings, 'ebay_cert_id')` | Both True | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SRC-01 | 02-01-PLAN.md | eBay AU adapter, Browse API, buy-it-now, EBAY_AU marketplace | SATISFIED | `ebay.py`: FIXED_PRICE filter, EBAY_AU header, AUD currency, OAuth via Browse API |
| SRC-02 | 02-02-PLAN.md | Discrepancy Records adapter, Neto platform, AUD prices | SATISFIED | `discrepancy.py`: scrapes live Neto site, AUD dicts, ships_from=Australia |
| SRC-03 | 02-02-PLAN.md, 02-04-PLAN.md | Clarity Records adapter, BigCommerce platform, AUD prices | BLOCKED | `clarity.py` exists and is structurally correct; site clarityrecords.com.au confirmed NXDOMAIN. Adapter `enabled=False`. REQUIREMENTS.md marks this complete but the implementation gap persists. |
| SRC-04 | 02-03-PLAN.md | Juno Records adapter, HTML scraping with correct User-Agent | SATISFIED (deviation) | `juno.py`: browser User-Agent, GBP dicts, artist-page approach (documented deviation). Requirement says "HTML search results" — adapter uses HTML artist browse pages instead of JS-rendered search page. |
| SRC-05 | 02-03-PLAN.md | Bandcamp adapter, physical vinyl only, not digital | SATISFIED | `bandcamp.py`: searches albums (item_type=a), filters results by "vinyl" in combined text |
| SRC-06 | 02-04-PLAN.md | All sources in central adapter registry; adding requires only registry entry | SATISFIED | `adapter.py` is the central registry; `scanner.py` calls `get_enabled_adapters()`. 02-04-PLAN.md formally claims this requirement. |

**REQUIREMENTS.md discrepancy:** The REQUIREMENTS.md traceability table marks SRC-03 as "Complete" but the Clarity adapter is still disabled due to NXDOMAIN. This is a documentation inconsistency — the file was updated optimistically before the gap closure attempt confirmed the site remains unreachable.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `app/services/clarity.py` | 24-26 | Docstring says "Site was unreachable during implementation — selectors may need adjustment"; `enabled=False` in registry | Warning | Adapter is a dead code path until clarityrecords.com.au resolves. No impact on other adapters. |
| `app/services/juno.py` | 13-14 | Juno search endpoint JS-rendered; falls back to `/artists/{query}/` page — only matches exact artist slugs | Info | Album-name queries or partial names return 404 silently. Documented in SUMMARY as known limitation. |

---

### Human Verification Required

#### 1. Clarity Records Site Reachability (blocked)

**Test:** Check `https://www.clarityrecords.com.au` reachability — DNS lookup or browser check
**Expected:** Domain resolves and returns HTTP 200 with product HTML
**Why human:** Domain confirmed NXDOMAIN on two separate automated checks (2026-04-02). Site may have closed permanently or migrated. Once reachable: verify BigCommerce selectors in `clarity.py`, then set `enabled=True` in `adapter.py`.

#### 2. Discrepancy Records Live Scrape

**Test:** `source venv/bin/activate && python3 -c "import asyncio; from app.services.discrepancy import search_and_get_listings; r = asyncio.run(search_and_get_listings('radiohead', 'album')); print(len(r), r[:1])"`
**Expected:** At least 1 result with source=discrepancy, currency=AUD, ships_from=Australia
**Why human:** Depends on live site availability and HTML selector stability. Verified at implementation time but external HTML may change.

#### 3. eBay Live OAuth Flow

**Test:** Add `EBAY_APP_ID` and `EBAY_CERT_ID` to `.env`, then run `asyncio.run(search_and_get_listings('radiohead', 'album'))`
**Expected:** Returns AUD-priced buy-it-now listings from EBAY_AU marketplace
**Why human:** Requires real eBay developer credentials. Config guard verified; live OAuth flow cannot be tested without credentials.

---

### Gaps Summary

**One active gap (external, not fixable by code):**

**Clarity Records (SRC-03):** The adapter implementation is structurally complete and correct. The gap is entirely external — `clarityrecords.com.au` was NXDOMAIN during both the original implementation (02-02) and the gap closure attempt (02-04). The domain may have expired or the store may have closed. The adapter correctly stays `enabled=False` per its own implementation plan instructions. Resolution requires either the site coming back online, or replacing Clarity with a different AU record store in the registry.

**SRC-06 now closed:** Previously orphaned (not claimed by any plan). Now formally claimed by 02-04-PLAN.md.

**Juno accepted limitation:** Artist-page approach limits search to exact artist slug matches. Documented in SUMMARY. Not re-opened.

**5 of 6 new adapters are active:** discogs (existing), shopify (existing), ebay, discrepancy, juno, bandcamp — all enabled and wired. Clarity is the only disabled adapter.

---

_Verified: 2026-04-03T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
_Re-verification after: 02-04 gap closure attempt_
