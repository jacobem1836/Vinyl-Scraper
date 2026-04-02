---
phase: "01"
plan: "02"
subsystem: "services/adapter"
tags: [adapter-registry, scanner, source-agnostic, extensibility]
dependency_graph:
  requires: ["01-01"]
  provides: ["adapter-registry", "source-agnostic-scanner"]
  affects: ["app/services/scanner.py", "app/services/adapter.py"]
tech_stack:
  added: ["TypedDict (ListingDict)", "AdapterFn Callable type alias"]
  patterns: ["registry pattern", "return_exceptions error isolation"]
key_files:
  created: ["app/services/adapter.py"]
  modified: ["app/services/scanner.py"]
decisions:
  - "enabled flag per adapter entry supports future per-source toggling without overengineering"
  - "return_exceptions=True in gather isolates per-adapter failures so other sources still return results"
metrics:
  duration_seconds: 70
  completed: "2026-04-02T04:39:04Z"
  tasks_completed: 3
  files_changed: 2
---

# Phase 1 Plan 2: Adapter Registry — Source-Agnostic Scanner Summary

**One-liner:** Central adapter registry with enabled flag and TypedDict type; scanner now iterates registry instead of hard-coding discogs and shopify.

## What Was Built

- `app/services/adapter.py`: New module defining `ListingDict` TypedDict, `AdapterFn` type alias, `ADAPTER_REGISTRY` list with discogs and shopify entries, and `get_enabled_adapters()` helper.
- `app/services/scanner.py`: Removed direct `discogs` and `shopify` imports; replaced hard-coded `asyncio.gather()` call with a dynamic loop over `get_enabled_adapters()`, with per-adapter exception handling via `return_exceptions=True`.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Create adapter registry with ListingDict type | 2ef5852 | app/services/adapter.py (created) |
| 2 | Refactor scanner.py to use registry | 3b53377 | app/services/scanner.py (modified) |
| 3 | Verify end-to-end registry behavior | (no file changes) | — |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- app/services/adapter.py: FOUND
- app/services/scanner.py: FOUND (direct discogs/shopify imports removed)
- Commit 2ef5852: verified
- Commit 3b53377: verified
- Import verification: PASSED
- Registry behavior tests: PASSED (disable adapter, exception isolation, restoration)
