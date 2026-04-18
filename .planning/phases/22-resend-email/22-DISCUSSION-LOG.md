# Phase 22: Resend Email - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-19
**Phase:** 22-resend-email
**Mode:** discuss

## Areas Discussed

### From Address
| Question | Options Presented | User Choice |
|----------|------------------|-------------|
| How to configure the Resend sender address | New RESEND_FROM env var / Reuse notify_email / Hardcode onboarding@resend.dev | New RESEND_FROM env var |

**User note:** "I dont have a domain for this yet, but for now just do resend_from and ill set it for my other domain"

### SMTP Config Cleanup
| Question | Options Presented | User Choice |
|----------|------------------|-------------|
| What to do with smtp_host, smtp_port, smtp_user, smtp_password | Remove from config.py / Keep as unused fields | Remove from config.py |

## Codebase Analysis Notes

- Current transport: `smtplib.SMTP` via `asyncio.to_thread(_send_smtp, ...)` in `notifier.py`
- `smtp_user` currently doubles as both SMTP username and `from_addr` — this coupling is broken by the migration
- `resend` SDK is synchronous; same `asyncio.to_thread` wrapper pattern applies
- All notification logic (thresholds, template rendering, `should_notify`) is untouched
- Todo file at `.planning/todos/pending/2026-04-15-change-to-resend-for-emails.md` was the originating request

## No Corrections
All decisions were made without needing corrections or revisits.
