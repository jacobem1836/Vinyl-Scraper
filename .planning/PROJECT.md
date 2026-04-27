# Vinyl Wishlist Manager

## What This Is

A personal vinyl record wishlist manager that scrapes multiple stores and marketplaces to track prices and availability for records you want to buy. You add records you're after; it finds them across the web, computes landed costs (including shipping to AU), and alerts you to deals. Accessed via a web dashboard and an iOS Shortcut for quick adds.

The app shipped v1.0 as a polished personal tool; v1.1 sharpened UX with CRATE design system and Discogs typeahead; v1.2 added signal intelligence (relevance filtering, ships_from) and a full notification system; v1.3 completed a full visual overhaul (true black, Gothic A1 typography, toast unification, wider cards); v1.4 cleared technical debt (dead code, Resend email, Discogs release pinning, per-item thresholds); v1.5 expanded source coverage to 12 Shopify stores, working eBay, and a new Clarity Records scraper.

## Core Value

Show me the cheapest way to buy the records I want, right now.

## Current State

**Latest milestone:** v1.5 Coverage & Sources — shipped 2026-04-27 (Phases 25–27)

Key outcomes (v1.5):
- eBay credentials documented + startup warning; adapter verified returning AU vinyl listings (Phase 25)
- 5 AU Shopify stores added (Wax Museum, Red Eye, Rockaway, Happy Valley, Rare Records) — 6 → 12 stores total including Heartland fallback (Phase 26)
- Clarity Records BigCommerce HTML scraper (`clarity.py`, 131 lines) re-implemented and registered as 7th adapter (Phase 27)
- 7 total adapters active: discogs, shopify (12 stores), ebay, discrepancy, juno, bandcamp, clarity

## Current Milestone: v1.6 Public Release

**Goal:** Move off Railway, add user authentication, and open the app to other users with their own wishlists.

**Target features:**
- Infrastructure migration (Railway → free/cheap alternative)
- User sign-up / sign-in / session management
- Per-user wishlists (data isolation by user)
- Security hardening for new auth surfaces

<details>
<summary>Prior milestone brief: v1.4 Quality & Gaps</summary>

**Goal:** Clear accumulated technical debt and close real feature gaps before building anything new.

**Delivered:**
- Dead Clarity code removed; eBay config hardened with diagnostic log (Phase 20)
- Typeahead spinner clearing fixed; image skeleton replaced with diagonal dark shimmer (Phase 21)
- SMTP email migrated to Resend API (Phase 22)
- Manual Discogs release selection + pinning on item detail (Phase 23)
- Per-item notification thresholds with global fallback (Phase 24)

</details>

<details>
<summary>Prior milestone brief: v1.3 Visual Overhaul</summary>

**Goal:** Cohesive visual refresh: Warner Music–inspired aesthetic, true black palette, typography hierarchy with item name > price, custom scrollbars, and targeted consistency fixes.

**Delivered:**
- True black palette + custom scrollbars + Warner Music aesthetic (Phase 16)
- Gothic A1 font swap + name > price hierarchy (Phase 17)
- Toast unification + empty vinyl placeholder (Phase 18)
- Card layout expansion — 3-col max, wider gap (Phase 19)

</details>

<details>
<summary>Prior milestone brief: v1.2 Signal Intelligence & Notifications</summary>

**Goal:** Reduce listing noise with relevance filtering and geographic enrichment, and add a full alert system for back-in-stock and price-drop events delivered as a single digest email per scan run.

**Delivered:**
- Relevance scoring + digital listing filter (Phase 13)
- ships_from enrichment from Discogs marketplace API (Phase 13)
- Toast feedback consistency + modal type default (Phase 14)
- Back-in-stock, price-drop detection, cooldown, digest email (Phase 15)

</details>

<details>
<summary>Prior milestone brief: v1.1 UX Polish & Album Selection</summary>

**Goal:** Sharpen the UI with targeted fixes, add Discogs typeahead for precise album identification, and redesign email notifications — all designed using the full design tool stack.

**Delivered:**
- Discogs typeahead + pinned release scanning
- Store image priority with Discogs/placeholder fallback
- CRATE brand font upgrade
- Email UI redesign
- UI polish (typography, card hierarchy, focus states, responsive grid)

</details>

## Requirements

### Validated

