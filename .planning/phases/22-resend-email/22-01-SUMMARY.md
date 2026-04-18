---
phase: 22-resend-email
plan: 01
subsystem: infra
tags: [resend, email, smtp, notifications, transactional-email]

# Dependency graph
requires: []
provides:
  - Resend SDK transport layer for deal alert emails
  - resend_api_key and resend_from settings replacing SMTP fields
  - notifier.py with _send_resend replacing _send_smtp
affects: [notifier, email-alerts, deal-notifications]

# Tech tracking
tech-stack:
  added: [resend==2.29.0]
  patterns: [asyncio.to_thread wrapping sync SDK call for non-blocking email dispatch]

key-files:
  created: []
  modified:
    - requirements.txt
    - app/config.py
    - app/services/notifier.py

key-decisions:
  - "Use resend==2.29.0 (latest stable at time of execution)"
  - "Add extra=ignore to pydantic model_config so old SMTP env vars in .env don't crash startup"
  - "Keep _html_to_plaintext function as it is unused but harmless"

patterns-established:
  - "Email transport via resend.Emails.send wrapped in asyncio.to_thread"
  - "Optional credentials defaulting to None — email silently skipped when unset"

requirements-completed: [RESEND-01, RESEND-02, RESEND-03]

# Metrics
duration: 12min
completed: 2026-04-19
---

# Phase 22 Plan 01: Resend Email Migration Summary

**Replaced SMTP transport in notifier.py with Resend API using resend==2.29.0, removing all smtplib dependency and four SMTP config fields**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-04-19T00:00:00Z
- **Completed:** 2026-04-19T00:12:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added `resend==2.29.0` to requirements.txt
- Replaced four SMTP Settings fields (smtp_host, smtp_port, smtp_user, smtp_password) with resend_api_key and resend_from
- Replaced `_send_smtp` function and all smtplib imports with `_send_resend` using resend.Emails.send
- App boots cleanly with no SMTP or Resend env vars set

## Task Commits

Each task was committed atomically:

1. **Task 1 + 2 + 3: Migrate SMTP to Resend API** - `8bbc999` (feat)

**Plan metadata:** (docs commit — this summary)

## Files Created/Modified
- `requirements.txt` - Added resend==2.29.0
- `app/config.py` - Removed smtp_host/port/user/password; added resend_api_key, resend_from; added extra="ignore" to model_config
- `app/services/notifier.py` - Replaced smtplib imports with `import resend`; replaced _send_smtp with _send_resend; updated guard and asyncio.to_thread call

## Decisions Made
- Pinned resend==2.29.0 (latest stable as of execution date)
- Added `extra="ignore"` to pydantic model_config so existing SMTP env vars in .env don't raise ValidationError after field removal

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added extra="ignore" to pydantic model_config**
- **Found during:** Task 2 (Update Settings in app/config.py)
- **Issue:** After removing SMTP fields, the project's .env still contained SMTP_ vars. Pydantic-settings raised ValidationError ("Extra inputs are not permitted") on startup, breaking app boot.
- **Fix:** Added `"extra": "ignore"` to model_config so unknown env vars are silently dropped.
- **Files modified:** app/config.py
- **Verification:** `python -c "from app.config import settings; ..."` passes without error
- **Committed in:** 8bbc999 (task commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Required for app to boot after SMTP field removal. No scope creep.

## Issues Encountered
- Project's .env file contained SMTP credentials that pydantic rejected after field removal — fixed with extra="ignore" (see deviations above)

## User Setup Required
To use Resend for email alerts, add to `.env`:
```
RESEND_API_KEY=re_...
RESEND_FROM=Crate <alerts@yourdomain.com>
NOTIFY_EMAIL=your@email.com
```
Old SMTP variables can be removed from `.env` but will now be silently ignored if left.

## Next Phase Readiness
- Email transport is functional via Resend SDK
- No SMTP credentials required
- Live send test requires RESEND_API_KEY, RESEND_FROM, NOTIFY_EMAIL set in .env

## Known Stubs
None — all transport logic is fully wired to the Resend SDK.

---
*Phase: 22-resend-email*
*Completed: 2026-04-19*
