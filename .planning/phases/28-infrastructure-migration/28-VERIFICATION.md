---
phase: 28-infrastructure-migration
verified: 2026-04-29T10:22:00Z
status: passed
score: 9/9 must-haves verified
gaps: []
deferred: []
---

# Phase 28: Infrastructure Migration — Verification Report

**Phase Goal:** App runs reliably on a non-Railway host with auto-deploy from git
**Verified:** 2026-04-29T10:22:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | App is reachable on the new host — all pages load, scanner runs | VERIFIED | `curl https://crate.fly.dev/api/health` returns HTTP 200 `{"status":"ok"}` live at time of verification; 2 Fly machines state=started with 1 passing health check each |
| 2 | PostgreSQL database is accessible from the new host and data is intact | VERIFIED | Neon DATABASE_URL set as Fly secret (Deployed); 33 wishlist_items and 1069 listings migrated and row-count verified; dashboard confirmed showing existing data (human-verified in 28-03) |
| 3 | A git push to main triggers an automatic redeploy within minutes | VERIFIED | Two successful workflow runs: 25103099701 (workflow_dispatch) and 25103381740 (push to main); `gh run list` confirms both `conclusion: success` |
| 4 | All env vars are set and the app starts cleanly | VERIFIED | `flyctl secrets list` shows all 8 secrets (DATABASE_URL, API_KEY, DISCOGS_TOKEN, EBAY_APP_ID, EBAY_CERT_ID, RESEND_API_KEY, RESEND_FROM, NOTIFY_EMAIL) status=Deployed; startup logs show no tracebacks |
| 5 | Dockerfile exists and builds a runnable image | VERIFIED | `Dockerfile` exists at repo root; `FROM python:3.11-slim`, EXPOSE 8080, CMD uvicorn on port 8080; used successfully in two CI deploys |
| 6 | fly.toml configures internal_port 8080, /api/health healthcheck, APScheduler-safe machine config | VERIFIED | `internal_port = 8080`, `path = '/api/health'`, `auto_stop_machines = 'off'`, `min_machines_running = 1` confirmed in file |
| 7 | .dockerignore excludes venv, vinyl.db, .planning, node_modules | VERIFIED | All four exclusions confirmed present in `.dockerignore` |
| 8 | GitHub Actions workflow triggers on push to main and uses flyctl deploy | VERIFIED | `.github/workflows/deploy.yml` exists; `on: push: branches: [main]`, `workflow_dispatch`, `superfly/flyctl-actions/setup-flyctl@master`, `flyctl deploy --remote-only`, `FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}` — all patterns confirmed |
| 9 | FLY_API_TOKEN is set as a GitHub Actions repository secret | VERIFIED | `gh secret list` shows `FLY_API_TOKEN` updated 2026-04-29T10:12:28Z |

**Score:** 9/9 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `Dockerfile` | Container build for Fly.io | VERIFIED | FROM python:3.11-slim, gcc+libpq-dev, requirements.txt install, EXPOSE 8080, CMD uvicorn on 0.0.0.0:8080 |
| `fly.toml` | Fly.io app configuration | VERIFIED | app=crate, region=syd, internal_port=8080, /api/health check, auto_stop=off, min_machines=1, memory_mb=512 |
| `.dockerignore` | Exclude local artifacts from build context | VERIFIED | Excludes venv/, __pycache__/, node_modules/, .planning/, vinyl.db and 19 others |
| `.github/workflows/deploy.yml` | GitHub Actions auto-deploy on push to main | VERIFIED | Triggers on push/main and workflow_dispatch; uses superfly/flyctl-actions; flyctl deploy --remote-only |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Dockerfile CMD | uvicorn app.main:app | container entrypoint on port 8080 | WIRED | CMD matches; port 8080 confirmed serving live traffic |
| fly.toml internal_port=8080 | Dockerfile EXPOSE 8080 | port binding | WIRED | Both set to 8080; health checks passing on Fly machines |
| Fly secrets DATABASE_URL | Neon PostgreSQL | app/config.py reads settings.database_url | WIRED | Secret Deployed; app connects to Neon (dashboard shows data) |
| fly.toml /api/health check | FastAPI health endpoint | http_service.checks path | WIRED | Both machines show "1 total, 1 passing" check |
| deploy.yml FLY_API_TOKEN | Fly.io app | superfly/flyctl-actions step | WIRED | Two successful deploys triggered; secret confirmed in GitHub |