- ✓ Add wishlist items (album, artist, label, or subject) via web form and iOS Shortcut API — existing
- ✓ Scrape Discogs for matching listings — existing
- ✓ Scrape Shopify-based stores for matching listings — existing
- ✓ Compute landed cost (price + estimated shipping to AU) — existing
- ✓ Dashboard showing best price, typical price, top listings per item — existing
- ✓ Background scheduled scanning (every 6 hours) — existing
- ✓ Email alerts for deals below typical price threshold — existing
- ✓ Bulk import via text file + CLI script — existing
- ✓ Deployed to Railway with PostgreSQL — existing
- ✓ **PERF-01–04**: Scan decoupled from HTTP, N+1 fixed, TTL cache, rate-limit semaphores — v1.0
- ✓ **SRC-01**: eBay AU Browse API adapter — v1.0
- ✓ **SRC-02**: Discrepancy Records AU scraper — v1.0
- ✓ **SRC-04**: Juno Records scraper — v1.0
- ✓ **SRC-05**: Bandcamp vinyl scraper — v1.0
- ✓ **UI-01**: Bootstrap removed; 545-line hand-rolled CSS design system (CRATE) — v1.0
- ✓ **UI-02**: Card grid with record artwork as visual hero — v1.0
- ✓ **UI-03**: Artwork fetched via Discogs release endpoint, served through `/api/artwork` proxy — v1.0
- ✓ **UI-04**: Landed cost breakdown with AUD FX conversion — v1.0
- ✓ **UI-05**: Dark palette consistently applied — v1.0
- ✓ **UI-06**: iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) preserved — v1.0
- ✓ **TYPE-01–04**: Discogs typeahead + pinned release scanning — v1.1
- ✓ **IMG-01–02**: Store image priority with Discogs/placeholder fallback — v1.1
- ✓ **BUG-01**: Overlapping buttons fix — v1.1
- ✓ **BUG-02**: Scan log type label fix — v1.1
- ✓ **FONT-01**: Self-hosted CRATE brand font — v1.1
- ✓ **EMAIL-01–03**: Redesigned deal alert email (inline CSS, CRATE aesthetic) — v1.1
- ✓ **UIP-01–10 / D-01–D-18**: UI polish — typography, card system, palette, states, responsive grid — v1.1
- ✓ **NOTIF-01**: Back-in-stock detection — v1.2
- ✓ **NOTIF-02**: Price-drop detection — v1.2
- ✓ **NOTIF-03**: Cooldown deduplication — v1.2
- ✓ **NOTIF-04**: Digest email aggregation — v1.2
- ✓ **SIG-01**: Relevance scoring + digital listing filter — v1.2
- ✓ **SIG-02**: ships_from enrichment from Discogs marketplace API — v1.2
- ✓ **UX-01**: Consistent toast feedback primitive + modal type default — v1.2
- ✓ **VIS-01**: True black background (#000) across all surfaces — v1.3
- ✓ **VIS-02**: Custom-styled scrollbars matching palette — v1.3
- ✓ **VIS-03**: Warner Music–inspired aesthetic direction — v1.3
- ✓ **TYPO-01**: Gothic A1 self-hosted font swap for cards and body text — v1.3
- ✓ **TYPO-02**: Item name larger than price on cards — v1.3
- ✓ **TYPO-03**: Type hierarchy across dashboard, item detail, and modals — v1.3
- ✓ **FIX-01**: Post-add toast unified with standard #toast primitive — v1.3
- ✓ **FIX-02**: Item detail placeholder swapped to empty vinyl PNG — v1.3
- ✓ **CLEAN-01**: Dead Clarity adapter code and registry entry removed — v1.4
- ✓ **CFG-01**: eBay config hardened with startup diagnostic log — v1.4
- ✓ **BUG-03**: Typeahead spinner clears on result select and type-change — v1.4
- ✓ **UI-07**: Image skeleton uses diagonal dark shimmer (not glow/pulse) — v1.4
- ✓ **EMAIL-04**: Deal alert emails sent via Resend API; SMTP no longer required — v1.4
- ✓ **DISC-01**: User can search Discogs releases from item detail — v1.4
- ✓ **DISC-02**: User can select a release to pin it to a wishlist item — v1.4
- ✓ **DISC-03**: Scans and artwork use pinned Discogs release ID when set — v1.4
- ✓ **NOTIF-05**: User can set a custom notification threshold per wishlist item — v1.4
- ✓ **NOTIF-06**: Per-item threshold overrides global threshold when set — v1.4
- ✓ **SRC-eBay**: eBay credentials documented + startup warning; adapter verified returning AU vinyl listings — v1.5
- ✓ **SRC-Wax**: Wax Museum Records added to Shopify STORES, returning listings — v1.5
- ✓ **SRC-RedEye**: Red Eye Records added to Shopify STORES, returning listings — v1.5
- ✓ **SRC-Rockaway**: Rockaway Records added (URL corrected to rockaway.com.au) — v1.5
- ✓ **SRC-HappyValley**: Happy Valley Shop added (URL corrected to happyvalleyshop.com) — v1.5
- ✓ **SRC-Rare**: Rare Records added to Shopify STORES, returning listings — v1.5
- ✓ **SRC-Heartland**: Heartland Records via products.json fallback path — v1.5
- ✓ **SRC-Clarity**: Clarity Records BigCommerce HTML scraper (`clarity.py`) registered as 7th adapter — v1.5

### Active

- [ ] Infrastructure migrated off Railway to a free/cheap host
- [ ] User sign-up and sign-in with email/password
- [ ] Session management (persists across browser refresh)
- [ ] Per-user wishlist data isolation
- [ ] Security hardening for auth surfaces

### Out of Scope

- User accounts / multi-user support — personal tool, single user
- Mobile app — iOS Shortcut handles mobile add; web is desktop-first
- Auction bidding or purchasing — discovery only, not transactional

## Context

- **Stack:** Python 3.11+, FastAPI, SQLAlchemy 2, Jinja2, pg8000/PostgreSQL (Railway), aiosqlite (dev), APScheduler, httpx
- **Adapters:** discogs, shopify (12 stores), ebay, discrepancy, juno, bandcamp, clarity (7 active)
- **Design system:** CRATE — CSS custom properties, true black palette (#000), white accent, Gothic A1 font, 44px touch targets, WCAG AA contrast
- **Database:** `listings` composite unique on `(wishlist_item_id, url)`; SQLite migration rebuilds table if legacy `UNIQUE (url)` inline constraint detected
- **iOS Shortcut:** Hits `POST /api/wishlist` with `X-API-Key` header; backward compatible
- **Codebase:** ~5,700 LOC (Python + HTML + CSS)

## Constraints

- **Compatibility:** iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) must not break
- **Deployment:** Railway + PostgreSQL; no infrastructure changes unless clearly better
- **Scraping:** Respect robots.txt / rate limits; scraper sources must be feasible (public listings, no login required)
- **Solo project:** No team overhead; keep architecture simple

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Expand beyond Discogs + Shopify | User wants more coverage | 7 adapters, 12 Shopify stores active ✓ Good |
| UI direction: Spotify-like, record-art-forward | Less AI-feel, more personal | CRATE design system, card grid, dark palette ✓ Good |
| Async scan decoupling via BackgroundTasks | Instant response for iOS Shortcut | PERF-01 validated ✓ Good |
| TTLCache maxsize=1 for dashboard | Single endpoint, 5-min TTL | Works well; invalidated on mutation ✓ Good |
| Per-adapter semaphores | Different rate limits per source | Cleaner than global semaphore ✓ Good |
| Discogs release endpoint for artwork | Higher res than search thumb | Full-res cover art on all items ✓ Good |
| `UNIQUE (wishlist_item_id, url)` on listings | Same URL valid for multiple wishlist items | Fixes IntegrityError on cross-item scans ✓ Good |
| SQLite table rebuild migration | Inline UNIQUE can't be dropped otherwise | Handles legacy dev DB automatically ✓ Good |
| Collect-then-dispatch for digest | One email per scan run, not per event | Reduces alert fatigue; tested with 9 unit tests ✓ Good |
| Cooldown is global hours (not per-item) | Solo tool; consistent behaviour simpler | May need per-item control as wishlist grows — Pending |
| Heartland: products.json not suggest.json | suggest.json disabled on their Shopify store | Works; client-side filter is acceptable for targeted queries ✓ Good |
| Clarity page 1 only | Targeted queries return best results first | Sufficient for artist/album queries; extend if coverage proves lacking ⚠ Revisit |
| Relevance threshold global (not per-item) | Simpler config, avoids per-row settings bloat | Works for single user; revisit if items diverge ⚠ Revisit |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-27 after v1.6 milestone started*
