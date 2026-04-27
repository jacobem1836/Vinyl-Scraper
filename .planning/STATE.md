---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: Public Release
status: ready_to_plan
last_updated: "2026-04-27"
last_activity: 2026-04-27
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-27)

**Core value:** Show me the cheapest way to buy the records I want, right now.
**Current focus:** v1.6 Public Release — Phase 28: Infrastructure Migration

## Current Position

Phase: 28 of 32 (Infrastructure Migration)
Plan: — (not yet planned)
Status: Ready to plan
Last activity: 2026-04-27 — v1.6 roadmap created (5 phases, 16 requirements mapped)

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

### Blockers

- None — infrastructure host choice TBD during Phase 28 planning

## Last Updated

2026-04-27 — v1.6 roadmap created, ready to plan Phase 28
