# Phase 28: Infrastructure Migration - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Move the app off Railway onto a free, always-on host with automatic redeploy on git push. Migrate PostgreSQL data to a managed free-tier database. No application code changes — purely deployment and ops work.

Success means: the app is reachable, the scanner runs on its 6-hour schedule, a `git push` to `main` triggers a redeploy, and all env vars are configured.

</domain>

<decisions>
## Implementation Decisions

### Host Platform
- **D-01:** Deploy to **Fly.io** (not Render, Koyeb, or VPS)
  - Reason: always-on free tier (3 shared-CPU VMs, no spin-down), critical because APScheduler must stay alive for background scans
  - Render free tier spins down after 15 min inactivity — ruled out for this reason

### Database
- **D-02:** PostgreSQL on **Neon** (not Render Postgres, not Supabase)
  - Reason: free tier with no expiry, 0.5GB storage, standard Postgres interface via `DATABASE_URL`
  - Render Postgres free expires after 90 days — ruled out
  - Supabase pauses after 1 week inactivity — ruled out

### Auto-Deploy
- **D-03:** GitHub Actions workflow triggers deploy on push to `main`
  - File: `.github/workflows/deploy.yml`
  - Uses `flyctl deploy` via the official `fly-apps/flyctl-actions` action
  - `FLY_API_TOKEN` stored as a GitHub secret
  - Preferred over Fly.io native git integration for visibility and extensibility (can add test step later)

### Container / Build
- **D-04:** Add a **minimal Dockerfile** — Fly.io requires one
  - Pattern: `FROM python:3.11-slim` → copy `requirements.txt` → `pip install` → copy app → `CMD uvicorn app.main:app --host 0.0.0.0 --port 8080`
  - No multi-stage build (overkill for a personal project)
  - `railway.toml` and `Procfile` kept in repo but not used by Fly.io

### Claude's Discretion
- Exact `fly.toml` configuration (region, memory, CPU)
- Data migration procedure (pg_dump from Railway, pg_restore to Neon)
- Port mapping in Dockerfile vs fly.toml (Fly.io uses 8080 internally by convention)
- Whether to keep `psycopg2-binary` or switch to `psycopg2` (binary is fine in Docker)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs or ADRs for this phase — all decisions captured above.

### Environment Variables Required (from app/config.py)
These must be set on Fly.io for the app to start cleanly (INFRA-04):
- `DATABASE_URL` — Neon connection string (postgresql://...)
- `API_KEY` — iOS Shortcut auth
- `DISCOGS_TOKEN`
- `EBAY_APP_ID`
- `EBAY_CERT_ID`
- `RESEND_API_KEY`
- `RESEND_FROM`
- `NOTIFY_EMAIL`

### Relevant files
- `app/config.py` — all settings and their env var names
- `requirements.txt` — dependencies to install in Docker image
- `Procfile` — existing start command (`uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`)
- `railway.toml` — existing deploy config (reference only, not used on Fly.io)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Procfile`: start command is the source of truth — replicate in Dockerfile CMD
- `requirements.txt`: complete pinned deps — pip install directly in Dockerfile
- `app/config.py`: all env vars via pydantic-settings, reads from env at startup

### Established Patterns
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- PostgreSQL driver: `psycopg2-binary==2.9.10` already in requirements.txt
- Database URL pattern: `postgresql://user:pass@host/db` — Neon provides this exact format
- APScheduler initialised on app startup in `app/main.py` — must keep running (no sleep/spin-down)

### Integration Points
- Database: `app/database.py` reads `settings.database_url` — only env var change needed for Neon
- Health check: `GET /api/health` is already defined (used in `railway.toml`) — reuse for Fly.io healthcheck

</code_context>

<specifics>
## Specific Ideas

- Free tier must be indefinitely free (not a 90-day trial) — drove the Fly.io + Neon choice
- Render was initially considered but ruled out due to spin-down behaviour killing the APScheduler

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 28-infrastructure-migration*
*Context gathered: 2026-04-27*
