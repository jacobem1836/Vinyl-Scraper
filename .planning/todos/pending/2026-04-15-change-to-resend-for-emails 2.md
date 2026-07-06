---
created: 2026-04-15T12:45:12.857Z
title: Change to Resend for emails
area: general
files: []
---

## Problem

The app currently uses SMTP (via `asyncio.to_thread(_send_smtp, ...)` in `app/services/notifier.py`) for deal alert emails. SMTP requires credential management and isn't ideal for a Railway-deployed app. Resend (resend.com) provides a simpler API-based email delivery with better deliverability and a free tier suitable for personal use.

## Solution

Replace the SMTP email sending implementation in `app/services/notifier.py` with the Resend Python SDK. Add `RESEND_API_KEY` to environment config. Update `app/config.py` to use `RESEND_API_KEY` instead of SMTP credentials.
