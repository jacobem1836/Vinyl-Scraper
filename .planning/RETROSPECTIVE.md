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

## Milestone: v1.2 — Signal Intelligence & Notifications

**Shipped:** 2026-04-14
**Phases:** 3 (13–15) | **Plans:** 8

### What Was Built
- **Signal filtering** — relevance scoring, digital listing suppression, ships_from enrichment from Discogs marketplace API; results ranked at query time
- **Toast feedback system** — `window.showToast()` helper wired to all user-initiated actions; single `#toast` primitive, no secondary dialogs; modal type resets on every open
- **Notification expansion** — back-in-stock and price-drop detection with snapshot columns; cooldown gate prevents duplicate sends; collect-then-dispatch scheduler sends one digest per scan run; 9 unit tests

### What Worked
- TDD approach for Phase 15 (write failing tests first, then implement) produced clean notifier functions with full unit coverage
- Collect-then-dispatch pattern is a strong architectural win — natural deduplication, no per-listing email churn
- Verification-first approach (VERIFICATION.md before marking complete) caught missing wiring early
- Quick task gsd-quick pattern worked well for the ad-hoc scanning toast feature

### What Was Inefficient
- Quick task worktree accidentally deleted Phase 13–15 planning artifacts (PLAN.md, SUMMARY.md files, ROADMAP.md, REQUIREMENTS.md) — required milestone reconstruction from git log and VERIFICATION.md files
- `app/services/test_relevance.py` landed in the wrong directory (services/ not tests/) — cleanup deferred
- Phase 13 planning files were never added to the main ROADMAP.md before the worktree deletion

### Patterns Established
- **Collect-then-dispatch:** Scheduler collects events from all item scans, then dispatches one digest — avoids per-item email noise and naturally deduplicates
- **Snapshot column pattern:** `prev_price` + `prev_is_in_stock` written just before overwrite on every scan — simple, no separate history table needed
- **Toast primitive:** Single `#toast` element for all feedback; server-side `?toast=` redirects feed the same element as JS-driven toasts

### Key Lessons
1. **Quick task worktrees should never touch planning files** — the .planning/ directory should be excluded from worktree scope or treated as orchestrator-only writes
2. **TDD for async notification logic pays off** — snapshot + detect + cooldown logic has enough edge cases that tests-first prevents regressions
3. **Verification docs are the safety net when planning docs are lost** — VERIFICATION.md files survived the worktree deletion and contained enough to reconstruct the milestone

### Cost Observations
- Model mix: ~100% sonnet
- Sessions: ~3 across 3 phases
- Notable: Phase 15 worktree deletion incident added ~30 min for manual restore; total cost was low because git log + VERIFICATION.md had everything needed

---

## Milestone: v1.3 — Visual Overhaul

**Shipped:** 2026-04-18
**Phases:** 4 (16–19) | **Plans:** 6 | **Timeline:** 4 days

### What Was Built
- **True black palette** — #000 across all surfaces; custom 4px translucent-white scrollbars; Warner Music–inspired editorial restraint (Phase 16)
- **Gothic A1 typography** — self-hosted woff2 (Light/Regular/Medium) replaces Inter; @font-face preload; item name larger and heavier than price on all surfaces (Phase 17)
- **Toast unification** — `window.showToast()` is now the single path for all post-add and scan feedback; scan panel gated to `is_running` state only; em-dash in copy (Phase 18)
- **Card expansion** — 3-col max (removed 4-col breakpoint), wider gap (space-md), tighter 12px container/nav padding (Phase 19)

### What Worked
- CSS-only phases (16, 17, 19) were fast, low-risk, and had clear success criteria — visual UAT is simple
- Toast interrupt-and-restore pattern (Phase 18) was a clean solution to competing toast messages — brief replacement then restore
- Phases 18 and 19 had no formal PLAN.md files but executed cleanly through direct SUMMARY-based execution — lighter-weight approach suits small-scope fixes
- Human UAT sign-off per phase kept visual quality bar high without needing automated tests

### What Was Inefficient
- Phase 17 plan count in ROADMAP.md showed 2/3 at time of archival (stale) — roadmap status not updated in sync with execution
- Phase 18 UAT recorded 1 issue before it was fixed; the UAT file wasn't updated after the fix commits landed — requires manual reconciliation at milestone completion
- Worktree merge conflict in Phase 18 deleted planning files again — same recurring issue as v1.2; worktrees and .planning/ don't mix

### Patterns Established
- **Toast interrupt-and-restore:** Short toasts temporarily replace active long-running toast, then restore it — prevents UI confusion when a new event fires mid-scan
- **Visual-only phases are low-overhead:** CSS-only phases need no backend review, no migration, no API contract concern — treat them as fast iteration cycles

### Key Lessons
1. **Update ROADMAP.md status immediately when phases complete** — stale status causes friction at milestone completion
2. **Update UAT file after post-UAT fixes** — mark issues resolved or retest; don't leave failed tests with no resolution note
3. **Worktrees must not touch planning files** — this is now the third milestone where worktree state deleted .planning/ artifacts

### Cost Observations
- Model mix: ~100% sonnet
- Sessions: ~3 across 4 phases
- Notable: Pure CSS/HTML milestone — fastest milestone by work-per-phase; visual phases are the highest-leverage work for perceived quality

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 5 | 17 | First milestone — baseline established |
| v1.1 | 7 | 16 | UX polish + Discogs typeahead — design tool stack introduced |
| v1.2 | 3 | 8 | Signal intelligence + notifications — TDD introduced for notifier |
| v1.3 | 4 | 6 | Visual overhaul — CSS-only phases, lightest milestone by weight |

### Cumulative Quality

| Milestone | Automated Tests | Human UAT Items | Zero-Dep Additions |
|-----------|----------------|-----------------|-------------------|
| v1.0 | 0 (no test suite) | 4 (browser checks) | 0 |
| v1.1 | 0 | 8 (browser checks) | 0 |
| v1.2 | 9 (test_notifier.py) | 3 (user-confirmed) | 0 |
| v1.3 | 0 (visual-only) | 12 (4 UAT passes) | 0 |

### Top Lessons (Verified Across Milestones)

1. Worktree agent base-commit hygiene is the #1 source of friction in parallel execution
2. CSS-only phases are the fastest and lowest-risk work units — isolate visual changes when possible
3. Quick task worktrees (and all worktrees) must not touch planning files — .planning/ should be orchestrator-only (recurring every milestone)
4. TDD for notification/detection logic pays off — snapshot + detect + cooldown has enough edge cases to justify tests-first
5. Keep ROADMAP.md and UAT files updated in real-time during execution — stale status creates reconciliation work at milestone close
