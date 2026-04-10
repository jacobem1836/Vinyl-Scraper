---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: UX Polish & Album Selection
status: executing
last_updated: "2026-04-08T13:30:20.255Z"
last_activity: 2026-04-08 -- Phase 10 execution started
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 11
  completed_plans: 8
  percent: 73
---

# Project State

## Current Position

Phase: 10 (ui-polish) — EXECUTING
Plan: 1 of 3
Status: Executing Phase 10
Last activity: 2026-04-08 -- Phase 10 execution started

```
v1.1 Progress: [████░░░░░░] 40% — 2/5 phases complete
```

## Project Reference

See: .planning/PROJECT.md
**Core value:** Show me the cheapest way to buy the records I want, right now.
**Current focus:** Phase 10 — ui-polish

## Performance Metrics

| Metric | Value |
|--------|-------|
| Phases complete | 0 / 5 |
| Plans complete | 0 / ? |
| Requirements mapped | 22 / 22 |
| v1.1 started | 2026-04-05 |

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
- [Phase 03-ui-redesign]: Pre-resolve FX rates at route handler level so _enrich_item stays synchronous
- [Phase 03-ui-redesign]: TTLCache(maxsize=4, ttl=3600) for FX rates — 1 hour TTL, room for future currencies
- [Phase 03-ui-redesign]: Cards are pure <a> tags; edit button removed from card face — edit accessible from detail page only (D-05)
- [Phase 03-ui-redesign]: aud_total falls back to landed_price with currency label when FX fetch fails — price column never blank

### Roadmap Evolution

- 2026-04-05: v1.1 roadmap created — 5 phases (6–10), 22 requirements mapped
- 2026-04-09: Phase 11 added: UI fixes

### Todos

- None yet

### Blockers

- None yet

## Session Continuity

**To resume:** Run `/gsd-plan-phase 6` to begin planning Phase 6 (Discogs Typeahead).

**Key constraints to keep in mind:**

- iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) must not break — any new schema field must be `Optional[...] = None`
- Phase 10 (UI Polish) requires magic MCP + stitch + ui-ux-pro-max + design-for-ai tools during planning and execution
- Discogs typeahead must have 300ms debounce + AbortController — missing either will exhaust the 60 req/min rate limit
- Email template must use inline hex CSS only — no CSS custom properties, no flexbox/grid

## Last Updated

2026-04-05 — v1.1 roadmap created (Phases 6–10, 22 requirements)
