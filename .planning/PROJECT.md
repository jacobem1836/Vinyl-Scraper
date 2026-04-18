# Vinyl Wishlist Manager

## What This Is

A personal vinyl record wishlist manager that scrapes multiple stores and marketplaces to track prices and availability for records you want to buy. You add records you're after; it finds them across the web, computes landed costs (including shipping to AU), and alerts you to deals. Accessed via a web dashboard and an iOS Shortcut for quick adds.

The app shipped v1.0 as a polished personal tool, v1.1 sharpened UX with CRATE design system and Discogs typeahead, v1.2 added signal intelligence (relevance filtering, ships_from) and a full notification system, and v1.3 completed a full visual overhaul (true black, Gothic A1 typography, toast unification, wider cards).

## Core Value

Show me the cheapest way to buy the records I want, right now.

## Current Milestone: v1.4 Quality & Gaps

**Goal:** Clear accumulated technical debt and close real feature gaps before building anything new.

**Target features:**
- Remove Clarity dead code + wire eBay keys (makes eBay work in production)
- Fix typeahead spinner bug (outstanding since v1.1)
- Resend email migration (replaces SMTP)
- Manual Discogs release selection (fix wrong artwork/match)
- Image skeleton: diagonal shimmer, much darker
- Per-item notification thresholds (custom % per item)

## Current State

**Latest milestone:** v1.3 Visual Overhaul — shipped 2026-04-18 (Phases 16–19)

Key outcomes:
- True black (#000) palette across all surfaces — dashboard, cards, detail, modals
- Custom 4px translucent-white scrollbars with hover brightening
- Gothic A1 self-hosted font (Light/Regular/Medium) replaces Inter; preloaded
- Item name visibly larger and heavier than price on cards, detail, and modals
- Post-add toast unified with scan toast via `window.showToast()` — no scan panel
- Item detail placeholder swapped to empty vinyl PNG
- Card grid: 3-col max, wider gap, tighter 12px margins

## Next Milestone

*Not yet scoped.* Candidate directions: purchase workflow integration, Clarity Records re-enable, per-item notification thresholds, mobile-first web view, admin/monitoring dashboard. Scope with `/gsd-new-milestone` when ready.

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

**Target features:**
- Album name autofill on add/edit (Discogs typeahead to pin a specific release)
- Fix overlapping buttons (bottom right)
- Fix scan log message ("no artist results" → correct type label)
- Prioritize scraped store images over Discogs fallback
- CRATE brand font upgrade
- Email UI redesign
- UI polish (typography scale, card hierarchy, focus states, button states, responsive grid, color contrast)

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
- ✓ **SRC-06**: Source-agnostic adapter registry — v1.0
- ✓ **SRC-01**: eBay AU Browse API adapter — v1.0
- ✓ **SRC-02**: Discrepancy Records AU scraper — v1.0
- ✓ **SRC-03**: Clarity Records adapter (disabled pending NXDOMAIN fix) — v1.0
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

- ✓ **NOTIF-01**: Back-in-stock detection (prev_is_in_stock snapshot, _back_in_stock helper) — v1.2
- ✓ **NOTIF-02**: Price-drop detection (pct + USD modes, prev_price snapshot, _price_dropped helper) — v1.2
- ✓ **NOTIF-03**: Cooldown deduplication (last_notified_at, _within_cooldown gate) — v1.2
- ✓ **NOTIF-04**: Digest email aggregation (send_digest_email, collect-then-dispatch scheduler) — v1.2
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

### Active

- [ ] **BUG-T4**: Fix typeahead spinner not clearing after result select or type-change
- [ ] **CLEAN-T2**: Remove dead Clarity Records code (clarity.py + registry entry)
- [ ] **CFG-T1**: Wire eBay developer keys/config so eBay adapter works in production
- [ ] **EMAIL-T5**: Migrate SMTP email → Resend API
- [ ] **UI-T6**: Image loading skeleton — diagonal shimmer, much darker
- [ ] **DISC-T3**: Manual Discogs release selection on item detail page
- [ ] **NOTIF-F1**: Per-item notification thresholds (custom % below typical per wishlist item)

### Out of Scope

- User accounts / multi-user support — personal tool, single user
- Mobile app — iOS Shortcut handles mobile add; web is desktop-first
- Auction bidding or purchasing — discovery only, not transactional
- Clarity Records (clarityrecords.com.au) — NXDOMAIN; re-enable when site recovers

## Context

- **Stack:** Python 3.14, FastAPI, SQLAlchemy 2, Jinja2, pg8000/PostgreSQL (Railway), aiosqlite (dev), APScheduler, httpx
- **Adapters:** discogs, shopify, ebay, discrepancy, juno, bandcamp (6 active; clarity disabled NXDOMAIN)
- **Design system:** CRATE — CSS custom properties, true black palette (#000), white accent, Gothic A1 font, 44px touch targets, WCAG AA contrast
- **Database:** `listings` composite unique on `(wishlist_item_id, url)`; SQLite migration rebuilds table if legacy `UNIQUE (url)` inline constraint detected
- **iOS Shortcut:** Hits `POST /api/wishlist` with `X-API-Key` header; backward compatible
- **Codebase:** ~5,530 LOC (Python + HTML + CSS)

## Constraints

- **Compatibility:** iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) must not break
- **Deployment:** Railway + PostgreSQL; no infrastructure changes unless clearly better
- **Scraping:** Respect robots.txt / rate limits; scraper sources must be feasible (public listings, no login required)
- **Solo project:** No team overhead; keep architecture simple

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Expand beyond Discogs + Shopify | User wants more coverage | 6 adapters active; Clarity dropped NXDOMAIN |
| UI direction: Spotify-like, record-art-forward | Less AI-feel, more personal | CRATE design system, card grid, dark palette ✓ Good |
| Async scan decoupling via BackgroundTasks | Instant response for iOS Shortcut | PERF-01 validated ✓ Good |
| TTLCache maxsize=1 for dashboard | Single endpoint, 5-min TTL | Works well; invalidated on mutation ✓ Good |
| Per-adapter semaphores | Different rate limits per source | Cleaner than global semaphore ✓ Good |
| Discogs release endpoint for artwork | Higher res than search thumb | Full-res cover art on all items ✓ Good |
| `UNIQUE (wishlist_item_id, url)` on listings | Same URL valid for multiple wishlist items | Fixes IntegrityError on cross-item scans ✓ Good |
| SQLite table rebuild migration | Inline UNIQUE can't be dropped otherwise | Handles legacy dev DB automatically ✓ Good |
| Clarity Records disabled | NXDOMAIN on clarityrecords.com.au | Re-enable when site recovers ⚠ Revisit |
| Relevance threshold global (not per-item) | Simpler config, avoids per-row settings bloat | Works for single user; revisit if items diverge ⚠ Revisit |
| Collect-then-dispatch for digest | One email per scan run, not per event | Reduces alert fatigue; tested with 9 unit tests ✓ Good |
| Cooldown is global hours (not per-item) | Solo tool; consistent behaviour simpler | May need per-item control as wishlist grows — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-18 — v1.4 milestone started (Quality & Gaps)*
