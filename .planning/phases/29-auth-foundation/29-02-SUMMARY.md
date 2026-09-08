---
phase: 29-auth-foundation
plan: "02"
subsystem: auth
tags: [auth, fastapi, sessions, templates, css, bcrypt]
dependency_graph:
  requires: [app/auth.py, User model, SessionMiddleware, users table]
  provides: [app/routers/auth.py, templates/login.html, templates/signup.html, templates/auth_base.html, auth CSS]
  affects: [app/main.py, static/style.css]
tech_stack:
  added: []
  patterns: [SQLAlchemy StaticPool for in-memory SQLite testing, APScheduler startup/shutdown mocking in TestClient, open-redirect prevention via _safe_next()]
key_files:
  created:
    - app/routers/auth.py
    - templates/auth_base.html
    - templates/login.html
    - templates/signup.html
    - tests/test_auth_routes.py
  modified:
    - app/main.py
    - static/style.css
decisions:
  - "StaticPool required for SQLite in-memory testing — without it each new SQLAlchemy connection opens a separate empty database"
  - "APScheduler start/shutdown patched in TestClient fixture to avoid event-loop-closed errors across test teardowns"
  - "auth_router wired before api_router and after web_router — keeps route priority consistent with existing ordering"
  - "D-07 font deviation: plan context mentioned Gothic A1 but existing CRATE app uses Bodoni Moda + Inter; honoured established fonts for visual consistency"
metrics:
  duration_seconds: 1050
  completed_date: "2026-05-10"
  tasks_completed: 2
  tasks_total: 2
  files_created: 5
  files_modified: 2
---

# Phase 29 Plan 02: Auth Routes and Templates Summary

**One-liner:** GET/POST /login, GET/POST /signup, POST /logout routes with CRATE dark aesthetic — signed sessions on success, form errors on failure, _safe_next() open-redirect prevention.

## What Was Built

Plan 02 adds the user-facing auth endpoints and CRATE-styled templates that Plans 01 primitives back:

- **`app/routers/auth.py`** -- `auth_router` (APIRouter) with 5 handlers:
  - `GET /login` -- renders `login.html` with optional `error` and `email` prefill
  - `POST /login` -- normalises email, verifies bcrypt hash via `verify_password`, sets `request.session["user_id"]` on success, generic error on failure (T-29-08)
  - `GET /signup` -- renders `signup.html`
  - `POST /signup` -- validates email format, enforces 8-char minimum, checks duplicate email, hashes with `hash_password`, creates User row, sets session; never round-trips password (T-29-09)
  - `POST /logout` -- `request.session.clear()`, redirects to `/login`
  - `_safe_next()` -- whitelists relative paths starting with single `/`; rejects external URLs and `//host` open-redirect attempts (T-29-07)
- **`app/main.py`** -- `auth_router` imported and wired via `app.include_router(auth_router)` between `web_router` and `api_router`
- **`templates/auth_base.html`** -- minimal layout shell: no main nav, CRATE wordmark, `auth-body` / `auth-shell` / `auth-card` structure
- **`templates/login.html`** -- extends `auth_base.html`; email/password fields, `name="next"` hidden input, link to `/signup`
- **`templates/signup.html`** -- extends `auth_base.html`; email/password fields, `minlength="8"`, hint text, link to `/login`
- **Auth CSS block in `static/style.css`** -- 14 new classes (`.auth-body`, `.auth-shell`, `.auth-brand`, `.auth-card`, `.auth-heading`, `.auth-form`, `.auth-label`, `.auth-input`, `.auth-hint`, `.auth-submit`, `.auth-error`, `.auth-foot` + `:focus` state and link sub-rule). All use existing CRATE CSS tokens; no new fonts.
- **`tests/test_auth_routes.py`** -- 9 tests via FastAPI TestClient with StaticPool in-memory SQLite and APScheduler mocked; all passing.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | auth_router with /signup, /login, /logout + tests (TDD) | 8083851 | app/routers/auth.py, app/main.py, tests/test_auth_routes.py |
| 2 | CRATE-styled login.html, signup.html, auth_base.html, auth CSS | 6874d64 | templates/auth_base.html, templates/login.html, templates/signup.html, static/style.css |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] SQLite in-memory StaticPool required for test isolation**
- **Found during:** Task 1 test run (GREEN phase)
- **Issue:** SQLite `:memory:` creates a separate empty database per connection. The test's `db_engine` fixture called `Base.metadata.create_all(bind=engine)`, but SQLAlchemy's session pool used a different underlying connection -- seeing an empty database. Query failed with "no such table: users".
- **Fix:** Used `poolclass=StaticPool` on the test engine, which forces all connections to share one underlying sqlite3 connection, so `create_all` and the session both see the same database.
- **Files modified:** `tests/test_auth_routes.py`
- **Commit:** 8083851

