# External Integrations

**Analysis Date:** 2026-04-02

## APIs & External Services

**Music Metadata & Marketplace:**
- Discogs - Vinyl record marketplace and catalog
  - SDK/Client: httpx (async HTTP requests)
  - Auth: Personal token (env var `DISCOGS_TOKEN`)
  - Base URL: `https://api.discogs.com`
  - Endpoints used:
    - `/database/search` - Search for albums, artists, labels
    - `/releases/{id}` - Get release details with pricing
    - `/artists/{id}/releases` - List artist releases
    - `/labels/{id}/releases` - List label releases
  - See: `app/services/discogs.py`
  - Rate limiting: 0.5s delays between requests to avoid rate limits

**Australian Record Store Scraping:**
- Shopify API (via `suggest.json` endpoint)
  - Used by 6 Australian stores:
    1. The Vinyl Store - `thevinylstore.com.au`
    2. Dutch Vinyl - `dutchvinyl.com.au`
    3. Strangeworld Records - `strangeworldrecords.com.au`
    4. Goldmine Records - `goldminerecords.com.au`
    5. Utopia Records - `utopia.com.au`
    6. uMusic Shop AU - `shop.umusic.com.au`
  - SDK/Client: httpx (async HTTP requests)
  - No authentication required (public API)
  - Endpoint: `/search/suggest.json`
  - Query parameters: `q`, `resources[type]`, `resources[limit]`
  - See: `app/services/shopify.py`

## Data Storage

**Databases:**
- SQLite (development)
  - File: `vinyl.db` (auto-created)
  - Connection: `sqlite:///./vinyl.db` (default DATABASE_URL)
  - Use case: Local development without external setup

- PostgreSQL (production)
  - Connection: Environment variable `DATABASE_URL` (Railway auto-configures)
  - URL scheme: `postgresql+pg8000://...` (converted from `postgres://`)
  - Driver: pg8000 (pure Python, no C dependencies)
  - See: `app/database.py` (lines 5-8)

**ORM/Client:**
- SQLAlchemy 2.0 with session-based pattern
- Models defined in: `app/models.py`
- Tables: `wishlist_items`, `listings`
- Migrations: Manual ALTER TABLE in `app/database.py:run_migrations()` for schema evolution

**File Storage:**
- Local filesystem only - No cloud storage integration
- Static files served from: `static/` directory
- Templates served from: `templates/` directory

**Caching:**
- None - All prices fetched on-demand during scans
- Results cached in database (listings table)

## Authentication & Identity

**API Authentication:**
- Custom X-API-Key header authentication
  - Parameter: `X-API-KEY` header
  - Validation in: `app/routers/wishlist.py:require_api_key()`
  - Used for iOS Shortcut API access and bulk import
  - Key stored in environment: `API_KEY`

**External Service Authentication:**
- Discogs API: Token-based auth
  - Header: `Authorization: Discogs token={DISCOGS_TOKEN}`
  - Token obtained from: `https://www.discogs.com/settings/developers`
  - Optional - Discogs search works without token but with lower rate limits

- Shopify stores: No authentication (public search endpoints)
  - User-Agent spoofing for request validity
  - See: `app/services/shopify.py` (line 42)

## Email & Notifications

**Email Service:**
- SMTP for deal alert emails
  - Host: Environment variable `SMTP_HOST` (defaults to iCloud: `smtp.mail.me.com`)
  - Port: Environment variable `SMTP_PORT` (defaults to 587)
  - Username: Environment variable `SMTP_USER`
  - Password: Environment variable `SMTP_PASSWORD` (app-specific password)
  - Recipient: Environment variable `NOTIFY_EMAIL`
  - See: `app/services/notifier.py:_send_smtp()`
  - Protocol: STARTTLS over SMTP (port 587)
  - All parameters optional - alerts disabled if not configured

## Monitoring & Observability

**Error Tracking:**
- None - Errors logged to stdout via print()
- Production stdout captured by Railway

**Logs:**
- Console output only (print statements)
- See error handling in:
  - `app/services/discogs.py` - Discogs API errors
  - `app/services/shopify.py` - Shopify API errors
  - `app/services/notifier.py` - Email send failures
  - `app/scheduler.py` - Scheduled job exceptions

## CI/CD & Deployment

**Hosting:**
- Railway (primary deployment target)
- Heroku-compatible (Procfile format)
- Supports any ASGI-compatible Python host

**Deployment Configuration:**
- `railway.toml` - Railway-specific build/deploy config
  - Builder: NIXPACKS
  - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Health check: GET `/api/health`
  - Restart policy: ON_FAILURE (max 3 retries)
  - Timeout: 30s
  - See: `railway.toml`

- `Procfile` - Process file for Heroku/Railway
  - Web process: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
  - See: `Procfile`

**CI Pipeline:**
- None detected - Manual deployment via git push to Railway

## Environment Configuration

**Required env vars:**
- `DISCOGS_TOKEN` (required for Discogs scraping)
- `API_KEY` (required for API authentication)

**Optional env vars (with defaults):**
- `DATABASE_URL` - Database connection string
  - Default: `sqlite:///./vinyl.db`
  - Production: PostgreSQL URL from Railway
- `SMTP_HOST` - SMTP server hostname
  - Default: `smtp.mail.me.com` (iCloud)
- `SMTP_PORT` - SMTP server port
  - Default: 587
- `SMTP_USER` - SMTP login email
  - Default: None (alerts disabled if not set)
- `SMTP_PASSWORD` - SMTP app-specific password
  - Default: None (alerts disabled if not set)
- `NOTIFY_EMAIL` - Email address for deal alerts
  - Default: None (alerts disabled if not set)
- `SCAN_INTERVAL_HOURS` - How often to auto-scan all items
  - Default: 6
- `SHIPPING_ESTIMATE_USD` - Flat shipping cost estimate (USD) to Australia
  - Default: 20.0 (added to all prices for "landed cost")

**Secrets location:**
- `.env` file (locally, not committed)
- Railway environment variable editor (production)

**Configuration loading:**
- See: `app/config.py` (BaseSettings with .env support)
- See: `README.md` "Configuration" section (table of variables)

## Webhooks & Callbacks

**Incoming:**
- None - Application is stateless (no webhook receivers)

**Outgoing:**
- Email notifications only (SMTP)
- No third-party webhooks called

## Data Flow

**Item Scan Flow:**
1. User adds wishlist item via web form or API
2. Immediate scan triggered: `app/routers/wishlist.py:add_wishlist_item_web()`
3. Concurrent requests:
   - Discogs service searches and fetches prices: `app/services/discogs.py`
   - Shopify service searches 6 Australian stores: `app/services/shopify.py`
4. Results stored in database: `app/models.py:Listing`
5. Deal notifications sent if configured: `app/services/notifier.py`

**Scheduled Scan Flow:**
1. APScheduler runs every `SCAN_INTERVAL_HOURS`: `app/scheduler.py`
2. Iterates all active wishlist items: `app/models.py:WishlistItem`
3. Calls scanner for each item: `app/services/scanner.py:scan_item()`
4. New listings stored, deals notified (if item.notify_email=true)
5. Existing listings updated with stock status

**Price Calculation:**
- All prices displayed as "landed cost": listing price + estimated shipping to Australia
- Shipping cost from: `app/services/shipping.py:get_shipping_cost()`
- Estimate defaults to: `SHIPPING_ESTIMATE_USD` (20.0 USD)

---

*Integration audit: 2026-04-02*
