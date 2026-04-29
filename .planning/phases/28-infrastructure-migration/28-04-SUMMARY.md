---
plan: 28-04
phase: 28-infrastructure-migration
status: complete
completed: 2026-04-29
requirements_satisfied:
  - INFRA-03
key-files:
  created:
    - .github/workflows/deploy.yml
---

# Plan 28-04 Summary — GitHub Actions Auto-Deploy

## What Was Built

Added a GitHub Actions workflow (`.github/workflows/deploy.yml`) that triggers on every push to `main` and deploys to Fly.io via `flyctl deploy --remote-only`. The workflow uses `superfly/flyctl-actions/setup-flyctl@master` and authenticates with a `FLY_API_TOKEN` repository secret.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| 1 | Created `.github/workflows/deploy.yml` | ✓ |
| 2 | Generated deploy-scoped `FLY_API_TOKEN` and set as GitHub Actions secret | ✓ |
| 3 | Triggered and verified two consecutive successful auto-deploy runs | ✓ |
| 4 | Final phase health check passed | ✓ |

## Verification Results

- **Run 1** (workflow_dispatch): `25103099701` — `success`
- **Run 2** (push to main, commit `chore: verify auto-deploy repeatable`): `25103381740` — `success`
- **App health**: `GET https://crate.fly.dev/api/health` → HTTP 200
- **Fly status**: 2 machines in `syd`, both `started`, checks passing, image `deployment-01KQCC0BDRNZKGQ4E1MYFK1DVT`

## Notes

- Initial run failed with `unauthorized` — the pre-existing `FLY_API_TOKEN` secret was stale. Regenerated via `flyctl tokens create deploy -x 999999h` and re-set.
- `--remote-only` flag means builds happen on Fly's remote builders; no Docker required in CI.
- `concurrency: group: deploy-${{ github.ref }}` prevents overlapping deploys on rapid pushes.
- **Railway** can now be safely paused or deleted — Neon holds all data, Fly hosts the app, and GitHub Actions handles deploys. No dependency on Railway remains.

## Self-Check: PASSED
