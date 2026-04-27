# Phase 28: Infrastructure Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 28-infrastructure-migration
**Areas discussed:** Target host platform, Database location, Auto-deploy trigger, Procfile vs Dockerfile

---

## Target Host Platform

| Option | Description | Selected |
|--------|-------------|----------|
| Render | Free web service, Nixpacks/Procfile native, git auto-deploy, managed Postgres | |
| Fly.io | Always-on free tier, Docker-based, GitHub Actions deploy | ✓ |
| Koyeb | Free, always-on, Procfile supported | |
| Self-hosted VPS | Cheapest long-term, full control, most setup | |

**User's choice:** Fly.io
**Notes:** User clarified they want free indefinitely. This prompted a second pass — Render was initially selected but ruled out once spin-down behaviour was flagged (APScheduler must stay alive for background scans). Fly.io free tier has always-on VMs with no spin-down.

---

## Database Location

| Option | Description | Selected |
|--------|-------------|----------|
| Render PostgreSQL | Free tier but expires after 90 days | |
| Neon | Free tier, no expiry, 0.5GB, serverless Postgres | ✓ |
| Supabase | Free tier but pauses after 1 week inactivity | |
| Keep Railway for DB only | Avoids data migration, still Railway-dependent | |

**User's choice:** Neon
**Notes:** Free-indefinitely constraint drove this. Render Postgres ruled out (90-day expiry). Supabase ruled out (inactivity pause). Neon is the clean free choice.

---

## Auto-Deploy Trigger

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions | `.github/workflows/deploy.yml`, flyctl deploy, FLY_API_TOKEN secret | ✓ |
| Fly.io native git integration | fly deploy --remote-only, less visible | |

**User's choice:** GitHub Actions
**Notes:** Preferred for visibility and extensibility (can add test step before deploy later).

---

## Procfile vs Dockerfile

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal Python Dockerfile | FROM python:3.11-slim, pip install, CMD uvicorn | ✓ |
| Multi-stage build | Smaller image, more complex | |

**User's choice:** Minimal Python Dockerfile
**Notes:** Fly.io requires a Dockerfile. Multi-stage ruled out as overkill for a personal project.

---

## Claude's Discretion

- Exact fly.toml configuration (region, memory, CPU sizing)
- Data migration procedure (pg_dump from Railway → pg_restore to Neon)
- Port configuration in Dockerfile (Fly.io convention is 8080 internal)
- psycopg2-binary vs psycopg2 (binary is fine in Docker)

## Deferred Ideas

None.
