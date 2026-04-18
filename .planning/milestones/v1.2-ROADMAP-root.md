# Roadmap: Vinyl Wishlist Manager

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-04-05)
- ✅ **v1.1 UX Polish & Album Selection** — Phases 6–12 (shipped 2026-04-11)
- ✅ **v1.2 Signal Intelligence & Notifications** — Phases 13–15 (shipped 2026-04-14)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–5) — SHIPPED 2026-04-05</summary>

- [x] Phase 1: Infrastructure (3/3 plans) — completed 2026-04-02
- [x] Phase 2: New Sources (4/4 plans) — completed 2026-04-03
- [x] Phase 3: UI Redesign (4/4 plans) — completed 2026-04-03
- [x] Phase 4: UI Polish (3/3 plans) — completed 2026-04-05
- [x] Phase 5: Improve UI and UX Design (3/3 plans) — completed 2026-04-05

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.1 UX Polish & Album Selection (Phases 6–12) — SHIPPED 2026-04-11</summary>

- [x] Phase 6: Discogs Typeahead (3/3 plans) — completed 2026-04-09
- [x] Phase 7: Image Priority + Scan Fix (2/2 plans) — completed 2026-04-09
- [x] Phase 8: Brand Font Upgrade (1/1 plans) — completed 2026-04-09
- [x] Phase 9: Email Redesign (2/2 plans) — completed 2026-04-09
- [x] Phase 10: UI Polish (3/3 plans) — completed 2026-04-11
- [x] Phase 11: UI Fixes (5/5 plans) — completed 2026-04-11
- [x] Phase 12: UI Fixes Round 2 (2/2 plans) — completed 2026-04-11

Full details: `.planning/milestones/v1.1-ROADMAP.md`

</details>

<details>
<summary>✅ v1.2 Signal Intelligence & Notifications (Phases 13–15) — SHIPPED 2026-04-14</summary>

- [x] Phase 13: Signal Filters (3/3 plans) — completed 2026-04-13
- [x] Phase 14: Feedback Primitives UI Hint (1/1 plans) — completed 2026-04-13
- [x] Phase 15: Notification Expansion (4/4 plans) — completed 2026-04-13

Full details: `.planning/milestones/v1.2-ROADMAP.md`

</details>

## Phase Details (Archived)

<details>
<summary>v1.1 phase details — see milestones/v1.1-ROADMAP.md for full content</summary>

### Phase 6: Discogs Typeahead
**Goal**: Users can search for and pin a specific Discogs album release when adding or editing a wishlist item
**Depends on**: Nothing (first phase of v1.1; all backend targets are isolated)
**Requirements**: TYPE-01, TYPE-02, TYPE-03, TYPE-04
**Success Criteria** (what must be TRUE):
  1. Typing in the album name field shows a dropdown of matching Discogs releases (title, artist, year, cover thumb) within 300ms of pausing
  2. User can navigate the dropdown with arrow keys and confirm a selection with Enter or click
  3. User can re-select or change the linked Discogs release when editing an existing wishlist item
  4. Rapid typing does not fire a new request on every keystroke — debounce holds for at least 300ms before fetching
  5. iOS Shortcut (`POST /api/wishlist` with `X-API-Key`) continues to work without any change to the Shortcut itself
**Plans**: 3 plans
Plans:
- [x] 06-01-PLAN.md — Backend: DB migration, schemas, typeahead API endpoint, pinned-release scanner logic
- [x] 06-02-PLAN.md — Frontend: typeahead CSS/JS, add/edit modal integration, human verification
- [x] 06-03-PLAN.md — Gap closure: spinner visibility fixes (selectResult, type change handler)


### Phase 7: Image Source Priority + Scan Log Fix
**Goal**: Record artwork shows the scraped store image when available, and scan log messages use the correct item type label
**Depends on**: Nothing (backend-only; independent of Phase 6)
**Requirements**: IMG-01, IMG-02, BUG-02
**Success Criteria** (what must be TRUE):
  1. A wishlist item with a store-sourced image shows that image on the dashboard card (not the Discogs thumb)
  2. A wishlist item with no store image falls back to the Discogs artwork, then the vinyl placeholder SVG — never a broken image
  3. Scan log for an album-type item says "no album results" (not "no artist results") when a source returns nothing
**Plans**: 2 plans
Plans:
- [x] 07-01-PLAN.md — Backend: Listing.image_url column, adapter image extraction, scanner image priority, scan_status type tracking
- [x] 07-02-PLAN.md — Frontend: scan log type label display in base.html

### Phase 8: Brand Font Upgrade
**Goal**: The CRATE logotype in the nav uses a brutalist display web font loaded from a static asset with no external CDN dependency
**Depends on**: Nothing (fully isolated — one font file, one CSS rule)
**Requirements**: FONT-01
**Plans**: 1 plan
Plans:
- [x] 08-01-PLAN.md — Self-host Bodoni Moda Bold woff2, add @font-face + CSS custom property + preload, update .nav-brand

### Phase 9: Email Redesign
**Goal**: Deal alert emails arrive with a scannable summary, CRATE-consistent dark aesthetic, and inline CSS that renders correctly in Gmail and Outlook
**Depends on**: Nothing (self-contained — only `notifier.py` and a new template file)
**Requirements**: EMAIL-01, EMAIL-02, EMAIL-03
**Plans**: 2 plans
Plans:
- [x] 09-01-PLAN.md — Email template with inline CSS, dark aesthetic, deal summary
- [x] 09-02-PLAN.md — Notifier integration and email rendering

### Phase 10: UI Polish
**Goal**: The dashboard is visually refined — readable typography, accessible controls, responsive at 3 columns, and free of layout bugs
**Depends on**: Phases 6–9 complete (polish after all logic and content changes are stable)
**Requirements**: UIP-01, UIP-02, UIP-03, UIP-04, UIP-05, UIP-06, UIP-07, UIP-08, UIP-09, UIP-10, BUG-01
**Plans**: 3 plans
Plans:
- [x] 10-01-PLAN.md — CSS design tokens: type scale, spacing tiers, card tier classes, disabled buttons, table cleanup, spinner fix
- [x] 10-02-PLAN.md — Template updates: card tiers, stats bar, H2 tokens, disabled button JS, copy updates
- [x] 10-03-PLAN.md — Verification: automated requirement checks + visual human checkpoint

### Phase 11: UI Fixes
**Goal**: Visual overhaul and UX fixes — warm B&W palette, reverted typography, card system with hover-reveal deals, logo + font branding, image loading states, overlapping button fix, email template update
**Depends on**: Phase 10 complete
**Requirements**: D-01 through D-18 (see 11-CONTEXT.md), BUG-01
**Plans**: 5 plans
Plans:
- [x] 11-01-PLAN.md — CSS design token update: warm B&W palette, typography revert
- [x] 11-02-PLAN.md — Card system and interaction layer
- [x] 11-03-PLAN.md — BUG-01 fix, skeleton loading, placeholder image
- [x] 11-04-PLAN.md — Logo + font identity
- [x] 11-05-PLAN.md — Email palette update

### Phase 12: UI Fixes Round 2
**Goal**: Final visual polish — Inter font, ghost card readability, consistent price sizing, toast visibility fix, email font consistency, notify email checkbox bug
**Depends on**: Phase 11 complete
**Plans**: 2 plans
Plans:
- [x] 12-01-PLAN.md — Visual polish: Inter font, ghost cards, price sizing, tick icon, scrollbar, card titles
- [x] 12-02-PLAN.md — Notify email checkbox bug fix and email branding

</details>

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
