---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Executing Phase 02
last_updated: "2026-04-02T23:28:13.498Z"
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 7
  completed_plans: 7
---

# Project State

## Current Phase

Phase 2: New Sources — Complete (3 of 3 plans done)

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
Phase 1 [##########] 100%
Phase 2 [##########] 100%
Phase 3 [          ] 0%
```

## Accumulated Context

### Decisions

- Semaphore(3): Discogs 60/min cap; 3 concurrent items with ~2 sources = ~6 req/min peak, well under limit
- TTLCache maxsize=1: single dashboard endpoint, 5-minute TTL; key='dashboard'
- API POST /api/wishlist now returns immediately with item (no listings yet); iOS Shortcut contract preserved
- Cache invalidated eagerly on every mutation (edit, delete, scan completion)
- Adapter registry uses enabled flag per entry for future per-source toggling without overengineering
- return_exceptions=True in registry gather isolates per-adapter failures so other sources still return results
- Status endpoint on web_router (no API key) for dashboard JS polling — iOS Shortcut uses api_router only
- Full page reload on listing arrival — simpler than partial DOM replacement, no stale state risk
- 2-minute polling timeout prevents runaway intervals if scan stalls
- [Phase 02-new-sources]: Semaphore(5) for eBay Browse API — higher limit than Discogs; per-adapter semaphores replace global scan_semaphore
- [Phase 02-new-sources]: OAuth token cached at module level with asyncio.Lock() for race-condition-safe refresh; 60s expiry buffer
- [Phase 02-new-sources]: ships_from hardcoded to Australia for EBAY_AU marketplace; all results are AU sellers
- [Phase 02-02]: Discrepancy search URL is /?kw= not /search?q= -- live HTML inspection revealed correct Neto param
- [Phase 02-02]: Clarity Records set enabled=False -- DNS failure during implementation; BigCommerce standard selectors in place, re-enable once site confirmed reachable
- [Phase 02-02]: AU store adapters use Semaphore(1) + sleep(1.5) -- small independent stores, conservative rate limiting
- [Phase 02-03]: Juno search page is JS-rendered; artist browse page used as fallback -- works for artist-name queries
- [Phase 02-03]: Bandcamp item_type=p is invalid filter; text-based vinyl filter used (check 'vinyl' in album title/subhead)
- [Phase 02-new-sources]: clarityrecords.com.au NXDOMAIN confirmed on second check (02-04); adapter stays disabled=False; SRC-03 and SRC-06 remain open until site is reachable

### Todos

- None yet

### Blockers

- None yet

## Last Updated

2026-04-02 — Completed 02-03 (Juno Records artist-page scraper + Bandcamp vinyl album adapter; full 7-adapter registry)
