# CRATE

Vinyl price tracking for Australian buyers. Add the records you want; CRATE searches Discogs, eBay AU and 26 Australian record stores, works out the landed cost in AUD (price converted plus estimated shipping), and emails you when a listing is a deal, a price drops, or something comes back into stock.

CRATE is a discovery tool, not a marketplace. It never buys anything on your behalf.

## How it works

1. You sign up (invite-only while in private beta) and add albums, artists, labels or keywords to your wishlist.
2. Each item is scanned immediately and then every six hours by a background scheduler. Every source is queried concurrently; a source failing never blocks the others.
3. Listings are filtered for relevance (title must match your query) and for format (vinyl only), then stored per item with their price history.
4. The dashboard shows the cheapest landed price per item; the item page shows every listing. A digest email goes out once per scan run when there is something worth telling you, with a 24 hour cooldown per item.

## Architecture

Single FastAPI process, server-rendered Jinja2 templates, hand-written CSS, PostgreSQL in production and SQLite locally, APScheduler running inside the web process (so the app must run as exactly one machine).

```
app/
  main.py            app factory, middleware (sessions, security headers), error pages, lifespan
  config.py          pydantic-settings; production mode validates SECRET_KEY and APP_URL
  database.py        engine (NullPool on Postgres so Neon can autosuspend), SessionLocal
  migrations.py      create_all + add-missing-columns + numbered migrations, run at startup
  models.py          User, WaitlistEntry, WishlistItem, Listing
  auth.py            bcrypt, session login/rotation, route guards, CSRF, signed email tokens, rate limiter
  cli.py             operator commands: invite, waitlist, set-password, verify, migrate
  scheduler.py       6-hourly scan of every user
  routers/
    public.py        landing + waitlist, privacy, /api/health
    auth.py          signup, login, logout, verify, forgot/reset password, account page
    wishlist.py      dashboard, item page, add/edit/delete, scan endpoints, Discogs typeahead, artwork proxy
  services/
    adapter.py       source registry (discogs, shopify, ebay)
    discogs.py       official API; prices via marketplace stats in AUD; rate-limit aware
    shopify.py       26 AU stores via /search/suggest.json or /products.json, vinyl-only filter
    ebay.py          Browse API, fixed-price vinyl, real origin country and currency
    scanner.py       per-item scan: upsert listings, snapshot previous price/stock, deactivate vanished ones
    notifier.py      deal / price-drop / back-in-stock detection and digest rendering
    pricing.py       FX (hourly, cached, with fallback) + shipping estimates = landed AUD; the only money maths
    relevance.py     title-vs-query scoring, digital-format rejection
    scan_status.py   per-user in-memory progress for the dashboard
    mailer.py        Resend wrapper (logs instead of sending when unconfigured)
templates/           pages, partials, email/ (verify, reset, digest)
static/              style.css (CRATE design system), typeahead.js, fonts, logo
tests/               pytest; runs against a throwaway SQLite file so migrations execute for real
```

### Data model

`users` own `wishlist_items` (FK, cascade delete) which own `listings` (unique on item + URL). Every query in the routers is scoped by `user_id`; there is no cross-user path. `listings.prev_price` / `prev_is_in_stock` hold the previous scan's values for change detection; `is_active` turns false when a source that answered no longer returns the URL.

## Local development

```bash
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # add DISCOGS_TOKEN at minimum; SIGNUP_MODE=open is easiest locally
uvicorn app.main:app --reload    # http://localhost:8000
pytest -q
```

Without `RESEND_API_KEY`, verification and reset emails are printed to the console instead of sent. Without `DISCOGS_TOKEN`, Discogs and the typeahead return nothing.

## Configuration

All settings come from environment variables (or `.env` locally). See `.env.example` for the full list. In production (`ENV=production`) the app refuses to start unless `SECRET_KEY` is at least 32 random characters and `APP_URL` is an `https://` URL.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs session cookies, CSRF tokens, verification and reset links. Rotating it logs everyone out. |
| `APP_URL` | Absolute base URL used in emails. |
| `DATABASE_URL` | `postgresql://...` in production. `postgres://` is normalised. |
| `SIGNUP_MODE` | `invite` (default): only addresses invited from the waitlist can sign up. `open`: anyone. |
| `LEGACY_OWNER_EMAIL` | One-off: wishlist rows that predate accounts are assigned to this user on the first migrated start. |
| `RESEND_API_KEY`, `RESEND_FROM` | Email delivery. The from-address domain must be verified in Resend. |
| `DISCOGS_TOKEN`, `EBAY_APP_ID`, `EBAY_CERT_ID` | Source credentials. |

## Accounts and access

