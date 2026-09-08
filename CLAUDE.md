# CRATE

Vinyl price tracker for Australian buyers: multi-user wishlist, concurrent source scanning (Discogs, eBay AU, 26 AU Shopify stores), landed cost in AUD, digest emails for deals, price drops and restocks. Read `README.md` first; it is the architecture and operations reference and is kept accurate.

**Core value:** show me the cheapest way to buy the records I want, right now.

## Stack

Python 3.11, FastAPI 0.115, SQLAlchemy 2, Jinja2 server-rendered HTML, hand-written CSS (no framework), APScheduler in-process, httpx, bcrypt + Starlette signed-cookie sessions, itsdangerous tokens, Resend for email. SQLite locally, PostgreSQL (Neon, Sydney) in production, `psycopg2-binary` driver. Hosted on one Fly.io machine in `syd`, deployed by GitHub Actions after tests pass.

## Commands

```bash
source venv/bin/activate
uvicorn app.main:app --reload      # local app on :8000 (uses .env; SIGNUP_MODE=open is easiest)
pytest -q                          # full suite, ~10s, uses a throwaway SQLite file
python -m app.cli invite a@b.c     # operator commands: invite | waitlist | set-password | verify | migrate
```

## Non-negotiables

- **User isolation.** Every wishlist/listing query goes through `_owned_item()` or filters on `user_id`. New routes must too, and `tests/test_isolation.py` must cover them.
- **CSRF.** Every POST route declares `dependencies=[Depends(require_csrf)]`; forms include `csrf_token`, fetch() sends `X-CSRF-Token`.
- **Money maths lives only in `app/services/pricing.py`.** Landed AUD = converted price + shipping estimate by origin.
- **One Session per coroutine.** Never share a SQLAlchemy Session across `asyncio.gather`.
- **Exactly one machine in production.** The scheduler runs in-process; `fly.toml` and `--ha=false` enforce it.
- **Sources must be lawful.** Check robots.txt and terms before adding a source; use the official API where one exists; self-identifying User-Agent (`services/http.py`) except where documented.
- **Schema changes** go in `app/migrations.py` (idempotent, dialect-aware for SQLite and Postgres) and get a test in `tests/test_migrations.py`.

## Conventions

- 4-space indent, double quotes, type hints on signatures, `print("[Component] message")` logging.
- Templates get context explicitly from routes; `csrf_token()`, `app_url`, `signup_open` are globals.
- Keep it small: no new dependencies without a clear need (see the package-install policy in the user's global rules), no abstractions with one implementation.
- Tests: `tests/conftest.py` provides `browser`/`browser2` (CSRF-aware clients), `db`, `sent_emails`. Prefer behaviour tests through routes over mocking internals.

## History

`.planning/` is the archived GSD planning record for v1.0 to v1.6. It is context, not the workflow: the September 2026 overhaul replaced phases 29 to 32 (auth, isolation, auth expansion, user features) with the current implementation. Do not resume those phases.