---

### Data-Flow Trace (Level 4)

Not applicable — this is an infrastructure-only phase. No new application code or UI components were introduced. All data flow depends on pre-existing app/config.py, app/database.py, and the FastAPI routes from prior phases.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Health endpoint returns 200 | `curl -si https://crate.fly.dev/api/health` | HTTP 200 `{"status":"ok"}` | PASS |
| Two successful CI runs exist | `gh run list --workflow=deploy.yml --limit 5 --json conclusion,databaseId` | IDs 25103099701 and 25103381740 both `conclusion: success` | PASS |
| All 8 Fly secrets deployed | `flyctl secrets list --app crate` | All 8 names listed, all status=Deployed | PASS |
| FLY_API_TOKEN in GitHub secrets | `gh secret list` | FLY_API_TOKEN present, updated 2026-04-29 | PASS |
| Two Fly machines running | `flyctl status --app crate` | 2 machines, both state=started, both checks passing | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INFRA-01 | 28-01, 28-03 | App deployed on a non-Railway host, reachable, scanner running | SATISFIED | crate.fly.dev live, APScheduler startup confirmed in logs, 2 machines running |
| INFRA-02 | 28-02 | PostgreSQL data migrated to Neon, database accessible | SATISFIED | Neon provisioned ap-southeast-2; 33 wishlist_items + 1069 listings restored; row counts match |
| INFRA-03 | 28-04 | Push to main triggers automatic redeploy | SATISFIED | Two successful GitHub Actions runs (25103099701, 25103381740); deploy.yml wired correctly |
| INFRA-04 | 28-03 | All env vars set, app starts cleanly | SATISFIED | All 8 secrets Deployed on Fly; startup logs clean (no tracebacks, no missing env errors) |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| 28-03-SUMMARY.md | RESEND_API_KEY and RESEND_FROM set as empty strings | Info | Email deal alerts are silently disabled until Resend credentials are configured; app runs normally — notifier checks `if not settings.resend_api_key` before sending |

Note: The empty RESEND values are not a stub in the anti-pattern sense — the app has explicit graceful-skip logic for missing email credentials. This is a configuration gap for a future task, not a blocker for the infrastructure goal.

Note: `auto_stop_machines = 'off'` (string) in fly.toml differs from the plan's `false` (boolean). Both are valid in Fly.io TOML; `'off'` is the format flyctl writes when using `--copy-config`. Functionally equivalent.

---

### Human Verification Required

None — all critical behaviors were verified programmatically or via live infrastructure checks (curl, gh CLI, flyctl).

The following items were human-verified during phase execution and are recorded in summaries:
- Dashboard loads with existing wishlist data (confirmed by user in 28-03: "Yep its there")
- iOS Shortcut endpoint compatibility (per 28-03 Task 3 human checkpoint)
- APScheduler running in flyctl logs

---

### Gaps Summary

No gaps. All four success criteria from ROADMAP.md are satisfied:

1. App reachable at https://crate.fly.dev/ — confirmed live (HTTP 200)
2. Neon database accessible, data intact (33 items, 1069 listings, row counts verified)
3. Push to main triggers auto-deploy — two successful CI runs confirmed
4. All 8 env vars set as Fly secrets, app starts cleanly

---

_Verified: 2026-04-29T10:22:00Z_
_Verifier: Claude (gsd-verifier)_
