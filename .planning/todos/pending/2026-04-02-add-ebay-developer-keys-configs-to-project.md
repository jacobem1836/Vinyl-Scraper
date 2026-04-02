---
created: 2026-04-02T23:32:36.586Z
title: Add ebay developer keys/configs to project
area: general
files: []
---

## Problem

The eBay adapter (`app/services/ebay.py`) was implemented in phase 02 and requires OAuth credentials (App ID, Cert ID, Dev ID) from the eBay Developer Program. These need to be added to the project's `.env` configuration and `app/config.py` settings so the adapter can authenticate and make Browse API calls in production.

## Solution

1. Register/retrieve eBay developer API keys from https://developer.ebay.com
2. Add eBay credential env vars to `.env` (EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID or similar)
3. Confirm `app/config.py` exposes these settings with appropriate defaults/guards
4. Test adapter returns results with valid credentials