- Signup is gated by the waitlist. Visitors join at `/`; you invite them with `python -m app.cli invite person@example.com` (run against the production database, e.g. `fly ssh console -C "python -m app.cli invite ..."`). Set `SIGNUP_MODE=open` to drop the gate.
- New accounts must confirm their email before deal alerts are sent. Password reset and confirmation links are signed with `SECRET_KEY` and expire (1 hour and 3 days respectively).
- Sessions are signed, `HttpOnly`, `SameSite=Lax`, `Secure` in production, 30 days. Every state-changing request needs a CSRF token (form field or `X-CSRF-Token` header).
- Login, signup, reset, waitlist and scan endpoints are rate-limited per IP (and per email for login) in-process.
- Users can change their password and delete their account (and all data) from `/account`.

## Scanning and notifications

- Manual rescans: per item or whole wishlist from the UI (`POST /api/scan/start`), at most 12 per user per hour, never two at once per user.
- Scheduled: every `SCAN_INTERVAL_HOURS`, every user in turn, three items at a time, one database session per item.
- Sources: a listing is kept if its title matches the query above `RELEVANCE_THRESHOLD` and it is not a digital format. Discogs prices come from the marketplace stats endpoint in AUD; eBay and Shopify report their own currency and origin.
- Landed cost = price converted to AUD (hourly rates from open.er-api.com, cached, hard-coded fallback) + shipping estimate by origin country (`services/pricing.py`, `SHIPPING_ESTIMATE_AUD` when unknown).
- Digest email per user per scan run when an item has a new listing at or below `notify_below_pct` under its typical (median) price, an existing listing dropped 10% or more, or a listing came back into stock. Per-item cooldown `NOTIFY_COOLDOWN_HOURS`.

## Deployment (Fly.io + Neon)

Production runs on one Fly machine in Sydney (`fly.toml`) against a Neon PostgreSQL project in `ap-southeast-2`. GitHub Actions (`.github/workflows/deploy.yml`) runs the tests on every push and pull request and deploys `main` with `flyctl deploy --ha=false` when they pass.

First-time setup:

```bash
fly apps create crate --org personal
fly secrets set SECRET_KEY=... APP_URL=https://<your-domain> DATABASE_URL=postgresql://... \
  DISCOGS_TOKEN=... EBAY_APP_ID=... EBAY_CERT_ID=... RESEND_API_KEY=... RESEND_FROM="CRATE <alerts@...>" \
  SIGNUP_MODE=invite LEGACY_OWNER_EMAIL=you@example.com
fly deploy --ha=false
fly scale count 1            # the scheduler must not run on two machines
```

`FLY_API_TOKEN` must be a GitHub Actions secret. Health check: `GET /api/health`. Rollback: `fly releases` then `fly deploy --image <previous image>` or revert the commit on `main`.

Neon cost note: the app uses `NullPool` on Postgres so no idle connection keeps Neon's compute awake; the scheduler wakes it every six hours. Keep the project on the free plan's autosuspend defaults.

## Operations

```bash
fly logs                                         # app output; scan and migration lines are prefixed [Scanner], [migrate], ...
fly ssh console -C "python -m app.cli waitlist"  # who is waiting / invited
fly ssh console -C "python -m app.cli invite a@b.c"
fly ssh console -C "python -m app.cli set-password a@b.c"   # interactive; or use the forgot-password flow
```

Troubleshooting:
- App will not start in production: check `SECRET_KEY` length and `APP_URL` scheme (the startup error says which).
- Migrations: run on every start and are idempotent. `schema_migrations` records what has applied. A failed migration aborts startup so the previous release keeps serving.
- No listings for anything: check `DISCOGS_TOKEN`, and look for `[Shopify]` lines reporting Cloudflare 429 challenges (the scanner staggers store requests to avoid them).
- Emails not arriving: `RESEND_API_KEY`/`RESEND_FROM` unset logs instead of sending; the from-domain must be verified in Resend; users must confirm their address before digests are sent.

## Sources

| Source | Method | Notes |
|---|---|---|
| Discogs | Official API with token | Vinyl-only search, marketplace stats in AUD, honours rate-limit headers |
| eBay AU | Browse API (OAuth client credentials) | Fixed-price vinyl category, origin country from item location |
| 26 Australian stores | Shopify `search/suggest.json` / `products.json` | All checked against robots.txt; vinyl-only filter; requests staggered |

Removed in 2026-09: Clarity Records (domain gone), Juno and Discrepancy Records (Cloudflare JavaScript challenge), Bandcamp (robots.txt disallows search; no public search API).

## Project history

`.planning/` is the archived planning record from v1.0 to v1.6 (a GSD-style workflow). It is historical context only; the September 2026 production overhaul superseded its remaining phases.
