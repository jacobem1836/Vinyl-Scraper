# Roadmap: Vinyl Wishlist Manager

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-04-05)
- ✅ **v1.1 UX Polish & Album Selection** — Phases 6–12 (shipped 2026-04-12)
- ✅ **v1.2 Signal Intelligence & Notifications** — Phases 13–15 (shipped 2026-04-14)
- ✅ **v1.3 Visual Overhaul** — Phases 16–19 (shipped 2026-04-18)
- 🔄 **v1.4 Quality & Gaps** — Phases 20–24 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–5) — SHIPPED 2026-04-05</summary>

- [x] Phase 1: Infrastructure (3/3 plans) — completed 2026-04-02
- [x] Phase 2: New Sources (4/4 plans) — completed 2026-04-03
- [x] Phase 3: UI Redesign (4/4 plans) — completed 2026-04-03
- [x] Phase 4: UI Polish (3/3 plans) — completed 2026-04-05
- [x] Phase 5: Improve UI/UX (3/3 plans) — completed 2026-04-05

</details>

<details>
<summary>✅ v1.1 UX Polish & Album Selection (Phases 6–12) — SHIPPED 2026-04-12</summary>

- [x] Phase 6: Discogs Typeahead (3/3 plans) — completed 2026-04-09
- [x] Phase 7: Image Priority + Scan Fix (2/2 plans) — completed 2026-04-09
- [x] Phase 8: Brand Font Upgrade (1/1 plan) — completed 2026-04-09
- [x] Phase 9: Email Redesign (2/2 plans) — completed 2026-04-09
- [x] Phase 10: UI Polish (3/3 plans) — completed 2026-04-11
- [x] Phase 11: UI Fixes (5/5 plans) — completed 2026-04-11
- [x] Phase 12: UI Fixes Round 2 (2/2 plans) — completed 2026-04-11

</details>

<details>
<summary>✅ v1.2 Signal Intelligence & Notifications (Phases 13–15) — SHIPPED 2026-04-14</summary>

- [x] Phase 13: Signal Filters (3/3 plans) — completed 2026-04-13
- [x] Phase 14: Feedback Primitives UI Hint (1/1 plan) — completed 2026-04-13
- [x] Phase 15: Notification Expansion (4/4 plans) — completed 2026-04-13

</details>

<details>
<summary>✅ v1.3 Visual Overhaul (Phases 16–19) — SHIPPED 2026-04-18</summary>

- [x] Phase 16: Visual Foundation (2/2 plans) — completed 2026-04-15
- [x] Phase 17: Typography Overhaul (3/3 plans) — completed 2026-04-15
- [x] Phase 18: UI Consistency Fixes (2 plans, no PLAN.md) — completed 2026-04-18
- [x] Phase 19: Card Layout Expansion (1/1 plan) — completed 2026-04-18

See archive: `.planning/milestones/v1.3-ROADMAP.md`

</details>

### v1.4 Quality & Gaps (Phases 20–24)

- [x] **Phase 20: Cleanup & Config** — Remove dead Clarity code, wire eBay keys (completed 2026-04-18)
- [ ] **Phase 21: Bug Fixes** — Fix typeahead spinner, image skeleton shimmer
- [ ] **Phase 22: Resend Email** — Migrate SMTP to Resend API
- [ ] **Phase 23: Discogs Release Selection** — Manual release pinning on item detail
- [ ] **Phase 24: Per-Item Notification Thresholds** — Custom % per wishlist item

## Phase Details

### Phase 20: Cleanup & Config
**Goal**: The codebase is free of dead Clarity code and eBay works in production
**Depends on**: Nothing (first v1.4 phase)
**Requirements**: CLEAN-01, CFG-01
**Success Criteria** (what must be TRUE):
  1. `clarity.py` and its adapter registry entry are gone from the codebase
  2. eBay adapter authenticates successfully in production (Railway env vars present and used)
  3. A scan with eBay enabled returns listings without auth errors
**Plans**: 1 plan
Plans:
- [x] 20-01-PLAN.md — Remove dead Clarity adapter and harden eBay config

### Phase 21: Bug Fixes
**Goal**: Typeahead spinner clears reliably and image skeletons use the correct dark shimmer style
**Depends on**: Phase 20
**Requirements**: BUG-03, UI-07
**Success Criteria** (what must be TRUE):
  1. Selecting a typeahead result hides the spinner immediately
  2. Changing the type dropdown while typeahead is open hides the spinner immediately
  3. Image skeletons display a diagonal top-left → bottom-right sweep shimmer (not pulse or glow)
  4. Skeleton shimmer is visibly dark, matching the true-black card surface
