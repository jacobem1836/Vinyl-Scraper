# Phase 29: Auth Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 29-auth-foundation
**Areas discussed:** Session mechanism, Auth library approach, Login/signup page design, Existing data

---

## Session mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Signed cookie sessions | Starlette SessionMiddleware, httpOnly cookie, server-side session read | ✓ |
| JWT in httpOnly cookie | Stateless self-contained token, no DB lookup per request | |
| JWT in localStorage | JS-accessible, XSS risk, SPA pattern — bad fit for SSR | |

**User's choice:** Signed cookie sessions  
**Notes:** Natural fit for Jinja2 SSR.

### Session TTL

| Option | Selected |
|--------|----------|
| 30 days | ✓ |
| 7 days | |
| 24 hours | |

**User's choice:** 30 days

---

## Auth library approach

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal hand-rolled | bcrypt + SessionMiddleware, ~100–150 lines, full control | ✓ |
| fastapi-users | Full-featured library, opinionated schema, significant overhead | |
| authlib | OAuth/OIDC library, better fit for Phase 31 Google OAuth | |

**User's choice:** Minimal hand-rolled  
**Notes:** No auth library — keep it simple and debuggable.

### Phase scope

| Option | Selected |
|--------|----------|
| Save password reset for Phase 31 | ✓ |
| Include password reset in Phase 29 | |

**User's choice:** Phase 31 — matches REQUIREMENTS.md traceability (AUTH-04 → Phase 31).

---

## Login/signup page design

### Page location

| Option | Selected |
|--------|----------|
| Dedicated full pages /login and /signup | ✓ |
| Modal overlay | |
| Inline on homepage | |

**User's choice:** Dedicated full pages  
**Notes:** Centred form layout selected in preview. CRATE wordmark at top, email/password fields, Sign in button, link to Sign up below.

### Page count

| Option | Selected |
|--------|----------|
| Separate /login and /signup pages | ✓ |
| Combined single page with toggle | |

**User's choice:** Separate pages

### Styling

| Option | Selected |
|--------|----------|
| Match existing dark aesthetic | ✓ |
| Minimal functional only | |

**User's choice:** Match existing dark aesthetic — true black, Gothic A1, same inputs/buttons.

---

## Existing data (pre-Phase 30)

### What signed-in users see

| Option | Selected |
|--------|----------|
| See all existing wishlist data | |
| See nothing (empty slate) | ✓ |

**User's choice:** Empty slate — no existing data to carry forward. Fresh start.

### Owner account

| Option | Selected |
|--------|----------|
| Phase 30's responsibility | |
| Create owner account in Phase 29 | |

**User's choice:** No existing data — not applicable. Phase 30 handles all data scoping.

---

## Claude's Discretion

- bcrypt work factor
- Password validation rules
- Error message copy
- Session cookie name and config details
- `next` redirect parameter edge cases

## Deferred Ideas

- Password reset (Phase 31 — AUTH-04)
- Google OAuth (Phase 31 — AUTH-05)
- Rate limiting on auth endpoints (Phase 31 — SEC-02)
- Per-user data scoping (Phase 30 — DATA-01, DATA-02)
