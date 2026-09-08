# Roadmap: Vinyl Wishlist Manager

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-04-05)
- ✅ **v1.1 UX Polish & Album Selection** — Phases 6–12 (shipped 2026-04-12)
- ✅ **v1.2 Signal Intelligence & Notifications** — Phases 13–15 (shipped 2026-04-14)
- ✅ **v1.3 Visual Overhaul** — Phases 16–19 (shipped 2026-04-18)
- ✅ **v1.4 Quality & Gaps** — Phases 20–24 (shipped 2026-04-26)
- ✅ **v1.5 Coverage & Sources** — Phases 25–27 (shipped 2026-04-27)
- 🚧 **v1.6 Public Release** — Phases 28–32 (in progress)

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

<details>
<summary>✅ v1.4 Quality & Gaps (Phases 20–24) — SHIPPED 2026-04-26</summary>

- [x] Phase 20: Cleanup & Config (1/1 plan) — completed 2026-04-18
- [x] Phase 21: Bug Fixes (1/1 plan) — completed 2026-04-26
- [x] Phase 22: Resend Email (1/1 plan) — completed 2026-04-18
- [x] Phase 23: Discogs Release Selection (1/1 plan) — completed 2026-04-26
- [x] Phase 24: Per-Item Notification Thresholds (1/1 plan) — completed 2026-04-26

See archive: `.planning/milestones/v1.4-ROADMAP.md`

</details>

<details>
<summary>✅ v1.5 Coverage & Sources (Phases 25–27) — SHIPPED 2026-04-27</summary>

- [x] Phase 25: eBay Credentials (1/1 plan) — completed 2026-04-26
- [x] Phase 26: Shopify Store Expansion (2/2 plans) — completed 2026-04-26
- [x] Phase 27: Clarity Records Adapter (1/1 plan) — completed 2026-04-26

See archive: `.planning/milestones/v1.5-ROADMAP.md`

</details>

### 🚧 v1.6 Public Release (In Progress)

**Milestone Goal:** Move off Railway, add user authentication, scope data per-user, open the app to others.

#### Phase 28: Infrastructure Migration
**Goal**: App runs reliably on a non-Railway host with auto-deploy from git
**Depends on**: Phase 27
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04
**Success Criteria** (what must be TRUE):
  1. App is reachable on the new host — all pages load, scanner runs
  2. PostgreSQL database is accessible from the new host and data is intact
  3. A git push to main triggers an automatic redeploy within minutes
  4. All env vars (RESEND_API_KEY, eBay creds, DB_URL, API_KEY) are set and the app starts cleanly
**Plans**: 4 plans
  - [x] 28-01-PLAN.md — Container + Fly.io config artifacts (Dockerfile, fly.toml, .dockerignore)
  - [x] 28-02-PLAN.md — Provision Neon Postgres and migrate data from Railway
  - [x] 28-03-PLAN.md — Launch Fly.io app, set secrets, first deploy
  - [x] 28-04-PLAN.md — GitHub Actions auto-deploy on push to main

#### Phase 29: Auth Foundation
**Goal**: Users can sign up, sign in, and stay signed in; all wishlist routes require authentication
**Depends on**: Phase 28
**Requirements**: AUTH-01, AUTH-02, AUTH-03, SEC-01, SEC-03
**Success Criteria** (what must be TRUE):
  1. A new user can create an account with email and password
  2. A returning user can sign in and reach the dashboard
  3. Refreshing the browser keeps the user signed in (session persists)
  4. Visiting any wishlist route while signed out redirects to the login page
  5. Passwords are stored as bcrypt hashes — plaintext never appears in the database
**Plans**: TBD
**UI hint**: yes

#### Phase 30: Data Isolation
**Goal**: Every wishlist item and listing belongs to exactly one user — no data bleeds between accounts
**Depends on**: Phase 29
**Requirements**: DATA-01, DATA-02
**Success Criteria** (what must be TRUE):
  1. User A cannot see or access User B's wishlist items via any route or API endpoint
  2. Listings are scoped to the owning user's wishlist items and are not shared across accounts
  3. The existing single-user dataset is migrated to the owner account without data loss
**Plans**: TBD

#### Phase 31: Auth Expansion
**Goal**: Users can recover access via password reset email and sign in with Google; auth endpoints are rate-limited
**Depends on**: Phase 29
**Requirements**: AUTH-04, AUTH-05, SEC-02
**Success Criteria** (what must be TRUE):
  1. A user who forgot their password receives a reset link via email and can set a new password
  2. A user can sign in via Google OAuth without creating a separate password
  3. Repeated failed sign-in or sign-up attempts are rejected with a rate-limit error
**Plans**: TBD
**UI hint**: yes

#### Phase 32: User Features
**Goal**: Each user has a personal API key for the iOS Shortcut and can share a read-only public link to their wishlist
**Depends on**: Phase 30
**Requirements**: DATA-03, DATA-04
**Success Criteria** (what must be TRUE):
  1. The iOS Shortcut `POST /api/wishlist` call works using the user's personal API key (X-API-Key header)
  2. A user can generate or view their personal API key from the dashboard
  3. A user can enable a public shareable link; opening that link shows a read-only view without requiring sign-in
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
| 20. Cleanup & Config | v1.4 | 1/1 | Complete | 2026-04-18 |
| 21. Bug Fixes | v1.4 | 1/1 | Complete | 2026-04-26 |
| 22. Resend Email | v1.4 | 1/1 | Complete | 2026-04-18 |
| 23. Discogs Release Selection | v1.4 | 1/1 | Complete | 2026-04-26 |
| 24. Per-Item Notification Thresholds | v1.4 | 1/1 | Complete | 2026-04-26 |
| 25. eBay Credentials | v1.5 | 1/1 | Complete | 2026-04-26 |
| 26. Shopify Store Expansion | v1.5 | 2/2 | Complete | 2026-04-26 |
| 27. Clarity Records Adapter | v1.5 | 1/1 | Complete | 2026-04-26 |
| 28. Infrastructure Migration | v1.6 | 4/4 | Complete    | 2026-04-29 |
| 29. Auth Foundation | v1.6 | 0/? | Not started | - |
| 30. Data Isolation | v1.6 | 0/? | Not started | - |
| 31. Auth Expansion | v1.6 | 0/? | Not started | - |
| 32. User Features | v1.6 | 0/? | Not started | - |
