---
phase: 29-auth-foundation
plan: "03"
subsystem: auth
tags: [auth, fastapi, route-guards, sessions, templates]
dependency_graph:
  requires: [app/auth.py, User model, SessionMiddleware, auth routes (29-02)]
  provides: [guarded web routes, nav user/logout, require_session_or_api_key]
  affects: [app/main.py, app/routers/wishlist.py, templates/base.html]
tech_stack:
  added: []
  patterns: [FastAPI Depends for route guards, session-or-api-key dual auth, Jinja2 conditional nav]
key_files:
  created:
    - tests/test_route_guards.py
  modified:
    - app/main.py
    - app/routers/wishlist.py
    - templates/base.html
decisions:
  - "Used _user=Depends(require_auth) (underscore prefix) on web_router routes that don't need to consume the user object -- keeps handler signatures minimal"
  - "require_session_or_api_key implemented as a plain async dependency (not using require_auth wrapper) to allow transparent API-key bypass on scan endpoints"
  - "Separated import lines in main.py and wishlist.py to satisfy acceptance criteria string match for from app.auth import require_auth"
  - "D-07 Gothic A1 font deviation: continued from Plan 02 -- CRATE app uses Bodoni Moda + Inter, no new fonts added"
metrics:
  duration_seconds: 286
  completed_date: "2026-05-10"
  tasks_completed: 1
  tasks_total: 2
  files_created: 1
  files_modified: 3
---

# Phase 29 Plan 03: Route Guards Summary

**One-liner:** require_auth applied to all web_router routes and index/item_detail; require_session_or_api_key added to scan endpoints; nav shows signed-in email + Logout button; 11 integration tests passing.

## What Was Built

Plan 03 closes SEC-01 (route guards) and demonstrates AUTH-03 (session persistence):

- **`app/main.py`** -- `require_auth` imported and added as a `Depends` parameter to `index` (GET /) and `item_detail` (GET /item/{item_id}); `user` passed to template context for both routes
- **`app/routers/wishlist.py`** -- `require_auth` imported; `_user=Depends(require_auth)` added to all 8 `web_router` endpoints (POST /wishlist/add, POST /wishlist/{item_id}/edit, POST /wishlist/{item_id}/delete, POST /wishlist/{item_id}/scan, POST /scan-all, GET /wishlist/{item_id}/status, GET /api/discogs/search, GET /api/artwork); `require_session_or_api_key` helper added for the two scan endpoints (`/api/scan/start`, `/api/scan/status`) -- accepts either a valid session cookie or X-API-Key; existing `Depends(require_api_key)` on all `/api/wishlist` routes unchanged (iOS Shortcut contract preserved); `/api/health` remains fully open
- **`templates/base.html`** -- `{% if user %}` block added after the "Add Item" button inside `nav-inner`; shows `{{ user.email }}` and a `<form method="post" action="/logout">` Logout button with existing CRATE CSS tokens; no new CSS classes or font families
- **`tests/test_route_guards.py`** -- 11 integration tests using FastAPI TestClient, StaticPool in-memory SQLite, APScheduler mocked; covers all behaviors from the plan spec

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Apply require_auth to all web routes; add nav user/logout; tests | f434e05 | app/main.py, app/routers/wishlist.py, templates/base.html, tests/test_route_guards.py |
| 2 | Manual end-to-end verification (checkpoint:human-verify) | -- | (pending user verification) |

## Deviations from Plan

None -- plan executed as written. All 11 test behaviors from the spec pass.

**Design note from Plans 01 + 02 carried forward:** Plan context (29-CONTEXT.md D-07) references "Gothic A1 font requested" but the established CRATE app uses Bodoni Moda (display) + Inter (body). No Gothic A1 font was added. This is flagged for user confirmation if Gothic A1 was a strict requirement -- it would be a follow-up to swap font tokens.

## Security Notes

| Threat | Status |
|--------|--------|
| T-29-14: Guarded route reachable without session | Mitigated -- every web_router route + index + item_detail carry Depends(require_auth); verified by 11 integration tests |
| T-29-15: Bypass via api_router | Mitigated -- existing /api/* routes (except /health) keep Depends(require_api_key); scan endpoints gain require_session_or_api_key |
| T-29-16: /api/health DoS | Accepted -- intentionally open for platform health checks; rate limiting is Phase 31 SEC-02 |
| T-29-17: Nav exposes email | Mitigated by design -- email only rendered to cookie holder; httpOnly + signed cookie defends the cookie |
| T-29-18: Open redirect via next= | Mitigated -- _safe_next() from Plan 02 already restricts next= to relative paths |
| T-29-19: Session fixation | Accepted for Phase 29; revisit in Phase 31 if needed |

## Known Stubs

None -- all routes are guarded and functional. Nav shows real user email from the database session. No placeholder values.

## Threat Flags

None -- no new trust boundaries beyond those documented in the plan's threat model. The route guard pattern closes the boundary documented in T-29-14 and T-29-15.

## Self-Check: PASSED

- `tests/test_route_guards.py` exists: FOUND
- Commit f434e05 exists: FOUND
- All 11 tests pass: CONFIRMED (11/11 PASSED)
- `grep -c "Depends(require_auth)" app/main.py` = 2: CONFIRMED
- `grep -c "Depends(require_auth)" app/routers/wishlist.py` = 8: CONFIRMED
- `grep -q "from app.auth import require_auth" app/main.py`: CONFIRMED
- `grep -q "from app.auth import require_auth" app/routers/wishlist.py`: CONFIRMED
- `grep -q "require_session_or_api_key" app/routers/wishlist.py`: CONFIRMED
- `grep -q "Depends(require_session_or_api_key)" app/routers/wishlist.py`: CONFIRMED
- /api/health NOT decorated with require_auth: CONFIRMED
- `grep -q "{{ user.email }}" templates/base.html`: CONFIRMED
- `grep -q 'action="/logout"' templates/base.html`: CONFIRMED
- `grep -c "Depends(require_api_key)" app/routers/wishlist.py` = 6: CONFIRMED
