---
phase: 13-signal-filters
plan: "01"
subsystem: services
tags: [relevance, digital-filter, schema, rapidfuzz]
dependency_graph:
  requires: []
  provides: [app/services/relevance.py, app/services/digital_filter.py, schema:relevance_score, schema:relevance_threshold]
  affects: [app/models.py, app/config.py, app/database.py, requirements.txt]
tech_stack:
  added: [rapidfuzz==3.14.5]
  patterns: [min-scorer-fusion, regex-normalization, layered-field-detection]
key_files:
  created:
    - app/services/relevance.py
    - app/services/test_relevance.py
    - app/services/digital_filter.py
    - app/services/test_digital_filter.py
  modified:
    - requirements.txt
    - app/config.py
    - app/models.py
    - app/database.py
decisions:
  - "rapidfuzz pinned at 3.14.5 (not 3.10.1): no Python 3.14 wheel available for 3.10.1"
  - "score_listing uses min(partial_ratio, token_set_ratio) not plain token_set_ratio: prevents same-artist/wrong-album inflation"
  - "Punctuation stripped in _normalize() via regex to achieve consistent case/punct insensitivity"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-13"
  tasks_completed: 3
  tasks_total: 3
  files_created: 4
  files_modified: 4
---

# Phase 13 Plan 01: Signal Filters Foundation Summary

**One-liner:** Schema columns, config default, rapidfuzz dep, and two pure helper modules (relevance scoring + digital detection) with 13 passing tests — foundation for Plan 03 filter wiring.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add rapidfuzz dep, config default, schema columns | e225727 | requirements.txt, app/config.py, app/models.py, app/database.py |
| 2 | Create relevance.py helper module | dc3c161 | app/services/relevance.py, app/services/test_relevance.py |
| 3 | Create digital_filter.py helper module | aecf4ec | app/services/digital_filter.py, app/services/test_digital_filter.py |

## Verification

- `settings.relevance_threshold_default` returns `70.0`
- `WishlistItem.relevance_threshold` column exists (nullable float)
- `Listing.relevance_score` column exists (nullable float)
- Migration blocks appended to `run_migrations()` for both columns
- `score_listing("Kid A", "Radiohead", "Radiohead - OK Computer")` returns ~40 (< 70 threshold)
- `score_listing("Kid A", "Radiohead", "Radiohead - Kid A (2000 UK 1st press)")` returns 100 (>= 85)
- All 13 tests pass: `pytest app/services/test_relevance.py app/services/test_digital_filter.py -q`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] rapidfuzz version pinned to 3.14.5 instead of 3.10.1**
- **Found during:** Task 1
- **Issue:** `rapidfuzz==3.10.1` has no pre-built wheel for Python 3.14 (the project venv's runtime). pip tried to build from source and failed.
- **Fix:** Pinned to `rapidfuzz==3.14.5`, the current stable release with a Python 3.14 wheel. Same public API; no code changes needed.
- **Files modified:** requirements.txt
- **Commit:** e225727

**2. [Rule 1 - Bug] Changed scorer from token_set_ratio to min(partial_ratio, token_set_ratio)**
- **Found during:** Task 2 (TDD GREEN phase)
- **Issue:** Plain `token_set_ratio("radiohead kid a", "radiohead - ok computer")` returned 75.0 — above the 70.0 threshold. This is exactly the same-artist/wrong-album bug the phase is designed to fix. The plan noted scorer choice was "Claude's Discretion."
- **Fix:** Use `min(partial_ratio(query, title), token_set_ratio(combined, title))`. The minimum of two signals requires both the album title to appear AND the combined string to match — preventing artist-only token overlap from inflating the score.
- **Files modified:** app/services/relevance.py
- **Commit:** dc3c161

**3. [Rule 1 - Bug] Added punctuation stripping to _normalize()**
- **Found during:** Task 2 (TDD GREEN phase, test_case_and_punctuation_insensitive)
- **Issue:** "KID A!" vs "Kid A" produced a 7.14-point difference (exceeding the 5.0 tolerance) because `!` was counted in the ratio. The plan specified case/punctuation insensitivity.
- **Fix:** Added `re.sub(r"[^a-z0-9 ]", " ", s)` in `_normalize()` to strip all non-alphanumeric characters before scoring.
- **Files modified:** app/services/relevance.py
- **Commit:** dc3c161

## Known Stubs

None — all new code is pure computation with no DB or UI integration yet. Plan 03 will wire these helpers into the scanner and router.

## Threat Flags

None — no new network endpoints, auth paths, or trust boundaries introduced. All new code is pure computation on already-trusted data.

## Self-Check: PASSED

- [x] `app/services/relevance.py` exists
- [x] `app/services/digital_filter.py` exists
- [x] `app/services/test_relevance.py` exists
- [x] `app/services/test_digital_filter.py` exists
- [x] Commit e225727 exists
- [x] Commit dc3c161 exists
- [x] Commit aecf4ec exists
- [x] All 13 tests pass
