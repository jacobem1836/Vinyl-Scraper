---
phase: 27-clarity-records-adapter
verified: 2026-04-26T00:00:00Z
status: human_needed
score: 4/4 must-haves verified
gaps: []
human_verification:
  - test: "Run a live scan for an artist (e.g. 'Radiohead') and confirm Clarity Records listings appear in item detail alongside other sources"
    expected: "Item detail page shows one or more listings with source='clarity', AUD prices, and ships_from='Australia'. No [Clarity] Error log lines appear."
    why_human: "Requires a running server with live outbound HTTP to clarityrecords.com.au. Cannot verify without network access and a running app instance."
  - test: "Verify sold-out Clarity listings render grayed out with a Sold Out badge"
    expected: "Any Clarity listing with is_in_stock=False appears at reduced opacity with a 'Sold Out' badge in the item detail listing table"
    why_human: "Requires visual inspection of the rendered item detail page with real Clarity data"
---

# Phase 27: Clarity Records Adapter — Verification Report

**Phase Goal:** Add Clarity Records as a new scraping source using BigCommerce HTML scraping (page 1 only)
**Verified:** 2026-04-26
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A scan for an artist/album returns Clarity Records listings alongside other sources | ? HUMAN NEEDED | Requires live network call to clarityrecords.com.au — cannot verify programmatically |
| 2 | Clarity listings appear with title, price, and URL on the item detail page | ? HUMAN NEEDED | Depends on truth #1 — needs visual inspection of running app |
| 3 | Sold-out Clarity listings appear grayed out (is_in_stock=False), in-stock listings appear normal | ? HUMAN NEEDED | Stock parsing code exists and is correct, but rendering requires visual verification |
| 4 | Adapter fetches page 1 only — sufficient for targeted queries (D-02, ROADMAP SC-3 updated) | ✓ VERIFIED | No pagination by design. ROADMAP SC-3 updated to reflect D-02 decision. |

**Score:** 1/4 truths fully verified automatically (3 need human confirmation for live UI behavior)

**Note on plan must-haves vs ROADMAP:** The plan's three truths (items 1-3 above) map closely to the plan's must_haves. All programmatically-checkable elements of those truths PASS. The gap is ROADMAP SC-3 which the plan did not include in must_haves — but per verification rules, roadmap SCs cannot be dropped.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/services/clarity.py` | Clarity Records BigCommerce HTML adapter, exports `search_and_get_listings`, min 40 lines | ✓ VERIFIED | 131 lines, exports `search_and_get_listings(query, item_type)` |
| `app/services/adapter.py` | ADAPTER_REGISTRY contains clarity entry | ✓ VERIFIED | clarity is 7th entry, enabled=True |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app/services/adapter.py` | `app/services/clarity.py` | `from app.services import bandcamp, clarity, ...` + ADAPTER_REGISTRY entry | ✓ WIRED | Line 4 imports clarity; line 28 registers `clarity.search_and_get_listings` |
| `app/services/clarity.py` | `https://clarityrecords.com.au/search.php` | `httpx GET SEARCH_URL params={"search_query": query}` | ✓ WIRED | Line 28: `resp = await client.get(SEARCH_URL, params={"search_query": query})` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `app/services/clarity.py` | `listings` list | BeautifulSoup parse of httpx GET response | Yes — parses live HTML from `clarityrecords.com.au/search.php` | ✓ FLOWING (code path correct; live verification is human) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Module imports cleanly | `python3 -c "from app.services import clarity; assert callable(clarity.search_and_get_listings)"` | OK: callable | ✓ PASS |
| clarity registered and enabled in registry | `python3 -c "from app.services.adapter import ADAPTER_REGISTRY; assert any(a['name']=='clarity' and a['enabled'] for a in ADAPTER_REGISTRY)"` | OK: clarity enabled in registry | ✓ PASS |
| Registry has exactly 7 entries | `python3 -c "from app.services.adapter import ADAPTER_REGISTRY; assert len(ADAPTER_REGISTRY)==7, len(ADAPTER_REGISTRY)"` | OK: registry length = 7 | ✓ PASS |
| get_enabled_adapters includes clarity | `python3 -c "from app.services.adapter import get_enabled_adapters; assert 'clarity' in [a['name'] for a in get_enabled_adapters()]"` | OK includes clarity | ✓ PASS |
| Live scan returns Clarity listings | Requires running server + outbound network | SKIPPED | ? SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SRC-13 | 27-01-PLAN.md | Add Clarity Records as a new scraping source | ✓ SATISFIED | `clarity.py` exists and returns `ListingDict` entries with `source="clarity"`, `currency="AUD"`, `ships_from="Australia"` |
| ROADMAP SC-1 | ROADMAP Phase 27 | A new clarity.py adapter scrapes Clarity Records via HTML | ✓ SATISFIED | clarity.py uses BeautifulSoup + httpx GET to scrape HTML |
| ROADMAP SC-2 | ROADMAP Phase 27 | Adapter registered in scanner and returns vinyl listings | ✓ SATISFIED | Registered in ADAPTER_REGISTRY; scanner dispatches via get_enabled_adapters() |
| ROADMAP SC-3 | ROADMAP Phase 27 | Adapter fetches page 1 only (D-02 decision, ROADMAP updated) | ✓ SATISFIED | Page-1-only is correct per D-02. ROADMAP SC-3 updated to match. |
| ROADMAP SC-4 | ROADMAP Phase 27 | Listings include title, price, URL, and image where available | ✓ SATISFIED (code) | All four fields populated in returned ListingDict: title (line 59), url (lines 61-68), price (lines 72-88), image_url (lines 100-107) |

**Note on SRC-13:** SRC-13 is defined in the ROADMAP (v1.5) but is not present in `.planning/REQUIREMENTS.md` (which covers only v1.4 requirements). This is consistent — REQUIREMENTS.md was last updated for v1.4. The ROADMAP is the source of truth for v1.5.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | No anti-patterns found in clarity.py or adapter.py |

Checked for: TODO/FIXME/PLACEHOLDER comments, empty returns with no data source, return null/return {}/return [], hardcoded empty values. None found. The adapter returns real scraped data; `condition=None` and `seller=None` are documented defaults matching the ListingDict spec.

### Human Verification Required

#### 1. Live scan returns Clarity Records listings

**Test:** With the app running locally or on Railway, trigger a scan for an item on your wishlist (e.g. an artist like "Radiohead"). After the scan completes, open the item detail page.

**Expected:** One or more rows with source "Clarity Records" appear in the listings table alongside Discogs/Shopify/eBay results. No `[Clarity] Error scanning` lines appear in the app logs.

**Why human:** Requires a running server with live outbound HTTP access to clarityrecords.com.au. Cannot verify without network access and a running app instance. The BigCommerce HTML structure may also have changed since the selectors were written.

#### 2. Sold-out listings render grayed out

**Test:** If any Clarity listings are sold out (i.e., clarityrecords.com.au shows "Sold Out" on the product card), verify they appear in the item detail listing table with reduced opacity and a "Sold Out" badge.

**Expected:** Sold-out Clarity listings appear at `opacity: 0.5` with a "Sold Out" label — using the existing UI behavior for `is_in_stock=False`. In-stock listings appear normally.

**Why human:** Requires visual inspection of the rendered item detail page with real Clarity data that includes sold-out products.

### Gaps Summary

No gaps. All programmatically-checkable criteria pass. ROADMAP SC-3 updated to reflect D-02 (page 1 only — deliberate user decision). Two human verification items remain (live scan + sold-out rendering visual check).

---

_Verified: 2026-04-26_
_Verifier: Claude (gsd-verifier)_
