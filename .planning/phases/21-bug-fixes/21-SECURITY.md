---
phase: 21
slug: bug-fixes
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-19
---

# Phase 21 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| None | All changes are client-side static file edits (JS + CSS). No trust boundaries crossed. | N/A |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-21-01 | N/A | static/typeahead.js | accept | Cosmetic spinner visibility change only; no new input paths or data flows | closed |
| T-21-02 | N/A | static/style.css | accept | CSS animation change only; no executable code or user data involved | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-21-01 | T-21-01 | Spinner hide is a cosmetic UI fix to `closeDropdown()` and debounce timer; no input processing, no external data flow, no STRIDE surface. | Jacob Marriott | 2026-04-19 |
| R-21-02 | T-21-02 | CSS keyframe rename and color/direction change to card artwork skeleton animation; purely presentational, no executable code or user data involved. | Jacob Marriott | 2026-04-19 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-19 | 2 | 2 | 0 | gsd-secure-phase (accepted by user) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-19
