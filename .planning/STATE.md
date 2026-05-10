---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: Public Release
status: executing
last_updated: "2026-05-10T04:50:01.044Z"
last_activity: 2026-05-10 -- Phase 29 planning complete
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 7
  completed_plans: 4
  percent: 57
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-27)

**Core value:** Show me the cheapest way to buy the records I want, right now.
**Current focus:** Phase 28 — infrastructure-migration

## Current Position

Phase: 29
Plan: Not started
Status: Ready to execute
Last activity: 2026-05-10 -- Phase 29 planning complete

Progress: [░░░░░░░░░░] 0% (v1.6)

## Phase Overview

| Phase | Goal | Status |
|-------|------|--------|
| 28. Infrastructure Migration | New host, auto-deploy, all env vars | Not started |
| 29. Auth Foundation | Sign-up, sign-in, session, route guards, bcrypt | Not started |
| 30. Data Isolation | Per-user wishlist items and listings | Not started |
| 31. Auth Expansion | Password reset, Google OAuth, rate limiting | Not started |
| 32. User Features | Personal API keys, public shareable wishlist | Not started |

## Accumulated Context

### Decisions

- Heartland: products.json fallback; suggest.json disabled on their Shopify store
- Clarity: page 1 only; BigCommerce relevance ordering sufficient for targeted queries
- Phase order: Infra → Auth Foundation → Data Isolation → Auth Expansion → User Features
  (Auth must exist before data can be scoped; data isolation before API keys make sense)

### Todos

- **[backlog]** eBay adapter may return cassette listings alongside vinyl — add optional vinyl-only filter in a future phase
- **[backlog]** Delete Railway service and PostgreSQL add-on — fully superseded by Fly.io + Neon after Phase 28 completion

### Blockers

- None — infrastructure host choice TBD during Phase 28 planning

## Last Updated

2026-04-27 — v1.6 roadmap created, ready to plan Phase 28
