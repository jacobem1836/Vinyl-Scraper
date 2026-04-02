# Testing Patterns

**Analysis Date:** 2026-04-02

## Test Framework

**Status:** Not detected

**No test framework configured or in use.**

The codebase contains no test files in the project directory. While test packages exist in `venv/lib` (from dependencies like BeautifulSoup4 and SQLAlchemy which include their own test suites), no project-specific tests are present.

**Implications:**
- All code relies on manual testing or integration testing via API endpoints
- No automated unit test suite
- No test runners configured (pytest, unittest, etc.)
- No CI/CD test pipeline detected

## Test File Organization

**Location:** Not applicable — no tests present

**Naming Convention:** Not applicable

**Search Pattern:** Files matching these would be tests if they existed:
- `test_*.py` prefix pattern
- `*_test.py` suffix pattern
- `tests/` directory structure

## Test Types

### Unit Tests
- **Not implemented**

### Integration Tests
- **Not implemented**
- Manual testing via HTTP endpoints is the implicit approach
- Example testable endpoints:
  - `POST /wishlist/add` (web form)
  - `GET /api/wishlist` (API with auth)
  - `POST /api/wishlist` (create with optional scan)
  - `POST /scan-all` (scan all items)

### E2E Tests
- **Not implemented**

## Coverage

**Requirements:** None enforced

**Estimated Coverage:** Unknown (no test suite to measure)

**Critical Untested Areas:**
- `app/services/discogs.py` — External API integration with multiple search types (album, artist, label)
- `app/services/shopify.py` — Multi-store web scraping and product parsing
- `app/services/scanner.py` — Listing deduplication and update logic
- `app/services/notifier.py` — Email notification filtering and delivery
- `app/routers/wishlist.py` — API and web route handlers
- Database migrations in `app/database.py`

## Manual Testing Approach

**Current Test Method:**
- HTTP requests to running FastAPI server
- Database state inspection via direct SQL queries
- Email sending requires manual SMTP verification (not typically tested in dev)

**Testable Components:**

### Router Tests (Manual via HTTP)
```
GET /                              # Index page with wishlist items
GET /item/{item_id}                # Item detail page
POST /wishlist/add                 # Add item via web form
POST /wishlist/{item_id}/edit      # Edit item via web form
POST /wishlist/{item_id}/delete    # Delete item via web form
POST /wishlist/{item_id}/scan      # Scan single item
POST /scan-all                      # Scan all items

GET /api/health                    # Health check
GET /api/wishlist                  # List items (requires API key)
POST /api/wishlist                 # Create item (requires API key)
POST /api/wishlist/bulk            # Bulk create (requires API key)
DELETE /api/wishlist/{item_id}     # Delete item (requires API key)
GET /api/wishlist/{item_id}/listings  # Get listings for item
POST /api/scan                     # Trigger scan (requires API key)
```

### Service Tests (Implicit via routes)
- **Scanner**: Call `POST /api/scan` or `POST /scan-all` and inspect database
- **Discogs**: Results come through scan endpoint when `discogs_token` configured
- **Shopify**: Results come through scan endpoint (multiple stores scraped)
- **Notifier**: Check email delivery to configured `notify_email` address
- **Shipping**: Verify landed price calculations via API responses

## Development Testing

**Manual Testing Checklist (Inferred from Code):**

1. **Add wishlist item**
   - POST form data to `/wishlist/add`
   - Verify item created in database
   - Verify initial scan ran (check listings added)
   - Verify notification sent if deals found

2. **Scan single item**
   - POST to `/wishlist/{item_id}/scan`
   - Monitor Discogs and Shopify API calls
   - Verify new listings added without duplicates
   - Verify deduplication on re-scan

3. **Bulk import**
   - POST JSON array to `/api/wishlist/bulk`
   - Verify all items created
   - Verify no scans triggered (default behavior)

4. **Price notifications**
   - Add items with different `notify_below_pct` values
   - Add low-price listings manually to database
   - Call scan endpoint
   - Verify email only sent for deals below threshold
   - Verify typical price calculations correct

5. **Shipping cost calculations**
   - Add listings with different `ships_from` countries
   - Verify landed price includes estimated shipping
   - Verify fallback to default shipping if country unknown

6. **Database persistence**
   - Test with SQLite (`vinyl.db`)
   - Test with PostgreSQL via Railway (requires `DATABASE_URL` env var)
   - Verify migrations run on startup

## Environment Setup for Testing

**Required Environment Variables:**
```
DATABASE_URL=sqlite:///./vinyl.db           # or postgresql+pg8000://...
DISCOGS_TOKEN=<your-discogs-token>          # for Discogs API
SMTP_HOST=smtp.mail.me.com                  # email sending
SMTP_PORT=587
SMTP_USER=<your-email>                      # email account
SMTP_PASSWORD=<your-password>               # email password
NOTIFY_EMAIL=<recipient-email>              # where to send deals
SCAN_INTERVAL_HOURS=6                       # scheduled scan frequency
SHIPPING_ESTIMATE_USD=20.0                  # AU shipping estimate
```

**Running the Server:**
```bash
# With hot reload for development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Known Testing Gaps

**Critical:**
- No integration tests for multi-store Shopify scraping (5 stores + umusic)
- No error handling tests for network failures or API rate limiting
- No database migration tests
- No email delivery tests (SMTP mocking not implemented)
- No concurrency tests (multiple concurrent scans or requests)

**Moderate:**
- No tests for edge cases (missing prices, null values, etc.)
- No tests for price outliers in median calculations
- No tests for HTML escaping in email generation

**Low:**
- No tests for static file serving
- No tests for template rendering

## Suggested Testing Approach

**If adding tests:**

1. **Framework**: Use `pytest` with `pytest-asyncio` for async support
2. **Fixtures**: Create test fixtures for:
   - In-memory SQLite database
   - Mock Discogs/Shopify API responses
   - Mock SMTP server
3. **Test Organization**:
   ```
   tests/
   ├── test_routers.py          # Route handlers
   ├── test_services.py         # Service layer (scanner, notifier)
   ├── test_database.py         # Database operations
   └── fixtures.py              # Shared test data
   ```

4. **Key Test Areas**:
   - Price calculation and notification logic (most critical)
   - Listing deduplication
   - API authentication
   - Database schema and migrations

---

*Testing analysis: 2026-04-02*
