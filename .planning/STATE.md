# Project State

## Current Phase
Phase 1: Infrastructure — In progress (Plan 2 of 3)

## Project Reference
See: .planning/PROJECT.md
**Core value:** Show me the cheapest way to buy the records I want, right now.
**Milestone:** v1 — Fast, Beautiful, More Sources

## Roadmap Summary

| Phase | Goal | Requirements |
|-------|------|--------------|
| 1. Infrastructure | Fast, source-agnostic foundation | PERF-01, PERF-02, PERF-03, PERF-04, SRC-06 |
| 2. New Sources | eBay AU, Discrepancy, Clarity, Juno, Bandcamp | SRC-01, SRC-02, SRC-03, SRC-04, SRC-05 |
| 3. UI Redesign | Spotify-like card layout, dark palette, artwork hero | UI-01, UI-02, UI-03, UI-04, UI-05, UI-06 |

## Progress

```
Phase 1 [###       ] 33%
Phase 2 [          ] 0%
Phase 3 [          ] 0%
```

## Accumulated Context

### Decisions
- Semaphore(3): Discogs 60/min cap; 3 concurrent items with ~2 sources = ~6 req/min peak, well under limit
- TTLCache maxsize=1: single dashboard endpoint, 5-minute TTL; key='dashboard'
- API POST /api/wishlist now returns immediately with item (no listings yet); iOS Shortcut contract preserved
- Cache invalidated eagerly on every mutation (edit, delete, scan completion)

### Todos
- None yet

### Blockers
- None yet

## Last Updated
2026-04-02 — Completed 01-01 (Backend Performance: scan decoupling, N+1 fix, cache, semaphore)
