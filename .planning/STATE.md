---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Signal & Polish
status: roadmap_ready
last_updated: "2026-04-12T00:00:00.000Z"
last_activity: 2026-04-12
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Current Position

Phase: 13 — Signal Filters (not started)
Plan: —
Status: Roadmap ready; awaiting phase planning
Last activity: 2026-04-12 — v1.2 roadmap created (5 phases, 18 requirements mapped)

## Project Reference

See: .planning/PROJECT.md
**Core value:** Show me the cheapest way to buy the records I want, right now.
**Current focus:** v1.2 Signal & Polish — Phase 13 Signal Filters

## Accumulated Context

### Decisions (carried from v1.1)

- Semaphore(3) for Discogs; per-adapter semaphores for other sources
- TTLCache maxsize=1 for dashboard, 5-min TTL
- API POST /api/wishlist returns immediately; iOS Shortcut contract preserved
- Adapter registry uses enabled flag per entry
- Clarity Records disabled — NXDOMAIN
- CRATE design system: near-black palette, Inter body + Bodoni Moda display
- Email template uses inline hex CSS only

### Decisions (v1.2 roadmap)

- Phase order: Filters → Feedback → Notifications → Branding → Security (clean data first; security last as capstone)
- `rapidfuzz` selected for relevance scoring (stack research); `pip-audit` for security audit
- UI-only default for add-item type; API default unchanged (preserves iOS Shortcut contract)
- Unified digest email preferred over separate emails per notification type
- Logo cache-bust via filename rename, not query string (mail clients cache aggressively)

### Todos

- Plan Phase 13 (Signal Filters)

### Blockers

- None

## Last Updated

2026-04-12 — v1.2 roadmap created
