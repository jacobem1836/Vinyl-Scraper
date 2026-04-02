# Codebase Concerns

**Analysis Date:** 2026-04-02

## Security Concerns

**API Key Validation:**
- Issue: Default API key in config is `change-me-please` and must be manually set by user. No warning system if left unchanged in production.
- Files: `app/config.py`, `app/routers/wishlist.py`
- Risk: Unauthorized access to all API endpoints (create/delete wishlist items, trigger scans) if deployment skips this step.
- Current mitigation: `.env.example` documents the requirement, but there's no runtime validation.
- Recommendation: Add startup check that warns or fails if `api_key` equals default value in non-development environment.

**No Input Validation on String Fields:**
- Issue: Form fields like `type` and `query` accept any string with minimal validation.
- Files: `app/routers/wishlist.py` (lines 66-70, 95-99)
- Risk: SQL injection via ORM is mitigated by SQLAlchemy, but no bounds checking on field lengths. Very long strings could cause unexpected DB behavior or memory issues.
- Current mitigation: SQLAlchemy parameterized queries prevent injection, but field size limits are database-dependent.
- Recommendation: Add Pydantic validators with `max_length` constraints (e.g., 500 chars for query, 50 for type).

**No Rate Limiting:**
- Issue: API endpoints have no rate limiting or throttling.
- Files: `app/routers/wishlist.py` (all API routes)
- Risk: Spam/DOS attacks. Anyone with a valid API key can spam scan operations or bulk-import thousands of items.
- Current mitigation: None.
- Recommendation: Add per-IP rate limiting using middleware (e.g., slowapi) or per-API-key request limits.

**Plaintext SMTP Credentials in .env:**
- Issue: `SMTP_PASSWORD` stored as plaintext in environment file.
- Files: `.env` (not readable, but pattern is documented in `.env.example`)
- Risk: If `.env` is ever accidentally committed or compromised, email account is exposed. App-specific passwords from iCloud mitigate full account compromise, but still a credential leak.
- Current mitigation: `.gitignore` should prevent `.env` from being committed (verify this).
- Recommendation: Document use of app-specific passwords (already done). Consider supporting OAuth2 for email in future.

**HTML Injection in Email Templates:**
- Issue: `html.escape()` is used correctly in email generation, but relies on correct usage everywhere.
- Files: `app/services/notifier.py` (lines 87-93)
- Risk: Low risk due to careful escaping, but `listing.url` is escaped with `quote=True` while other fields use default escaping. Inconsistent patterns.
- Current mitigation: All user-controlled fields are escaped before HTML insertion.
- Recommendation: Use a templating engine (Jinja2) for email bodies instead of string concatenation to reduce escape errors.

## Performance Bottlenecks

**Sequential Item Scanning in Scheduled Job:**
- Issue: `scan_all_items()` in scheduler scans each item sequentially in a loop (lines 70-74 of `app/services/scanner.py`).
- Files: `app/scheduler.py` (line 18), `app/services/scanner.py` (lines 64-80)
- Impact: If there are 50 wishlist items and each scan takes 10 seconds, full scan takes 500+ seconds. With default 6-hour interval, this blocks the scheduler for 8+ minutes every 6 hours.
- Current bottleneck: `for item in items: new_listings = await scan_item(db, item)` — asyncio operations within items are concurrent, but items are scanned sequentially.
- Improvement path: Batch items into parallel tasks (e.g., `asyncio.gather(*[scan_item(db, i) for i in items])`) with concurrency limit to avoid overwhelming external APIs.

**Database Migration Errors Silently Ignored:**
- Issue: `run_migrations()` catches all exceptions and silently passes (lines 26-44 of `app/database.py`).
- Files: `app/database.py`
- Impact: If a migration fails (e.g., column type conflict, constraint violation), the app starts successfully but the database is in an inconsistent state. This won't be discovered until a query tries to use the missing column.
- Symptom: Runtime errors in unrelated endpoints when they touch the affected columns.
- Improvement path: Log migration errors with details, or fail startup with clear message if migrations fail (in production). Keep silent-pass for development only.

**N+1 Query Pattern in Enrichment:**
- Issue: `_enrich_item()` in `app/routers/wishlist.py` (line 26) iterates over `item.listings` without explicit eager loading.
- Files: `app/routers/wishlist.py` (line 27)
- Impact: For each item in the list (line 49 and 184), a separate query is made to fetch related listings. With 100 items, this becomes 100+ queries instead of 1-2 with joins.
- Symptom: Slow dashboard load times as wishlist grows.
- Improvement path: Use `joinedload()` or `selectinload()` in queries that fetch items for display.

