---
phase: 25-ebay-credentials
plan: "01"
subsystem: config
tags: [ebay, credentials, config, startup]
dependency_graph:
  requires: []
  provides: [ebay-credentials-documented, startup-warning]
  affects: [app/main.py, .env.example]
tech_stack:
  added: []
  patterns: [startup-warning, env-documentation]
key_files:
  created: []
  modified:
    - .env.example
    - app/main.py
decisions:
  - "EBAY_DEV_ID documented in .env.example only — not added to config.py or ebay.py (D-04)"
  - "Startup warning placed immediately before asyncio.create_task to avoid blocking startup flow"
metrics:
  duration: "<5 min"
  completed_date: "2026-04-25"
  tasks_completed: 1
  tasks_total: 2
  files_changed: 2
---

# Phase 25 Plan 01: eBay Credentials Documentation and Startup Warning Summary

**One-liner:** eBay credential docs added to .env.example with startup warning gating adapter visibility when creds are absent.

## Status

Task 1 complete (committed `354f342`). Task 2 is a human-verify checkpoint — pending live scan verification.

## Tasks Completed

| # | Name | Commit | Files |
|---|------|--------|-------|
| 1 | Document eBay credentials in .env.example and add startup warning | 354f342 | `.env.example`, `app/main.py` |

## Tasks Pending

| # | Name | Status |
|---|------|--------|
| 2 | Verify live scan returns eBay AU listings | Awaiting human verification (checkpoint) |

## What Was Built

**Task 1:**
- `.env.example` now documents all three eBay keys (`EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_DEV_ID`) with descriptions and a reference to `developer.ebay.com` for obtaining credentials
- `app/main.py` `startup()` now prints `[startup] WARNING: eBay credentials missing ...` when either `settings.ebay_app_id` or `settings.ebay_cert_id` is absent — mirrors the same boolean guard already in `app/services/ebay.py`
- No other files modified; `app/config.py` and `app/services/ebay.py` are unchanged

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check

- [x] `.env.example` contains `EBAY_APP_ID=`, `EBAY_CERT_ID=`, `EBAY_DEV_ID=` and `developer.ebay.com`
- [x] `app/main.py` contains `if not settings.ebay_app_id or not settings.ebay_cert_id` and `[startup].*eBay.*missing`
- [x] `app/config.py` untouched (no `ebay_dev_id` field)
- [x] `app/services/ebay.py` untouched
- [x] Commit `354f342` exists
- [x] `from app.main import app` exits 0 with venv active

## Self-Check: PASSED
