# Requirements: Vinyl Wishlist Manager

**Defined:** 2026-04-18
**Core Value:** Show me the cheapest way to buy the records I want, right now.

## v1.4 Requirements

Requirements for the Quality & Gaps milestone. Each maps to roadmap phases.

### Cleanup

- [ ] **CLEAN-01**: Remove `clarity.py` and its registry entry — dead code, NXDOMAIN confirmed
- [ ] **CFG-01**: eBay developer credentials wired via env vars so eBay adapter authenticates in production

### Bug Fixes

- [ ] **BUG-03**: Typeahead spinner clears after result select and after type dropdown change
- [ ] **UI-07**: Image loading skeleton uses diagonal shimmer (dark, top-left → bottom-right sweep), not glow/pulse

### Email

- [ ] **EMAIL-04**: Deal alert emails sent via Resend API, replacing SMTP

### Discogs Release Selection

- [ ] **DISC-01**: User can search Discogs releases from item detail page
- [ ] **DISC-02**: User can select a release to pin it to a wishlist item
- [ ] **DISC-03**: Scans and artwork use pinned Discogs release ID when set, instead of auto-search

### Notifications

- [ ] **NOTIF-05**: User can set a custom notification threshold (% below typical) per wishlist item
- [ ] **NOTIF-06**: Per-item threshold overrides the global threshold when set

## Future Requirements

Deferred to a future milestone. Tracked but not in current roadmap.

### Sources

- **SRC-NEW**: Replace Clarity Records with a working AU vinyl store (candidates: Wax Museum, Heartland, Vinyl Revival)

### Streaming / Third-Party Integrations

- **AUTH-01**: User sign-in / session management (prerequisite for streaming integrations)
- **STREAM-01**: Spotify sign-in — auto-populate wishlist from saved albums/artists
- **STREAM-02**: Discogs sign-in — auto-add from Discogs wantlist/collection
- **STREAM-03**: Apple Music sign-in — same as Spotify

### Mobile

- **MOB-01**: Native mobile app (iOS/Android)
- **MOB-02**: Spine View (flip mode) — shelf view collapsing grid into vertical spines

### Notifications Expansion

- **NOTIF-07**: New-listing-from-preferred-store notification type
- **NOTIF-08**: Rare-pressing detection notification type
- **NOTIF-09**: Shipping-threshold-met notification type

### Infrastructure

- **SEC-01**: Security audit — API key handling, rate limiting, input validation, dependency scan

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / multi-user | Personal tool, single user — significant architectural shift |
| Auction bidding or purchasing | Discovery only, not transactional |
| Mobile app (this milestone) | Large scope — own milestone/project |
| Auth / streaming integrations | Depends on auth foundation — deferred |
| Physical media extension (CDs, cassettes) | Vinyl-focused for now |
| AI web scraping | Not needed — existing adapters work well |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLEAN-01 | Phase 20 | Pending |
| CFG-01 | Phase 20 | Pending |
| BUG-03 | Phase 21 | Pending |
| UI-07 | Phase 21 | Pending |
| EMAIL-04 | Phase 22 | Pending |
| DISC-01 | Phase 23 | Pending |
| DISC-02 | Phase 23 | Pending |
| DISC-03 | Phase 23 | Pending |
| NOTIF-05 | Phase 24 | Pending |
| NOTIF-06 | Phase 24 | Pending |

**Coverage:**
- v1.4 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-18*
*Last updated: 2026-04-18 — traceability populated after v1.4 roadmap creation*
