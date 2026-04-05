# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-04-05
**Phases:** 5 | **Plans:** 17 | **Tasks:** 14

### What Was Built
- **Performance foundation** — async scan decoupling, N+1 fix, TTL cache, per-adapter semaphores
- **7-source scraper network** — eBay AU (Browse API), Discrepancy Records, Juno, Bandcamp, plus existing Discogs/Shopify; adapter registry makes adding new sources a one-dict-entry change
- **CRATE design system** — 545-line custom CSS replacing Bootstrap/Tailwind; near-black palette, card grid with high-res record artwork, WCAG AA contrast, 44px touch targets, modal ARIA, inline delete confirmation
- **AUD landed cost pipeline** — FX conversion service, Discogs release-endpoint artwork, per-listing `aud_total` enrichment
- **Database migration robustness** — SQLite inline constraint detection and table rebuild handles schema drift between dev and prod

### What Worked
- Wave-based execution with worktree isolation kept plan changes clean and atomic
- CSS-only phases (05-01, 05-02) were fast and low-risk — pure design system work with no backend impact
- Keeping adapters stateless and uniform (`search_and_get_listings(query, type) → list[dict]`) made Phase 2 additions mechanical
- Per-phase SUMMARY.md files made the PR body and milestone archive essentially self-writing

### What Was Inefficient
- Worktree agents repeatedly branched from old base commits (likely `main` instead of current feature branch HEAD), requiring manual cherry-picks or direct edits in wave 2 of phase 5
- ROADMAP.md and STATE.md conflict in worktree merges — these shared planning files are a known friction point; orchestrator owning writes helps but doesn't fully solve it
- Traceability table in REQUIREMENTS.md wasn't updated during phase execution (UI-01, UI-03, UI-06 showed Pending despite being shipped) — requirements hygiene needs a phase-end checkpoint

### Patterns Established
- **Adapter pattern:** Each source adapter is a single async function returning `list[dict]`; registered in one place; scanner is source-agnostic
- **Migration pattern:** `run_migrations()` in `database.py` handles schema evolution; SQLite requires table rebuilds for constraint changes
- **CSS design token naming:** `--color-*`, `--space-*`, `--text-*` with semantic names (`--color-accent`, `--color-surface`, etc.)
- **Phase 5 as polish phase:** UI/UX polish phases work well as standalone "apply audit findings" phases with no backend coupling

### Key Lessons
1. **Worktree agents need explicit base commit resets** — always run `git reset --hard $EXPECTED_BASE` at worktree start, not just a merge-base check
2. **SQLite inline constraints can't be dropped** — detect via `sqlite_master` and rebuild the table; don't rely on `DROP INDEX` alone
3. **Requirements traceability needs active maintenance** — mark requirements complete in the file at execution time, not retrospectively
4. **Planning files (STATE.md, ROADMAP.md) should never be in a worktree's commit scope** — orchestrator-only writes prevent last-merge-wins corruption

### Cost Observations
- Model mix: ~100% sonnet (executor and verifier)
- Sessions: ~6 across 5 phases
- Notable: Phase 5 wave 2 worktree conflict required inline manual edits — adds ~5 min per affected wave; worth fixing the base-commit issue in the agent prompt

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 5 | 17 | First milestone — baseline established |

### Cumulative Quality

| Milestone | Automated Tests | Human UAT Items | Zero-Dep Additions |
|-----------|----------------|-----------------|-------------------|
| v1.0 | 0 (no test suite) | 4 (browser checks) | 0 |

### Top Lessons (Verified Across Milestones)

1. Worktree agent base-commit hygiene is the #1 source of friction in parallel execution
2. CSS-only phases are the fastest and lowest-risk work units — isolate visual changes when possible