**Plans**: 1 plan
Plans:
- [ ] 21-01-PLAN.md — Fix typeahead spinner clearing and replace skeleton pulse with diagonal dark shimmer
**UI hint**: yes

### Phase 22: Resend Email
**Goal**: Deal alert emails are sent via the Resend API; SMTP configuration is no longer required
**Depends on**: Phase 20
**Requirements**: EMAIL-04
**Success Criteria** (what must be TRUE):
  1. A triggered deal alert email arrives in the inbox when sent via Resend
  2. SMTP environment variables are no longer required for email to function
  3. Resend API key is read from env vars; no credentials are hardcoded
**Plans**: 1 plan
Plans:
- [ ] 22-01-PLAN.md — [to be planned]

### Phase 23: Discogs Release Selection
**Goal**: Users can search for and pin a specific Discogs release to a wishlist item, fixing wrong artwork and scan mismatches
**Depends on**: Phase 20
**Requirements**: DISC-01, DISC-02, DISC-03
**Success Criteria** (what must be TRUE):
  1. User can open item detail and search Discogs releases by title/artist inline
  2. User can select a release from search results and pin it to the item
  3. Item detail page shows artwork from the pinned release, not the auto-search result
  4. Scanning an item with a pinned release ID uses that release ID directly instead of running a title/artist search
**Plans**: 1 plan
Plans:
- [ ] 23-01-PLAN.md — [to be planned]
**UI hint**: yes

### Phase 24: Per-Item Notification Thresholds
**Goal**: Each wishlist item can have its own notification threshold, overriding the global default
**Depends on**: Phase 20
**Requirements**: NOTIF-05, NOTIF-06
**Success Criteria** (what must be TRUE):
  1. User can set a custom % threshold on an individual wishlist item via the edit form
  2. A wishlist item with a custom threshold triggers alerts at that threshold, not the global one
  3. A wishlist item without a custom threshold continues to use the global default
  4. The custom threshold value is visible on item detail so the user knows what's set
**Plans**: 1 plan
Plans:
- [ ] 24-01-PLAN.md — [to be planned]

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure | v1.0 | 3/3 | Complete | 2026-04-02 |
| 2. New Sources | v1.0 | 4/4 | Complete | 2026-04-03 |
| 3. UI Redesign | v1.0 | 4/4 | Complete | 2026-04-03 |
| 4. UI Polish | v1.0 | 3/3 | Complete | 2026-04-05 |
| 5. Improve UI/UX | v1.0 | 3/3 | Complete | 2026-04-05 |
| 6. Discogs Typeahead | v1.1 | 3/3 | Complete | 2026-04-09 |
| 7. Image Priority + Scan Fix | v1.1 | 2/2 | Complete | 2026-04-09 |
| 8. Brand Font Upgrade | v1.1 | 1/1 | Complete | 2026-04-09 |
| 9. Email Redesign | v1.1 | 2/2 | Complete | 2026-04-09 |
| 10. UI Polish | v1.1 | 3/3 | Complete | 2026-04-11 |
| 11. UI Fixes | v1.1 | 5/5 | Complete | 2026-04-11 |
| 12. UI Fixes Round 2 | v1.1 | 2/2 | Complete | 2026-04-11 |
| 13. Signal Filters | v1.2 | 3/3 | Complete | 2026-04-13 |
| 14. Feedback Primitives UI Hint | v1.2 | 1/1 | Complete | 2026-04-13 |
| 15. Notification Expansion | v1.2 | 4/4 | Complete | 2026-04-13 |
| 16. Visual Foundation | v1.3 | 2/2 | Complete | 2026-04-15 |
| 17. Typography Overhaul | v1.3 | 3/3 | Complete | 2026-04-15 |
| 18. UI Consistency Fixes | v1.3 | 2/2 | Complete | 2026-04-18 |
| 19. Card Layout Expansion | v1.3 | 1/1 | Complete | 2026-04-18 |
| 20. Cleanup & Config | v1.4 | 1/1 | Complete   | 2026-04-18 |
| 21. Bug Fixes | v1.4 | 0/1 | Not started | - |
| 22. Resend Email | v1.4 | 0/? | Not started | - |
| 23. Discogs Release Selection | v1.4 | 0/? | Not started | - |
| 24. Per-Item Notification Thresholds | v1.4 | 0/? | Not started | - |

*Roadmap updated: 2026-04-18 — v1.4 Quality & Gaps phases added*