**Blocking Email Sends on Request Thread:**
- Issue: Email sending in `notifier.send_deal_email()` is run via `asyncio.to_thread()` but is called eagerly in request handlers.
- Files: `app/services/notifier.py` (lines 109-119), `app/routers/wishlist.py` (lines 86-87, 131-134)
- Impact: Request response time depends on email delivery (20+ seconds to SMTP server). If email fails, user sees delayed response.
- Current mitigation: Uses thread pool, so doesn't block event loop, but still blocks the HTTP request.
- Improvement path: Queue email sends to a background job (Celery, RQ) instead of waiting for delivery.

## Tech Debt

**Bare Exception Handlers:**
- Issue: Multiple `except Exception:` blocks that catch and silence all errors.
- Files: `app/database.py` (lines 33, 38, 43), `app/services/discogs.py` (lines 42, 87, 90, 151, 154, 215, 218), `app/services/shopify.py` (lines 69, 70), `app/services/notifier.py` (line 121)
- Impact: Errors are printed to stdout but never logged structurally. In production (Railway), these logs are hard to aggregate and search.
- Recommendation: Replace `print()` with structured logging (use `logging` module or library like `structlog`). Log at appropriate levels (DEBUG for expected API errors, ERROR for unexpected exceptions).

**Logging via print() Statements:**
- Issue: All error reporting uses `print()` instead of logging module.
- Files: Most service files (discogs, shopify, notifier, bulk_import)
- Impact: Cannot control log levels, filter by module, or send to external log aggregators. Hard to debug production issues on Railway.
- Recommendation: Implement logging configuration (e.g., configure `logging` module in `app/config.py` or use a library like `loguru`).

**No Environment-Based Configuration:**
- Issue: Debug/development settings are not environment-aware (e.g., SQLAlchemy echo mode, log levels).
- Files: `app/config.py`
- Impact: Can't easily enable query logging in production for debugging slow queries.
- Recommendation: Add `DEBUG` and `LOG_LEVEL` env vars to control behavior per deployment.

**Manual Schema Migrations:**
- Issue: Database migrations are custom Python code that tries to ALTER TABLE if columns don't exist.
- Files: `app/database.py` (lines 26-44)
- Impact: Scaling beyond SQLite becomes risky. Hard to track which migrations have run. No rollback capability. Fragile for schema complexity.
- Improvement path: Migrate to proper migration tool (Alembic) before database grows significantly.

**Inconsistent Error Handling in API Routes:**
- Issue: Some routes check `is_active=True` in filter, others check separately.
- Files: `app/routers/wishlist.py` (lines 102-104 vs line 116, 125 vs 239)
- Impact: Inconsistent behavior. Line 116 deletes items regardless of `is_active` status, while line 102 rejects requests for inactive items.
- Recommendation: Standardize — either soft-delete (filter is_active=True always) or hard-delete (no is_active check needed).

## Missing Error Handling

**Unhandled httpx Timeout Exceptions:**
- Issue: HTTPX clients have `timeout=20.0` but timeouts are not explicitly caught or retried.
- Files: `app/services/discogs.py` (lines 49, 97, 161), `app/services/shopify.py` (line 107)
- Impact: If an external API is slow, scan operation fails silently (caught by outer `except Exception`). No retry logic.
- Recommendation: Add specific handling for `httpx.TimeoutException` with exponential backoff for Discogs/Shopify queries.

