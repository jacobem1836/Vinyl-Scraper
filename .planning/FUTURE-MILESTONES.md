# Future Milestones

High-level plan for milestones after v1.2. Captured 2026-04-12 from ideas dump. Not yet scoped — refine when each comes up for scheduling.

---

## v1.2 — Signal & Polish (current milestone)

Quality pass: filter noise, fix feedback gaps, consistent UI. Scoped separately in `REQUIREMENTS.md` / `ROADMAP.md`.

---

## v1.3 — Media Expansion

**Goal:** Aggregate beyond vinyl. Become the overwhelmed-collector's one place for physical music + merch.

**Candidate features:**
- New item type: CD
- New item type: Cassette/tape
- New item type: Poster
- New item type: Merch (t-shirts, etc.)
- Type-aware scrapers (not every adapter handles every type)
- Type-aware UI: card treatment, filters, default type selector update
- Schema migration for `type` enum expansion
- Relevance filtering needs to know media type

**Why later:** requires schema + adapter rework; v1.2 polish unblocks the UX first.

---

## v1.4 — Identity & Auto-Populate

**Goal:** Stop manual wishlist entry. Pull from the services the user already curates.

**Candidate features:**
- User sign-in (first multi-auth surface)
- Spotify OAuth → import saved albums/artists as wishlist candidates
- Discogs OAuth → import existing wishlist/collection
- Apple Music OAuth → import library
- Reconciliation UI (dedupe imports, confirm before adding)
- Security review for auth surface

**Why later:** needs auth layer; breaks the "single-user personal tool" constraint — decide how to handle that before building.

---

## v1.5 — AI Aggregation + Geographic Expansion

**Goal:** Solve the "too many places to check" problem at scale. AU first, then expand.

**Candidate features:**
- AI-powered search across long-tail sites (no per-site adapter)
- Facebook Marketplace integration
- More AU retailers (local stores, independents)
- Country expansion: US, UK, EU (major retailers per region)
- Per-country shipping cost model (extend current AU landed-cost logic)
- Location-aware result ranking

**Why later:** biggest architectural shift; depends on v1.2 filtering (otherwise AI expands the noise problem).

---

## v1.6 — Mobile App + Spine View

**Goal:** Native mobile experience with a distinctive UI that feels analog.

**Candidate features:**
- Mobile app (iOS first — matches existing Shortcut integration)
- **Spine View:** toggle from grid to shelf view; vertical strips simulating record spines with title/artist written vertically
- Pull-from-shelf animation when opening an item
- Infinite scroll shelf
- Parity with web dashboard for core flows (add, scan-now, deals)

**Why later:** needs stable API surface and v1.2/v1.3 content decisions finalized before investing in native UI.

---

## Parked ideas (not milestone-worthy yet)

- Hover for deal — already exists (v1.1)
- "Where is db?" — not a feature, ask directly

---

*Last updated: 2026-04-12*
