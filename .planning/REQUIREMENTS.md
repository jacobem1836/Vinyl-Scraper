# Requirements — v1.2 Signal & Polish

**Milestone goal:** Fix the quality issues killing daily usefulness — filter noisy/irrelevant results, give consistent feedback on every action, finish the UI polish arc, and close out security hygiene.

**Status:** Defined 2026-04-13. Roadmap created 2026-04-12.

---

## v1.2 Requirements

### Signal / Filtering

- [ ] **FILTER-01**: User sees only listings scoring above a relevance threshold (title/artist fuzzy match) when viewing an item
- [ ] **FILTER-02**: User sees no digital-only listings (MP3, FLAC, "File" format, Bandcamp digital) in scan results
- [ ] **FILTER-03**: User sees accurate seller location on Discogs listings

### Feedback / UI Consistency

- [ ] **FEEDBACK-01**: User sees spinner + toast when clicking scan-now on an individual item
- [ ] **FEEDBACK-02**: "Item added, scanning…" dialog matches CRATE design system (reuses same toast/modal primitive)
- [ ] **FEEDBACK-03**: Add-item modal opens with type defaulted to "album"

### Notifications

- [ ] **NOTIF-01**: User receives back-in-stock alert when a listing transitions out-of-stock → in-stock
- [ ] **NOTIF-02**: User receives price-drop alert when a listing's price drops vs prior scan
- [ ] **NOTIF-03**: Notifier deduplicates repeat events within a cool-down window (no spam loops)
- [ ] **NOTIF-04**: Multiple events for one scan collapse into a single digest email

### Branding

- [ ] **BRAND-01**: Site logo updated in nav bar
- [ ] **BRAND-02**: Email logo matches site logo (CID embed or absolute URL)
- [ ] **BRAND-03**: Custom scrollbar styling applied across site (Firefox `scrollbar-*` + Webkit `::-webkit-scrollbar`)

### Security

- [ ] **SEC-01**: API key comparison uses `hmac.compare_digest` (timing-safe)
- [ ] **SEC-02**: `pip-audit` run; vulnerable dependencies upgraded
- [ ] **SEC-03**: Web mutation routes have CSRF protection
- [ ] **SEC-04**: Error/log output scrubbed of secrets and PII
- [ ] **SEC-05**: Rate limiting on public-facing endpoints reviewed

---

## Future Requirements (deferred to later milestones)

See `.planning/FUTURE-MILESTONES.md` for the full roadmap. High level:

- **v1.3 Media Expansion** — CDs, tapes, posters, merch (schema + adapter rework)
- **v1.4 Identity & Auto-Populate** — Spotify / Discogs / Apple Music OAuth import
- **v1.5 AI Aggregation + Geography** — AI-powered search, Facebook Marketplace, country expansion
- **v1.6 Mobile App + Spine View** — native iOS, shelf-view UI

---

## Out of Scope (this milestone)

- New media types — deferred to v1.3
- User accounts / auth / OAuth — deferred to v1.4
- AI-powered scraping — deferred to v1.5
- Mobile app / Spine View — deferred to v1.6
- ML-based relevance (embeddings, etc.) — overkill; fuzzy token matching is sufficient
- Real-time push notifications — email-only this milestone
- Per-item notification preferences — global preferences only for now
- Hover-for-deal feature — already exists (v1.1)

---

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| FILTER-01 | Phase 13 | Pending |
| FILTER-02 | Phase 13 | Pending |
| FILTER-03 | Phase 13 | Pending |
| FEEDBACK-01 | Phase 14 | Pending |
| FEEDBACK-02 | Phase 14 | Pending |
| FEEDBACK-03 | Phase 14 | Pending |
| NOTIF-01 | Phase 15 | Pending |
| NOTIF-02 | Phase 15 | Pending |
| NOTIF-03 | Phase 15 | Pending |
| NOTIF-04 | Phase 15 | Pending |
| BRAND-01 | Phase 16 | Pending |
| BRAND-02 | Phase 16 | Pending |
| BRAND-03 | Phase 16 | Pending |
| SEC-01 | Phase 17 | Pending |
| SEC-02 | Phase 17 | Pending |
| SEC-03 | Phase 17 | Pending |
| SEC-04 | Phase 17 | Pending |
| SEC-05 | Phase 17 | Pending |

---
*Last updated: 2026-04-12 — phase mappings added (v1.2 roadmap)*
