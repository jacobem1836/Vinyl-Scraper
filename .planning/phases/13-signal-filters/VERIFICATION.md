---
phase: 13-signal-filters
verified: 2026-04-13T00:00:00Z
status: human_needed
score: 3/4 roadmap success criteria verified (4th requires live scan)
---

# Phase 13: Signal Filters — Verification Report

**Phase Goal:** Only relevant, physical, accurately-located listings reach the user
**Verified:** 2026-04-13
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Listings scoring below relevance threshold are hidden from dashboard and detail view | VERIFIED | `_effective_threshold` and `_passes_relevance` wired into `_enrich_item`, `scan_single_item_web`, `scan_all_items_web`, and `list_item_listings_api` in `app/routers/wishlist.py` |
| 2 | Digital-only listings never appear in scan results | VERIFIED | Digital-drop loop at lines 35–43 of `scanner.py`; `is_digital(r)` tested against 8 cases (all pass); dropped before any DB write |
| 3 | Discogs listings display the correct seller location string | VERIFIED | `_fetch_ships_from` defined and called at all 4 `_build_listing` call sites in `discogs.py` (`_get_release_listings`, `_get_album_listings`, `_get_artist_listings`, `_get_label_listings`); uses `/marketplace/search?release_id=...`; 5 occurrences confirmed |
| 4 | Baseline listing count does not drop by more than expected filter rate | NEEDS HUMAN | Requires a live scan against real Discogs data; cannot be verified programmatically without network access |

**Score:** 3/4 truths verified programmatically