**Email Sending Failures Don't Notify User:**
- Issue: If email fails to send in a request handler, user gets a successful response even though no notification was queued.
- Files: `app/routers/wishlist.py` (lines 86-87, 131-134) — notification send result is not checked.
- Impact: User thinks they'll get an email alert, but they won't.
- Recommendation: Check return value of `send_deal_email()` and log a warning if it fails (don't fail the request, but alert operator).

**Missing Null Check on Related Objects:**
- Issue: `item.listings` could be None (line 27 of wishlist.py says `or []` but relies on relationship always existing).
- Files: `app/routers/wishlist.py` (line 27)
- Impact: Low risk due to SQLAlchemy relationship defaults, but fragile if relationship definition changes.
- Recommendation: Ensure relationship is always initialized (it is, via `relationship(cascade="all, delete-orphan")`), or add explicit null coalescing.

**No Validation of notify_below_pct Range:**
- Issue: `notify_below_pct` is a float field with no min/max bounds in form submission.
- Files: `app/routers/wishlist.py` (lines 69, 98)
- Impact: User can set value to 200% or -50%, breaking price comparison logic.
- Recommendation: Add Pydantic validator `0 <= notify_below_pct <= 100` in `WishlistItemCreate` schema.

## Scalability Limits

**SQLite Database Not Suitable for Multi-User Production:**
- Issue: Default database is SQLite with file locking. Multiple concurrent writes will cause contention.
- Files: `app/config.py` (line 5), `app/database.py` (lines 6-10)
- Current state: README documents migration to PostgreSQL on Railway, so this is partially addressed.
- Impact: If deployed with SQLite to shared hosting, concurrent scan + user interactions will cause `database is locked` errors.
- Recommendation: Enforce PostgreSQL in production. Add validation in startup to reject SQLite in production mode.

**No Database Indexing Strategy:**
- Issue: Models don't define indexes beyond primary keys and foreign keys.
- Files: `app/models.py`
- Impact: Queries like filtering by `wishlist_item_id` or `url` will be slower as data grows.
- Improvement path: Add indexes on `Listing.wishlist_item_id`, `Listing.url`, `WishlistItem.is_active`.

**Unbounded Listing Growth:**
- Issue: No cleanup logic for old listings. Listings from old searches accumulate indefinitely.
- Files: No cleanup code exists
- Impact: Database grows unbounded. After 1 year of scanning, thousands of outdated listings remain.
- Improvement path: Add optional scheduled job to soft-delete listings older than N days, or add TTL mechanism.

**External API Rate Limiting Not Handled:**
- Issue: Discogs API has rate limits (60 requests/min for search, 300 requests/hour for detail), but no backoff strategy.
- Files: `app/services/discogs.py`
- Impact: If scanning many items quickly, Discogs returns 429 errors. Currently caught and silently ignored.
- Recommendation: Implement exponential backoff with retry, or check response headers for rate limit status.

## Dependencies at Risk

**Old Python Version Target:**
- Issue: README specifies "Python 3.11+", but it's 2026 and Python 3.11 is EOL (Oct 2027). Code may not fully benefit from recent improvements.
- Impact: Missing features, security backports may be limited.
- Recommendation: Update to Python 3.13+ (verify all dependencies support it, especially pg8000 and aiosqlite).

**pg8000 as Primary Production Database Driver:**
- Issue: pg8000 is a pure-Python PostgreSQL driver with slower performance than psycopg3/psycopg2.
- Files: `requirements.txt` (line 5), `app/database.py` (lines 6-7)
- Impact: On Railway with many concurrent connections, pg8000 may become a bottleneck.
- Recommendation: Monitor performance. Consider switching to `psycopg[binary]` (psycopg3) if performance issues arise.

**APScheduler in Single-Process Deployment:**
- Issue: APScheduler keeps jobs in memory. If app restarts, missed scheduled scans are lost.
- Files: `app/scheduler.py`
- Impact: If Railway auto-restarts the app, scanning for that interval is skipped.
- Recommendation: For production, consider switching to persistent scheduler (Celery Beat) or use Railway's cron integration to trigger `/api/scan` endpoint periodically.

## Testing Gaps

**No Test Coverage:**
- Issue: No test files exist in codebase.
- Files: None (test directory missing)
- Impact: Refactoring is risky. Bugs are found in production (email on Railway, API responses).
- Critical gaps:
  - Scanner logic: What happens if Discogs returns 404? Edge cases in price parsing?
  - Notifier logic: Email edge cases (very long titles, special characters)?
  - API key validation: Does it properly reject bad keys?
  - Database migrations: Do they work on fresh install? On existing databases with schema variations?
- Recommendation: Add pytest fixtures for database, mock external APIs, write at least 40% coverage of critical paths (scanner, notifier, API validation).

## Known Limitations

**Discogs Search Does Not Support All Item Types Equally:**
- Issue: Label and artist searches in Discogs only fetch top 5 releases (hardcoded in lines 125, 189 of discogs.py). Album search fetches 3 results. Coverage is inconsistent.
- Files: `app/services/discogs.py`
- Impact: Some searches return fewer listings than expected. Not a bug, but a limitation users may notice.
- Improvement path: Make max_results configurable per item type, or document the limitation.

**Shipping Cost Table is Hardcoded:**
- Issue: `SHIPPING_TABLE` in `shipping.py` is static and must be updated manually.
- Files: `app/services/shipping.py`
- Impact: Shipping costs drift from reality over time. No way for users to override estimates.
- Recommendation: Make shipping costs configurable per item or globally via environment variable.

**No Support for Manual Listing Creation:**
- Issue: Listings are only created by automated scanner. Users cannot add manual prices.
- Impact: If a seller sends a custom quote outside of the websites, users can't track it.
- Recommendation: Add web UI / API endpoint to manually add listings (low priority for MVP).

---

*Concerns audit: 2026-04-02*