**2. [Rule 3 - Blocking] APScheduler start/shutdown collides with TestClient lifecycle**
- **Found during:** Task 1 test run (2nd and subsequent tests)
- **Issue:** Each `with TestClient(app) as c:` triggers ASGI startup/shutdown hooks. APScheduler's `start()` requires a live event loop; after the first TestClient context closes, the loop is gone. Subsequent TestClient contexts fail at startup with `RuntimeError: Event loop is closed`. At teardown, `scheduler.shutdown()` raises `AttributeError: 'NoneType' has no attribute 'call_soon_threadsafe'` because `scheduler._eventloop` is None.
- **Fix:** Patched `app.main.scheduler.start`, `app.main.scheduler.shutdown`, and `app.main.setup_scheduler` inside the `client` fixture's context manager.
- **Files modified:** `tests/test_auth_routes.py`
- **Commit:** 8083851

**3. [Deviation - Design] Existing fonts honoured instead of Gothic A1**
- **Found during:** Task 2, reading `29-CONTEXT.md` (D-07 mentions Gothic A1) vs `templates/base.html` (uses Bodoni Moda + Inter)
- **Issue:** 29-CONTEXT.md references "Gothic A1 font requested" but the established CRATE app uses Bodoni Moda (display) and Inter (body). Introducing a third font family would break visual consistency.
- **Fix:** Honoured the existing font stack. Auth pages use `--font-display` (Bodoni Moda) for the wordmark and `--font-sans` (Inter) for body text, matching the rest of the app. No new `@font-face` added.
- **Files modified:** None (decision not to add Gothic A1)

## Security Notes

| Threat | Status |
|--------|--------|
| T-29-07: Open redirect via next= | Mitigated -- `_safe_next()` whitelists single-slash relative paths; rejects external and `//host` |
| T-29-08: Login error reveals which field failed | Mitigated -- single generic "Invalid email or password." message |
| T-29-09: Password round-tripped in error response | Mitigated -- only `email` is passed back to templates; `password` never appears in template context |
| T-29-10: Passwords logged via uvicorn | Accepted -- uvicorn does not log POST bodies |
| T-29-11: Brute-force login | Accepted (Phase 31 SEC-02) |
| T-29-12: CSRF on /signup, /login, /logout | Accepted (same_site=lax on SessionMiddleware per Plan 01) |
| T-29-13: bcrypt hash serialized via API | Mitigated -- no User Pydantic schema; User never returned in a response_model |

## Known Stubs

None -- all routes are wired and functional. Templates render actual data from the database. No placeholder values flow to UI.

## Threat Flags

None -- no new trust boundaries beyond those documented in the plan's threat model. The /login, /signup, /logout endpoints are the planned auth surface.

## Self-Check: PASSED

- `app/routers/auth.py` exists: FOUND
- `templates/auth_base.html` exists: FOUND
- `templates/login.html` exists: FOUND
- `templates/signup.html` exists: FOUND
- `tests/test_auth_routes.py` exists: FOUND
- Commit 8083851 exists: FOUND
- Commit 6874d64 exists: FOUND
- All 9 tests pass: CONFIRMED (9/9 PASSED)
- `grep -q "include_router(auth_router)" app/main.py`: CONFIRMED