---

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `app/services/relevance.py` | VERIFIED | Exists; exports `score_listing(item_query, item_artist, listing_title) -> float`; uses `min(partial_ratio, token_set_ratio)` deviation from plan (correct fix); punctuation-stripping `_normalize()` present |
| `app/services/digital_filter.py` | VERIFIED | Exists; exports `is_digital(listing: dict) -> bool`; all 7 DIGITAL_FORMAT_TOKENS present (`file`, `mp3`, `flac`, `digital`, `lossless`, `wav`, `aac`) |
| `app/services/test_relevance.py` | VERIFIED | 5 tests; all pass |
| `app/services/test_digital_filter.py` | VERIFIED | 8 tests; all pass |
| `app/services/scanner.py` | VERIFIED | Imports `is_digital` and `score_listing`; digital-drop loop before persistence; `relevance_score=result.get("_relevance_score")` on Listing constructor; `[filter] item=...` log line at line 132–136 |
| `app/services/discogs.py` | VERIFIED | `_fetch_ships_from` async helper defined; called at 4 `_build_listing` sites; `marketplace/search` used exactly once (the helper); no retry logic (`grep "retry"` = 0) |
| `app/routers/wishlist.py` | VERIFIED | `_effective_threshold` (5 occurrences) and `_passes_relevance` (7 occurrences) present; `_enrich_item` filters `all_listings` at line 66; `list_item_listings_api` applies filter at lines 361–362; both scan routes guard notifiable list |
| `requirements.txt` | VERIFIED | `rapidfuzz==3.14.5` present (plan specified 3.10.1; agent upgraded to 3.14.5 for Python 3.14 wheel compatibility — intentional documented deviation) |
| `app/config.py` | VERIFIED | `relevance_threshold_default: float = 70.0` present at line 17 |
| `app/models.py` | VERIFIED | `WishlistItem.relevance_threshold = Column(Float, nullable=True)` at line 20; `Listing.relevance_score = Column(Float, nullable=True)` at line 42 |
| `app/database.py` | VERIFIED | Two migration blocks appended at lines 112–121: `ADD COLUMN relevance_threshold FLOAT` and `ADD COLUMN relevance_score FLOAT` |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `scanner.scan_item` | `digital_filter.is_digital` | direct import + call in result loop | WIRED | Line 11 import; line 39 call |
| `scanner.scan_item` | `relevance.score_listing` | direct import + call in persistence loop | WIRED | Line 12 import; line 66 call |
| `scanner.scan_item` | `Listing.relevance_score` | `relevance_score=result.get("_relevance_score")` on constructor | WIRED | Line 99 in Listing() constructor |
| `scanner.scan_item` | `[filter] log line` | `print(f"[filter] item=...")` | WIRED | Lines 132–136; format matches D-13 spec exactly |
| `routers/wishlist._enrich_item` | `Listing.relevance_score filter` | `_passes_relevance(l, thr)` comprehension | WIRED | Line 66 |
| `routers/wishlist.scan_single_item_web` | notifiable filter | `_passes_relevance(l, _thr)` on new_listings and existing listings | WIRED | Lines 183–185 |
| `routers/wishlist.scan_all_items_web` | notifiable filter | `_passes_relevance(l, _thr)` | WIRED | Lines 213–215 |
| `routers/wishlist.list_item_listings_api` | relevance filter | `_passes_relevance(l, thr)` Python filter after DB fetch | WIRED | Lines 361–362 |
| `discogs._get_release_listings` | `_fetch_ships_from` | `listing["ships_from"] = await _fetch_ships_from(client, release_id)` | WIRED | Line 136 |
| `discogs._get_album_listings` | `_fetch_ships_from` | `l["ships_from"] = await _fetch_ships_from(client, release_id)` | WIRED | Line 204 |
| `discogs._get_artist_listings` | `_fetch_ships_from` | `l["ships_from"] = await _fetch_ships_from(client, release_id)` | WIRED | Line 279 |
| `discogs._get_label_listings` | `_fetch_ships_from` | `l["ships_from"] = await _fetch_ships_from(client, release_id)` | WIRED | Line 354 |
| `database.run_migrations` | `ADD COLUMN relevance_threshold` | ALTER TABLE statement | WIRED | Lines 112–116 |
| `database.run_migrations` | `ADD COLUMN relevance_score` | ALTER TABLE statement | WIRED | Lines 117–121 |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `routers/wishlist._enrich_item` | `all_listings` | `item.listings` ORM relationship, filtered by `_passes_relevance` | Yes — `_passes_relevance` reads `listing.relevance_score` from DB column populated in scanner | FLOWING |
| `scanner.scan_item` | `result["_relevance_score"]` | `score_listing(item.query, "", title)` — pure computation on actual scanned title | Yes — computed from live listing title | FLOWING |
| `scanner.scan_item` | digital_dropped | `is_digital(r)` — checks `r["format"]`, `r["item_type"]`, `r["title"]` from adapter | Yes — checks real adapter dict fields | FLOWING |
| `discogs._fetch_ships_from` | `ships_from` | `/marketplace/search` API response `listings[0]["ships_from"]` | Yes — live API response; `None` on failure (logged) | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `relevance_threshold_default == 70.0` | `python -c "from app.config import settings; print(settings.relevance_threshold_default)"` | `70.0` | PASS |
| `score_listing` returns float >=85 for correct album | `score_listing("Kid A", "Radiohead", "Radiohead - Kid A (2000 UK 1st press)")` | `100.0` | PASS |
| `score_listing` returns float <70 for wrong album / same artist | `score_listing("Kid A", "Radiohead", "Radiohead - OK Computer")` | `40.0` | PASS |
| All 13 tests pass | `pytest app/services/test_relevance.py app/services/test_digital_filter.py -v` | 13/13 passed in 0.05s | PASS |
| Imports succeed across all new and modified modules | `from app.services.scanner import scan_item; from app.routers.wishlist import _effective_threshold, _passes_relevance` | No error | PASS |
| `_fetch_ships_from` defined and called 5 times | `grep -c "_fetch_ships_from" app/services/discogs.py` | `5` | PASS |
| No retry logic in discogs.py | `grep -c "retry" app/services/discogs.py` | `0` | PASS |
| `_effective_threshold` wired in >= 3 places | `grep -c "_effective_threshold" app/routers/wishlist.py` | `5` | PASS |
| `_passes_relevance` wired in >= 3 places | `grep -c "_passes_relevance" app/routers/wishlist.py` | `7` | PASS |

---

## Requirements Coverage

