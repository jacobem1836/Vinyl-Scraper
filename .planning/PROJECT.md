# Vinyl Wishlist Manager

## What This Is

A personal vinyl record wishlist manager that scrapes multiple stores and marketplaces to track prices and availability for records you want to buy. You add records you're after; it finds them across the web, computes landed costs (including shipping to AU), and alerts you to deals. Accessed via a web dashboard and an iOS Shortcut for quick adds.

## Core Value

Show me the cheapest way to buy the records I want, right now.

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

### Active

- [ ] Performance — page load, search, and bulk import are noticeably slow
- [ ] UI redesign — Spotify-like aesthetic: record artwork as the hero, minimal/uncluttered, less "AI-generated"
- [ ] Expand scraping sources — Juno Records, Bandcamp, eBay AU; Australian stores (Clarity, Egg, etc.) where feasible
- [ ] Polish for daily use and shareable quality

### Out of Scope

- User accounts / multi-user support — personal tool, single user
- Mobile app — iOS Shortcut handles mobile add; web is desktop-first
- Auction bidding or purchasing — discovery only, not transactional

## Context

- **Stack:** Python 3, FastAPI, SQLAlchemy, Jinja2 templates, pg8000/PostgreSQL, APScheduler, deployed on Railway
- **Scraping architecture:** Source adapters (`app/services/discogs.py`, `app/services/shopify.py`) return standardized listing dicts; scanner coordinates them concurrently
- **Performance issues:** No DB query caching, `_enrich_item()` called per-item on every dashboard load, scan runs synchronously on item add before returning response
- **UI:** Server-side rendered Jinja2 templates; no JS framework; current look is generic/bootstrap-ish
- **iOS Shortcut:** Hits `POST /api/wishlist` with `X-API-Key` header; must remain backward compatible
- **Codebase map:** `.planning/codebase/` contains full analysis (CONCERNS.md has detailed perf notes)

## Constraints

- **Compatibility:** iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) must not break
- **Deployment:** Railway + PostgreSQL; no infrastructure changes unless clearly better
- **Scraping:** Respect robots.txt / rate limits; scraper sources must be feasible (public listings, no login required)
- **Solo project:** No team overhead; keep architecture simple

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Expand beyond Discogs + Shopify | User wants more coverage; Juno, Bandcamp, eBay, AU stores are targets | — Pending |
| UI direction: Spotify-like, record-art-forward | Feels less AI, more personal and visually engaging | — Pending |
| Performance fix approach | TBD — caching, async scan decoupling, or query optimization | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-02 after initialization*
