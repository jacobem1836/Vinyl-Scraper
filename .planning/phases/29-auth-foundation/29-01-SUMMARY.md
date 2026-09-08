---
phase: 29-auth-foundation
plan: "01"
subsystem: auth
tags: [auth, bcrypt, sessions, middleware, fastapi]
dependency_graph:
  requires: []
  provides: [app/auth.py, User model, SessionMiddleware, secret_key config, users table]
  affects: [app/main.py, app/models.py, app/database.py, app/config.py]
tech_stack:
  added: [bcrypt==4.2.0, itsdangerous==2.2.0]
  patterns: [bcrypt password hashing, Starlette signed-cookie sessions, FastAPI exception handler redirect]
key_files:
  created:
    - app/auth.py
    - tests/test_auth_foundation.py
  modified:
    - requirements.txt
    - app/config.py
    - app/models.py
    - app/database.py
    - app/main.py
decisions:
  - "Hand-rolled bcrypt auth (no auth library) per D-03 in 29-CONTEXT.md"
  - "itsdangerous==2.2.0 added to requirements.txt as it is a required transitive dep for Starlette SessionMiddleware not previously pinned"
  - "AuthRedirect custom exception used instead of HTTPException for 303 redirects from dependencies (FastAPI deps cannot return RedirectResponse directly)"
metrics:
  duration_seconds: 338
  completed_date: "2026-05-10"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 5
---

# Phase 29 Plan 01: Auth Foundation Summary

**One-liner:** bcrypt hashing, User model, Starlette signed-cookie sessions (30-day TTL), `current_user`/`require_auth` dependencies — all wired; no routes yet.

## What Was Built

Plan 01 establishes the auth primitives that Plans 02 (login/register routes) and 03 (route guards) depend on:

- **User model** (`app/models.py`) — `id`, `email` (unique, indexed), `password_hash`, `created_at`; matches existing declarative Column style
- **users table migration** (`app/database.py:run_migrations`) — additive `CREATE TABLE IF NOT EXISTS users` appended using the existing try/except pattern; works on both SQLite and PostgreSQL
- **`secret_key` config field** (`app/config.py:Settings`) — defaults to `"dev-insecure-change-me"`; production deploys must set `SECRET_KEY` env var
- **bcrypt dependency** (`requirements.txt`) — `bcrypt==4.2.0` and `itsdangerous==2.2.0` (Starlette SessionMiddleware transitive dep)
- **`app/auth.py`** — `hash_password`, `verify_password`, `current_user`, `require_auth`, `AuthRedirect`, `auth_redirect_response`
- **SessionMiddleware** (`app/main.py`) — signed `crate_session` httpOnly cookie, 30-day TTL, `same_site=lax`, mounted before all routers
- **AuthRedirect exception handler** (`app/main.py`) — converts `AuthRedirect` to `303 /login?next=<encoded_path>`
- **8 unit tests** (`tests/test_auth_foundation.py`) — all passing: hash round-trip, mismatch rejection, User model columns, users table creation, `current_user` with no session / valid session / missing user

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | User model, bcrypt dep, secret_key, migration | 4e639d1 | requirements.txt, app/config.py, app/models.py, app/database.py, tests/test_auth_foundation.py |
| 2 | app/auth.py + SessionMiddleware + exception handler | df25179 | app/auth.py, app/main.py, requirements.txt |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] itsdangerous missing from requirements.txt**
- **Found during:** Task 2 verification -- `from app.main import app` raised `ModuleNotFoundError: No module named 'itsdangerous'`
- **Issue:** Starlette's `SessionMiddleware` requires `itsdangerous` for cookie signing; it was not previously in `requirements.txt` (venv happened to have it from another dep, but it wasn't pinned)
- **Fix:** Appended `itsdangerous==2.2.0` to `requirements.txt`
- **Files modified:** `requirements.txt`
- **Commit:** df25179

**2. [Infrastructure] Worktree reset dropped planning files**
- **Found during:** Task 1 commit -- git reset to correct base caused planning artifact files to be untracked
- **Fix:** Restored `.planning/phases/29-auth-foundation/` files from the original commit via `git checkout <hash> --`
- **Files modified:** All 29-auth-foundation planning files
- **Commit:** bac9c6d

## Security Notes

| Threat | Status |
|--------|--------|
| T-29-01: Session tampering | Mitigated -- `SessionMiddleware` signs cookie with `settings.secret_key` |
| T-29-02: Password storage | Mitigated -- bcrypt rounds=12 in `hash_password`; plaintext never written |
| T-29-03: XSS cookie theft | Mitigated -- httpOnly by default in Starlette SessionMiddleware; `same_site=lax` |
| T-29-04: Weak `secret_key` default | Accepted -- dev default ships; production MUST set `SECRET_KEY` env var |

## Known Stubs

None -- plan goal achieved. No placeholder values that flow to UI.

## Threat Flags

None -- no new network endpoints or trust boundaries introduced; this plan adds only middleware and internal utilities.

## Self-Check: PASSED

- `app/auth.py` exists: FOUND
- `tests/test_auth_foundation.py` exists: FOUND
- Commit 4e639d1 exists: FOUND
- Commit df25179 exists: FOUND
- All 8 tests pass: CONFIRMED (8/8 PASSED)
- `from app.main import app` imports cleanly: CONFIRMED
