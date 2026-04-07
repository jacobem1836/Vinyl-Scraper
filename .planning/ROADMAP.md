# Roadmap: Vinyl Wishlist Manager

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-04-05)
- **v1.1 UX Polish & Album Selection** — Phases 6–10 (current)

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

### v1.1 UX Polish & Album Selection

- [ ] **Phase 6: Discogs Typeahead** — Album search-as-you-type in add/edit modals, pinning a specific Discogs release
- [ ] **Phase 7: Image Source Priority + Scan Log Fix** — Store images preferred over Discogs fallback; scan log type label corrected
- [ ] **Phase 8: Brand Font Upgrade** — CRATE logotype uses self-hosted brutalist display font with no CDN dependency
- [ ] **Phase 9: Email Redesign** — Deal alert emails redesigned with inline CSS, CRATE aesthetic, and scannable deal summary
- [ ] **Phase 10: UI Polish** — Typography scale, button states, modal accessibility, responsive grid, inline delete confirmation, overlapping button fix

## Phase Details

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
- [ ] 06-03-PLAN.md — Gap closure: spinner visibility fixes (selectResult, type change handler)


### Phase 7: Image Source Priority + Scan Log Fix
**Goal**: Record artwork shows the scraped store image when available, and scan log messages use the correct item type label
**Depends on**: Nothing (backend-only; independent of Phase 6)
**Requirements**: IMG-01, IMG-02, BUG-02
**Success Criteria** (what must be TRUE):
  1. A wishlist item with a store-sourced image shows that image on the dashboard card (not the Discogs thumb)
  2. A wishlist item with no store image falls back to the Discogs artwork, then the vinyl placeholder SVG — never a broken image
  3. Scan log for an album-type item says "no album results" (not "no artist results") when a source returns nothing
**Plans**: TBD

### Phase 8: Brand Font Upgrade
**Goal**: The CRATE logotype in the nav uses a brutalist display web font loaded from a static asset with no external CDN dependency

**REQUIRED TOOLING** — plan-phase and execute-phase subagents MUST invoke ALL of the following before making any design decisions:
- `ui-ux-pro-max` Claude skill — font pairing and typographic direction
- `design-for-ai` Claude skill — visual design principles
- `mcp__magic__*` — 21st Magic component inspiration for font/brand patterns
- `mcp__stitch__*` — design system application

**Depends on**: Nothing (fully isolated — one font file, one CSS rule)
**Requirements**: FONT-01
**Success Criteria** (what must be TRUE):
  1. The CRATE nav wordmark renders in a brutalist display font (not the system fallback) on page load
  2. The font file is served from `/static/fonts/` — no request goes to an external CDN at runtime
  3. The wordmark does not flash or reflow during page load (no FOUT)
  4. Font selection was informed by ui-ux-pro-max + magic MCP before implementation
**Plans**: TBD
**UI hint**: yes

### Phase 9: Email Redesign
**Goal**: Deal alert emails arrive with a scannable summary, CRATE-consistent dark aesthetic, and inline CSS that renders correctly in Gmail and Outlook

**REQUIRED TOOLING** — plan-phase and execute-phase subagents MUST invoke ALL of the following before making any design decisions:
- `ui-ux-pro-max` Claude skill — email layout and visual hierarchy direction
- `design-for-ai` Claude skill — visual design principles
- `mcp__magic__*` — 21st Magic component inspiration for email patterns
- `mcp__stitch__*` — design system application

**Depends on**: Nothing (self-contained — only `notifier.py` and a new template file)
**Requirements**: EMAIL-01, EMAIL-02, EMAIL-03
**Success Criteria** (what must be TRUE):
  1. A deal alert email renders correctly in Gmail web (no broken layout, no stripped styles)
  2. Email body shows item name, best price, percentage below typical price, and a direct link to the item detail page
  3. Email visual design is dark-themed (near-black background, white text) consistent with the CRATE dashboard aesthetic, using only inline CSS and hex color literals (no CSS custom properties)
  4. Email layout was designed using ui-ux-pro-max + magic MCP before implementation
**Plans**: TBD
**UI hint**: yes

### Phase 10: UI Polish
**Goal**: The dashboard is visually refined — readable typography, accessible controls, responsive at 3 columns, and free of layout bugs

**REQUIRED TOOLING** — plan-phase and execute-phase subagents MUST invoke ALL of the following before making any design decisions:
- `ui-ux-pro-max` Claude skill — design direction and audit for every change
- `design-for-ai` Claude skill — visual design principles
- `mcp__magic__*` — 21st Magic component builder/refiner for UI patterns
- `mcp__stitch__*` — design system application and screen generation

**Depends on**: Phases 6–9 complete (polish after all logic and content changes are stable)
**Requirements**: UIP-01, UIP-02, UIP-03, UIP-04, UIP-05, UIP-06, UIP-07, UIP-08, UIP-09, UIP-10, BUG-01
**Success Criteria** (what must be TRUE):
  1. All body text at 14px on the dark background meets WCAG AA contrast (4.5:1) — `--color-text-faint` is at least #686868
  2. All buttons (btn-cta, btn-secondary, btn-destructive) show a visible focus ring when focused via keyboard, an active press micro-animation, and a disabled appearance when unavailable
  3. The card grid switches to 3 columns at 1024px viewport width
  4. Clicking delete on a card shows an inline "Are you sure? / Cancel" confirmation — native browser `confirm()` is gone
  5. No buttons overlap in the bottom-right corner of the dashboard
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure | v1.0 | 3/3 | Complete | 2026-04-02 |
| 2. New Sources | v1.0 | 4/4 | Complete | 2026-04-03 |
| 3. UI Redesign | v1.0 | 4/4 | Complete | 2026-04-03 |
| 4. UI Polish | v1.0 | 3/3 | Complete | 2026-04-05 |
| 5. Improve UI/UX | v1.0 | 3/3 | Complete | 2026-04-05 |
| 6. Discogs Typeahead | v1.1 | 0/2 | Planned | - |
| 7. Image Priority + Scan Fix | v1.1 | 0/? | Not started | - |
| 8. Brand Font Upgrade | v1.1 | 0/? | Not started | - |
| 9. Email Redesign | v1.1 | 0/? | Not started | - |
| 10. UI Polish | v1.1 | 0/? | Not started | - |
