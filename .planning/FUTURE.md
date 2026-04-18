# Future Work

Backlog of ideas deferred from current scope. Promote to a milestone via `/gsd-new-milestone` when ready.

*Last updated: 2026-04-14*

---

## Auth Foundation (prerequisite for streaming/multi-user features)

- User sign-in / accounts
- Session + account management

**Why deferred:** Prerequisite for Spotify/Discogs/Apple Music integrations and multi-user support. Significant architectural shift from single-user personal tool.

---

## Streaming / Third-Party Integrations

*Depends on: Auth Foundation*

- **Spotify sign-in** — auto-populate wishlist from saved albums/artists
- **Discogs sign-in** — auto-add wishlist from Discogs collection/wantlist
- **Apple Music sign-in** — same as Spotify
- Other streaming services (Tidal, YouTube Music, etc.)

---

## Mobile App

*Large scope — own milestone / project.*

- Native mobile app (iOS/Android)
- **Spine View (flip mode)** — shelf view collapsing grid into vertical spines with title/artist written vertically. Infinite scroll. Pull-out-of-shelf animation when tapping a record. Mobile-exclusive feature.

---

## Notifications Expansion

- Additional notification types beyond current back-in-stock + price-drop digest
  - (TBD: new-listing-from-preferred-store? rare-pressing-found? shipping-threshold-met?)
- Per-item notification thresholds (custom % below typical per wishlist item)

---

## Security Audit

Standalone pass — not a feature milestone.

- Review API key handling, rate limiting, input validation
- Audit iOS Shortcut API surface
- Dependency vulnerability scan
- Secrets review (env vars, logs)
