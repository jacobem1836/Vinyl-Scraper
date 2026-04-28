---
phase: 28-infrastructure-migration
plan: 03
subsystem: deployment
tags: [fly.io, deployment, secrets, postgresql, neon]

requires:
  - phase: 28-01
    provides: Dockerfile and fly.toml config
  - phase: 28-02
    provides: Neon DATABASE_URL (pooled PostgreSQL endpoint)

provides:
  - Fly.io app crate deployed and running in Sydney (syd)
  - All 8 required secrets set and deployed
  - Health check endpoint confirmed 200 OK
  - App live at https://crate.fly.dev/

affects:
  - 28-04 (Railway decommission — Fly.io must be verified working first)
  - 29-auth-foundation (will deploy to this Fly app)

tech-stack:
  added: [fly.io, flyctl]
  patterns: [secrets-first deployment, two-machine HA on Fly.io, memory scaling after OOM]

key-files:
  modified:
    - fly.toml (finalized app = "crate", region = syd)

key-decisions:
  - "Used flyctl launch --no-deploy --copy-config to preserve existing fly.toml settings rather than regenerating"
  - "Set RESEND_API_KEY and RESEND_FROM as empty strings — notifier gracefully skips email if unset (line 79 notifier.py)"
  - "Two machines created automatically by Fly for HA — min_machines_running = 1 in fly.toml keeps one always on"
  - "Scaled machines from 256MB to 512MB after OOM crash on first boot — app stable at 512MB with Neon connection pool"
  - "App renamed from vinyl-scraper to crate — old app destroyed, fly.toml updated accordingly"

requirements-completed: [INFRA-01, INFRA-04]

duration: 15min
completed: 2026-04-27
---

# Phase 28 Plan 03: Fly.io App Launch and Deployment Summary

**crate Fly.io app deployed to Sydney with Neon database, all 8 secrets configured, health check passing at https://crate.fly.dev/**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-27T12:20:00Z
- **Completed:** 2026-04-27T12:34:00Z
- **Tasks:** 3 (Task 1 human checkpoint cleared; Tasks 2 executed; Task 3 human-verify checkpoint)
- **Files modified:** 1 (fly.toml)

## Accomplishments

- Fly app `crate` created in syd region (original vinyl-scraper app destroyed; name changed to crate)
- All 8 secrets set in one atomic `flyctl secrets set` call and confirmed Deployed
- `flyctl deploy` succeeded — build completed, 2 machines started, health checks passing
- `/api/health` returns `{"status":"ok"}` (HTTP 200) — confirmed via curl
- FastAPI startup logs clean: no tracebacks, no missing env var errors
- APScheduler starts silently on `startup` hook in main.py (scheduler.start() confirmed running via startup complete log)
- OOM crash on first boot — machines scaled from 256MB to 512MB; both machines stable and healthy post-scale
- Dashboard confirmed loading with existing wishlist items from Neon — human verified ("Yep its there")

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 2 | Launch Fly app and set all secrets | 28b0341 | fly.toml |
| 3 | Human verify checkpoint | confirmed by user | — |

## Fly App Details

| Property | Value |
|----------|-------|
| App name | crate |
| Hostname | crate.fly.dev |
| Region | syd (Sydney, Australia) |
| Machines | 2 (shared-cpu-1x, 512MB each) |
| Image size | 136 MB |
| Health check | /api/health — 1 passing per machine |
| Status | started (both machines) |

## Secrets Deployed (names only)

| Secret | Status |
|--------|--------|
| DATABASE_URL | Deployed |
| API_KEY | Deployed |
| DISCOGS_TOKEN | Deployed |
| EBAY_APP_ID | Deployed |
| EBAY_CERT_ID | Deployed |
| RESEND_API_KEY | Deployed (empty — email alerts disabled until Resend key added) |
| RESEND_FROM | Deployed (empty — email alerts disabled until Resend key added) |
| NOTIFY_EMAIL | Deployed |

## Health Check Verification

```
curl -si https://crate.fly.dev/api/health
HTTP/2 200
content-type: application/json
{"status":"ok"}
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] OOM crash on first boot — memory scaled to 512MB**
- **Found during:** Task 3 (post-deployment)
- **Issue:** Both machines OOM-crashed immediately after first deploy at 256MB. Python + SQLAlchemy + Neon connection pool exceeded the default memory allocation.
- **Fix:** `flyctl machine update` to scale both machines to 512MB shared-cpu-1x. App came up stable with no further crashes.
- **Files modified:** None (Fly platform config only — fly.toml machine preset was not changed)

**2. [Rule 2 - Missing] RESEND_API_KEY and RESEND_FROM not in .env**
- **Found during:** Task 2 (reading .env for secret values)
- **Issue:** The app switched from SMTP to Resend in Phase 22. The .env file has old SMTP vars but no RESEND_API_KEY or RESEND_FROM. The plan expected 8 secrets from .env.
- **Fix:** Set RESEND_API_KEY and RESEND_FROM as empty strings. Notifier at line 79 of notifier.py performs `if not settings.resend_api_key or not settings.resend_from` and returns early — email alerts are silently disabled, app runs normally. No crash.
- **Impact:** Email deal alerts will not fire until Resend key is configured via `flyctl secrets set RESEND_API_KEY=<key>`
- **Files modified:** None (secret value choice only)

## Startup Log Evidence

```
app[d8dd799b450738] syd [info] INFO: Started server process [636]
app[d8dd799b450738] syd [info] INFO: Waiting for application startup.
app[d8dd799b450738] syd [info] INFO: Application startup complete.
app[d8dd799b450738] syd [info] INFO: Uvicorn running on http://0.0.0.0:8080
app[d8dd799b450738] syd [info] INFO: 172.19.1.129:50924 - "GET /api/health HTTP/1.1" 200 OK
health[d8dd799b450738] syd [info] Health check 'servicecheck-00-http-8080' on port 8080 is now passing.
```

## Known Stubs

None — this is a deployment plan. No UI or application code was modified.

## Next Phase Readiness

- Fly app running and healthy at 512MB — stable
- Plan 28-04 (Railway decommission) can proceed — human verification passed, dashboard confirmed showing Neon data
- RESEND keys should be configured separately (`flyctl secrets set RESEND_API_KEY=... RESEND_FROM=...`) once Resend account is set up

---

## Self-Check

- [x] fly.toml modified and committed: `28b0341`
- [x] App at https://crate.fly.dev/ confirmed reachable
- [x] `flyctl status` shows 2 machines, state=started
- [x] `flyctl secrets list` shows 8 secrets, all Deployed
- [x] `/api/health` returns HTTP 200 `{"status":"ok"}`
- [x] Dashboard loads with existing wishlist items from Neon — human verified
- [x] Machines scaled to 512MB — stable, no further OOM crashes
- [x] All must_haves from plan frontmatter satisfied

## Self-Check: PASSED

*Phase: 28-infrastructure-migration*
*Completed: 2026-04-27*
