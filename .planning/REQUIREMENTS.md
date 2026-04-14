# Requirements: Vinyl Wishlist Manager — v1.3 Visual Overhaul

**Defined:** 2026-04-14
**Core Value:** Show me the cheapest way to buy the records I want, right now.

## v1.3 Requirements

Visual overhaul milestone. Cohesive aesthetic direction (Warner Music–inspired), typographic hierarchy refresh, and targeted UI consistency fixes. No new features or data model changes.

### Visual Foundation

- [ ] **VIS-01**: True black background (`#000`) replaces near-black across all surfaces
- [ ] **VIS-02**: Custom-styled scrollbars matching palette (track, thumb, hover)
- [ ] **VIS-03**: Warner Music–inspired aesthetic direction applied (palette tweaks, spacing, restraint)

### Typography

- [ ] **TYPO-01**: Font swap to a thinner/crispier typeface for cards and body text
- [ ] **TYPO-02**: Type scale revision — item name rendered larger than price on cards
- [ ] **TYPO-03**: Hierarchy applied consistently across dashboard cards, item detail, and modals

### UI Consistency Fixes

- [ ] **FIX-01**: "Item added, scanning in background" message uses the standard `#toast` primitive (not a separate box)
- [ ] **FIX-02**: Item detail screen placeholder image replaced with the new empty vinyl image asset

## Future Requirements

See `.planning/FUTURE.md` for deferred work (auth, streaming integrations, mobile app + Spine View, notifications expansion, security audit).

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / sign-in | Deferred to dedicated auth milestone (see FUTURE.md) |
| Spotify/Discogs/Apple Music integrations | Depends on auth foundation |
| Mobile app + Spine View | Own milestone; deferred to FUTURE.md |
| New notification types | Dilutes visual theme; defer to v1.4 |
| Security audit | Standalone pass, not a feature milestone |
| Data model changes | This milestone is purely visual |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VIS-01 | Phase 16 | Pending |
| VIS-02 | Phase 16 | Pending |
| VIS-03 | Phase 16 | Pending |
| TYPO-01 | Phase 17 | Pending |
| TYPO-02 | Phase 17 | Pending |
| TYPO-03 | Phase 17 | Pending |
| FIX-01 | Phase 18 | Pending |
| FIX-02 | Phase 18 | Pending |

**Coverage:**
- v1.3 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-14*
