---
phase: 28-infrastructure-migration
plan: 01
subsystem: infra
tags: [docker, fly.io, python, uvicorn, postgresql]

# Dependency graph
requires: []
provides:
  - Dockerfile at repo root building python:3.11-slim image, uvicorn on port 8080
  - fly.toml at repo root with internal_port 8080, /api/health healthcheck, APScheduler-safe machine config
  - .dockerignore excluding venv, vinyl.db, .planning, node_modules
affects:
  - 28-02 (GitHub Actions deploy workflow needs fly.toml and Dockerfile)
  - 28-03 (flyctl launch/deploy uses these artifacts)

# Tech tracking
tech-stack:
  added: [Docker, fly.toml]
  patterns:
    - "Fly.io internal port 8080 convention (not env var ${PORT})"
    - "auto_stop_machines=false + min_machines_running=1 for APScheduler persistence"

key-files:
  created:
    - Dockerfile
    - .dockerignore
    - fly.toml
  modified: []

key-decisions:
  - "Port 8080 hardcoded (not ${PORT}) per Fly.io convention — PORT env var only used as a fallback reference"
  - "auto_stop_machines=false and min_machines_running=1 to keep APScheduler alive between requests"
  - "primary_region=syd (Sydney) — closest Fly.io region to Brisbane AU"
  - "256MB RAM, 1 shared CPU — within Fly free tier (3 shared-cpu-1x VMs free)"
  - "No multi-stage Docker build — overkill for a personal project per CONTEXT D-04"

patterns-established:
  - "Dockerfile: copy requirements.txt before app code for layer caching"
  - "fly.toml: always set auto_stop_machines=false for apps with background schedulers"

requirements-completed: [INFRA-01]

# Metrics
duration: 8min
completed: 2026-04-27
---

# Phase 28 Plan 01: Fly.io Container and Config Artifacts Summary

**Dockerfile (python:3.11-slim, port 8080), .dockerignore, and fly.toml (syd region, APScheduler-safe) created at repo root — ready for Fly.io deployment**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-04-27T11:01:00Z
- **Completed:** 2026-04-27T11:09:36Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Dockerfile builds python:3.11-slim image, installs requirements.txt, copies app/static/templates, exposes and starts uvicorn on port 8080
- .dockerignore excludes 24 local-only artifacts (venv, sqlite db, planning docs, railway config) to keep build context clean
- fly.toml configures syd region, /api/health healthcheck, and machines that never auto-stop so APScheduler keeps its 6-hour scan schedule

## Task Commits

1. **Task 1: Create Dockerfile** - `a65f9c5` (feat)
2. **Task 2: Create .dockerignore** - `6f74226` (chore)
3. **Task 3: Create fly.toml** - `a046df9` (chore)

## Files Created/Modified

- `Dockerfile` - Container build: python:3.11-slim, gcc+libpq-dev, requirements.txt install, app copy, uvicorn CMD on port 8080
- `.dockerignore` - Excludes venv/, vinyl.db, .planning/, .git/, .env, tests/, railway.toml, Procfile, and more
- `fly.toml` - Fly.io config: app=vinyl-scraper, region=syd, internal_port=8080, /api/health check, auto_stop=false, 256MB VM

## Decisions Made

- Port 8080 hardcoded in Dockerfile CMD (not ${PORT}) per Fly.io convention from CONTEXT D-04
- `auto_stop_machines = false` and `min_machines_running = 1` — APScheduler runs background scans every 6 hours and must not be killed by spin-down
- `primary_region = "syd"` — Sydney is closest Fly.io region to Brisbane
- Kept `psycopg2-binary` (no switch to `psycopg2`) — binary variant is fine inside Docker containers

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all three files created and verified without issues.

## User Setup Required

None - no external service configuration required for this plan. Fly.io account creation and `flyctl` setup are handled in Plan 03.

## Next Phase Readiness

- Dockerfile, fly.toml, .dockerignore are in place — Plan 02 (GitHub Actions deploy workflow) can reference fly.toml
- Plan 03 (flyctl launch + deploy) will use these artifacts to create the Fly.io app
- `app = "vinyl-scraper"` in fly.toml is a placeholder — flyctl launch in Plan 03 may rewrite if name conflicts

---
*Phase: 28-infrastructure-migration*
*Completed: 2026-04-27*
