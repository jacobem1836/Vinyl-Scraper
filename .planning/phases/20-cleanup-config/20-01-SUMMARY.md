---
plan: 20-01
phase: 20
subsystem: services
tags: [cleanup, dead-code, ebay, adapter-registry]
dependency_graph:
  requires: []
  provides: [clean-adapter-registry, ebay-credential-warning]
  affects: [app/services/adapter.py, app/services/ebay.py]
tech_stack:
  added: []
  patterns: [print-based prefixed logging]
key_files:
  created: []
  modified:
    - app/services/adapter.py
  deleted:
    - app/services/clarity.py
decisions:
  - Clarity Records permanently removed (not disabled) — NXDOMAIN site, no path back in v1.4
  - eBay credential warning uses print consistent with codebase logging convention
metrics:
  duration_minutes: 5
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
  files_deleted: 1
  completed_date: "2026-04-18"
requirements_satisfied: [CLEAN-01, CFG-01]
---

# Phase 20 Plan 01: Remove dead Clarity adapter and harden eBay config Summary

**One-liner:** Deleted clarity.py, scrubbed its registry entry from adapter.py, and added an operator-visible warning when eBay credentials are absent.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 20-01-T1 | Remove Clarity adapter and registry entry | 8a4d117 | app/services/clarity.py (deleted), app/services/adapter.py |
| 20-01-T2 | Add diagnostic logging for missing eBay credentials | ad905bf | app/services/ebay.py |

## What Was Done

### Task 1: Remove Clarity adapter and registry entry

Deleted `app/services/clarity.py` entirely — the BigCommerce scraper for clarityrecords.com.au which has been NXDOMAIN since implementation. Removed the `clarity` import from `adapter.py` and its disabled registry entry. The adapter registry now has exactly 6 entries: discogs, shopify, ebay, discrepancy, juno, bandcamp.

### Task 2: Add diagnostic logging for missing eBay credentials

Added a `print("[eBay] Skipping — credentials not configured (set EBAY_APP_ID and EBAY_CERT_ID env vars)")` before the early return in `search_and_get_listings`. Operators can now see in Railway logs why eBay returns no results when env vars are not set. No functional change — still returns `[]`.

## Verification Results

All plan checks passed:
- `clarity.py` does not exist
- No `clarity` references anywhere in `app/`
- Registry has 6 adapters, no clarity entry
- eBay diagnostic log line present (1 match)
- App imports successfully (verified with venv)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None. The eBay log message only names env var keys (EBAY_APP_ID, EBAY_CERT_ID), never their values. No secrets exposed, consistent with T-20-01 threat register acceptance.

## Self-Check: PASSED

- app/services/adapter.py: exists and modified (clarity removed)
- app/services/clarity.py: confirmed deleted
- app/services/ebay.py: exists and modified (warning added)
- Commits 8a4d117 and ad905bf: present in git log
