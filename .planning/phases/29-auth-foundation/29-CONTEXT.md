# Phase 29: Auth Foundation - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Add user sign-up, sign-in, and session persistence to the app. All wishlist routes require authentication — unauthenticated users are redirected to /login. Passwords stored as bcrypt hashes. No data isolation in this phase (that is Phase 30). No password reset or OAuth (Phase 31).

</domain>

<decisions>
## Implementation Decisions

### Session mechanism
- **D-01:** Signed cookie sessions via Starlette's built-in `SessionMiddleware` — httpOnly cookie, server reads session on each request. Natural fit for Jinja2 SSR.
- **D-02:** Session TTL: 30 days. Sign in once and stay signed in.

### Auth library approach
- **D-03:** Minimal hand-rolled auth — no auth library. bcrypt for password hashing, SessionMiddleware for session storage. ~100–150 lines of straightforward code. Full control, no magic.
- **D-04:** Phase 29 scope: sign-up, sign-in, session persistence, route guards only. Password reset (AUTH-04) and Google OAuth (AUTH-05) are Phase 31.

### Login/signup page design
- **D-05:** Dedicated full pages at `/login` and `/signup`. Unauthenticated requests to any protected route redirect to `/login?next=<original_path>`.
- **D-06:** Separate pages for login and signup — one purpose per page, linked to each other.
- **D-07:** Pages must match the existing dark aesthetic — true black background, Gothic A1 font, same input/button styles as the rest of the CRATE app. Should feel native, not bolted on.

### Existing data (pre-Phase 30)
- **D-08:** There is no existing data to carry forward — treat this as a fresh start. Authenticated users begin with an empty wishlist. Phase 30 handles all data scoping when it adds user_id columns.
- **D-09:** No owner account migration in Phase 29. Phase 30 is responsible for assigning any data to users.

### Claude's Discretion
- bcrypt work factor (12 rounds is standard)
- Password validation rules (minimum length, etc.)
- Error message copy on failed login/signup
- Exact session cookie name and configuration details
- `next` redirect parameter handling edge cases

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — AUTH-01 (sign-up), AUTH-02 (sign-in), AUTH-03 (session persistence), SEC-01 (route guards), SEC-03 (bcrypt) are the Phase 29 requirements. AUTH-04, AUTH-05, SEC-02 are explicitly Phase 31.

### Existing app structure
- `app/main.py` — App factory, startup hooks, route registration. New auth routes and SessionMiddleware go here.
- `app/models.py` — Current data models (WishlistItem, Listing). A User model must be added.
- `app/config.py` — Pydantic settings. A `secret_key` setting for SessionMiddleware signing must be added.
- `app/routers/wishlist.py` — All existing wishlist routes. These must be protected with auth dependency injection.

No external specs — requirements are fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/routers/wishlist.py:require_api_key` — Existing FastAPI dependency pattern (`Depends(require_api_key)`) that can be mirrored for a `require_auth` dependency. Same shape, different implementation.
- `templates/` — Existing Jinja2 templates to reference for styling consistency (true black, Gothic A1, existing input/button styles).
- `app/config.py:Settings` — Add `secret_key: str` here for SessionMiddleware. Already uses pydantic-settings from env.

### Established Patterns
- Dependency injection via `Depends()` is the project's route-guard pattern — `require_auth` should follow the same shape as `require_api_key`.
- Routes are split across `app/main.py` (index, item_detail) and `app/routers/wishlist.py` (web_router, api_router). All three locations need protection.
- DB migrations are run via `run_migrations()` in startup — new User table migration fits this pattern.

### Integration Points
- `SessionMiddleware` must be added to `app` in `main.py` before any routes are mounted.
- New `User` SQLAlchemy model in `app/models.py`.
- New `app/routers/auth.py` (or inline in main.py) for `/login`, `/signup`, `/logout` routes.
- `require_auth` FastAPI dependency must be added to every route in `web_router`, `api_router`, and the direct routes in `main.py`.

</code_context>

<specifics>
## Specific Ideas

- Login page layout: CRATE wordmark at top, centred form, "Don't have an account? Sign up" link at bottom — matches the preview selected during discussion.
- Pages should feel like part of CRATE, not an afterthought. Same dark card/surface treatment as existing modals/inputs.

</specifics>

<deferred>
## Deferred Ideas

- Password reset via email link — Phase 31 (AUTH-04, maps explicitly there)
- Google OAuth sign-in — Phase 31 (AUTH-05)
- Rate limiting on auth endpoints — Phase 31 (SEC-02)
- Per-user data scoping — Phase 30 (DATA-01, DATA-02)
- Personal API keys for iOS Shortcut — Phase 32 (DATA-03)

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 29-auth-foundation*
*Context gathered: 2026-05-10*
