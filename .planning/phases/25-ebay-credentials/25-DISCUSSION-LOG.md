# Phase 25: eBay Credentials - Discussion Log (Assumptions Mode)

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-21
**Phase:** 25-ebay-credentials
**Mode:** assumptions
**Areas analyzed:** Adapter Status, What's actually missing, EBAY_DEV_ID decision

## Assumptions Presented

### Adapter Status
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| eBay adapter is fully implemented and registered — no new code needed | Confident | `app/services/ebay.py`, `app/services/adapter.py:24`, `app/config.py:8-9`, `.env` |

### What's Actually Missing
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| `.env.example` missing eBay section | Confident | `.env.example` contents (no eBay entries) |
| `main.py` startup() needs eBay credential warning | Confident | `main.py:28-44` — only DB init and scheduler start present |

### EBAY_DEV_ID Decision
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Document DEV_ID in `.env.example` but don't wire it to config.py — Browse API doesn't use it | Likely | `ebay.py:27` (only uses app_id + cert_id for OAuth2) |

## Corrections Made

No corrections — all assumptions confirmed by user.
