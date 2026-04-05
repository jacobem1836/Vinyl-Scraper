---
created: 2026-04-02T23:32:36.586Z
title: Remove dead clarity stuff from project
area: general
files:
  - app/services/clarity.py
  - app/services/adapter.py
---

## Problem

Clarity Records (`clarityrecords.com.au`) is confirmed NXDOMAIN — the domain doesn't exist (unregistered or expired). The adapter was implemented in 02-02 and disabled, and the gap-closure attempt in 02-04 confirmed the site is still unreachable. Keeping dead code and a disabled adapter in the registry adds noise and leaves SRC-03 open indefinitely.

## Solution

- Remove `app/services/clarity.py` entirely
- Remove the clarity entry from `ADAPTER_REGISTRY` in `app/services/adapter.py`
- Remove any `import clarity` in `adapter.py`
- Update REQUIREMENTS.md to drop or mark SRC-03 as cancelled
- Optionally: replace with a different working AU vinyl store