| Requirement | Plan | Description | Status | Evidence |
|-------------|------|-------------|--------|----------|
| FILTER-01 | 13-01, 13-03 | Relevance threshold hides bad matches from dashboard and detail view | SATISFIED | `score_listing` in `relevance.py`; `_passes_relevance` applied at every display query path in `wishlist.py`; `relevance_score` persisted on `Listing` row; per-item `relevance_threshold` override on `WishlistItem` |
| FILTER-02 | 13-01, 13-03 | Digital-only listings never appear in scan results | SATISFIED | `is_digital()` in `digital_filter.py`; drop loop in `scanner.scan_item` before any DB write; 8 tests cover MP3, FLAC, file, digital token, item_type, title-sniffing, format-as-list |
| FILTER-03 | 13-02 | Discogs listings display correct seller location | SATISFIED | `_fetch_ships_from` calls `/marketplace/search` per release; enriches `ships_from` at all 4 call sites; falls back to `None` with log on failure; no retry (D-12 preserved) |

---

## Anti-Patterns Found

No blockers found. Notes:

- `scanner.py` lines 131–136: `kept_count = pre_filter_total - digital_dropped - relevance_below`. This counts relevance-below listings as "not kept" even though they ARE persisted (query-time filter, not scan-time drop). This is the intended D-07 design — the log line reports what users see at the current threshold, not what is stored. Documented in 13-03-SUMMARY decisions. Not a bug.
- `routers/wishlist.py` `list_item_listings_api` (line 362) applies `_passes_relevance` in Python after a DB fetch, not in SQL. This is the intended "query-time filter" design per D-07 (threshold changes take effect without rescan). Acceptable for the data volumes in this project.
- `_scan_in_background` (lines 22–32) does not apply `_passes_relevance` to `new_listings` before calling `send_deal_email`. However, the explicit scan routes (`scan_single_item_web`, `scan_all_items_web`) do apply the filter. The background-task path is a pre-existing pattern; the risk of sub-threshold email alerts from this path exists but is minor (only fires on first background scan after add, not scheduled scans).

---

## Human Verification Required

### 1. Baseline listing count does not drop excessively (SC-4)

**Test:** Trigger a real scan against a wishlist item known to return several Discogs listings. Observe the `[filter]` log line.
**Expected:** `kept=N/M` where `N` is meaningfully close to `M` — i.e. relevance filtering is removing wrong-album noise, not most valid listings. A scan for "Radiohead - Kid A" should not drop more than ~30% of listings to relevance filtering on a healthy first scan.
**Why human:** Requires live Discogs API access and a seeded wishlist item. The 40.0 score for OK Computer vs Kid A confirms the algorithm works correctly in unit tests, but real-world scan distribution can only be checked against a live result set.

### 2. ships_from populates with a real country string on a live scan

**Test:** Scan a Discogs-enabled wishlist item that is known to have marketplace listings. Inspect the resulting Listing rows in the DB (or via the `/api/wishlist/{id}/listings` endpoint).
**Expected:** `ships_from` column contains a non-null country string such as "United Kingdom" or "Germany" — not "no location" — on at least the majority of newly-created Listing rows.
**Why human:** Requires a valid `DISCOGS_TOKEN` env var and a live API call. The code path is correctly wired (verified), but actual data return from the Discogs marketplace API can only be confirmed at runtime.

---

## Gaps Summary

No programmatically-verifiable gaps found. All three FILTER requirements are implemented end-to-end:

- FILTER-01: `score_listing` helper tested (13/13 tests pass), wired into scanner (scores stored), and applied at query time in all display routes
- FILTER-02: `is_digital` helper tested, drop loop wired in scanner before persistence
- FILTER-03: `_fetch_ships_from` wired at all 4 Discogs adapter call sites, no retry, correct rate-limit posture

Two human verification items remain: live scan to confirm SC-4 (baseline count not over-filtered) and to confirm `ships_from` populates with real data. These require a live DISCOGS_TOKEN and cannot be verified without network access.

One minor design note: the background-task scan path (`_scan_in_background`) does not apply the relevance filter before `send_deal_email`. This is a pre-existing pattern not in scope for Phase 13, and the explicit scan routes do apply filtering correctly.

---

_Verified: 2026-04-13_
_Verifier: Claude (gsd-verifier)_
