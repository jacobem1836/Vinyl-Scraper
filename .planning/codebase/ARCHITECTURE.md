# Architecture

**Analysis Date:** 2026-04-02

## Pattern Overview

**Overall:** Layered monolith with async service architecture

**Key Characteristics:**
- FastAPI web framework for HTTP endpoints (REST API + server-side rendered pages)
- Modular service layer for business logic (scraping, notifications, shipping calculations)
- Background job scheduler for periodic scanning
- SQLAlchemy ORM for database abstraction (SQLite locally, PostgreSQL in production)
- Clear separation between web routes, services, and data models

## Layers

**Web Layer (HTTP):**
- Purpose: Handle incoming requests, render templates, enforce API authentication
- Location: `app/routers/wishlist.py`, `app/main.py`
- Contains: Route handlers for web pages and API endpoints
- Depends on: Services, database, Pydantic schemas
- Used by: HTTP clients (browsers, iOS Shortcut, external API consumers)

**Service Layer (Business Logic):**
- Purpose: Execute core domain logic independent of HTTP
- Location: `app/services/` directory
- Contains: Scanner (coordinates scraping), notifier (email alerts), Discogs/Shopify adapters, shipping cost lookup
- Depends on: Models, database, external APIs, configuration
- Used by: Routers, scheduler

**Data Layer (Models & Database):**
- Purpose: Define data structure and persistence
- Location: `app/models.py`, `app/database.py`
- Contains: SQLAlchemy ORM models (WishlistItem, Listing), database engine, session factory
- Depends on: SQLAlchemy, configuration
- Used by: All other layers

**Configuration & Bootstrap:**
- Purpose: Environment-based settings and app initialization
- Location: `app/config.py`, `app/main.py` startup hooks
- Contains: Pydantic settings, database migrations, scheduler setup
- Depends on: Environment variables
- Used by: All layers

## Data Flow

**Adding a Wishlist Item:**

1. User submits form (web) or API POST (iOS Shortcut)
2. Route handler validates input using Pydantic schema
3. Creates `WishlistItem` row in database
4. Calls `scanner.scan_item()` with the new item
5. Scanner concurrently calls `discogs.search_and_get_listings()` and `shopify.search_and_get_listings()`
6. Each source returns list of `Listing` dicts with price, title, URL
7. Scanner deduplicates by URL, creates new `Listing` rows, commits to database
8. If `notify_email=True` and new listings found, notifier computes typical price and sends email alert
9. Route redirects to dashboard or returns enriched item JSON

**Background Scanning (Scheduled):**

1. APScheduler fires `scheduled_scan()` every N hours (default 6)
2. Fetches all active `WishlistItem` rows
3. For each item, calls `scan_item()` (same flow as above)
4. Checks `should_notify()` for each new listing (price ≥ X% below typical price)
5. Sends deal emails for items with `notify_email=True` and notifiable listings
6. Updates `last_scanned_at` timestamp

**Displaying Dashboard:**

1. GET `/` route fetches all active `WishlistItem` rows
2. Calls `_enrich_item()` for each item to compute:
   - Best price (lowest landed cost among all active priced listings)
   - Typical price (median of all active priced listings)
   - Top 3 cheapest listings
   - Total listing count
3. Computes aggregate stats (total cost, cheapest item, most expensive item)
4. Renders `index.html` template with enriched data

**State Management:**
- State lives in PostgreSQL/SQLite database
- Web routes query database per request (no in-memory caching)
- Background scheduler maintains long-lived session for periodic tasks
- No shared state between HTTP requests; each request gets fresh DB session via `Depends(get_db)`

## Key Abstractions

**WishlistItem:**
- Purpose: Represents a user's search query (album, artist, label, subject)
- Examples: `app/models.py:WishlistItem`
- Pattern: SQLAlchemy ORM model with relationships to Listing

**Listing:**
- Purpose: Individual product found across all sources for a WishlistItem
- Examples: `app/models.py:Listing`
- Pattern: Unique by URL; deduplication on scan; tracks stock status and pricing

**Source Adapters:**
- Purpose: Encapsulate scraping logic for each store/API
- Examples: `app/services/discogs.py`, `app/services/shopify.py`
- Pattern: Async functions `search_and_get_listings(query, item_type)` returning standardized dict list

**Scanner:**
- Purpose: Coordinates scraping from all sources, deduplicates results, persists to database
- Examples: `app/services/scanner.py`
- Pattern: `async def scan_item(db, item)` returns newly created Listing rows

**Notifier:**
- Purpose: Computes typical price, determines deal threshold, sends email alerts
- Examples: `app/services/notifier.py`
- Pattern: Pure functions for price calculation; async email dispatch via thread pool

## Entry Points

**Main Application:**
- Location: `app/main.py`
- Triggers: `uvicorn app.main:app` command or Railway deployment
- Responsibilities: App factory, route mounting, startup/shutdown hooks (DB migrations, scheduler init)

**CLI Bulk Import:**
- Location: `bulk_import.py`
- Triggers: `python bulk_import.py wishlist.txt`
- Responsibilities: Parse text file, POST items to `/api/wishlist/bulk` endpoint via HTTP

**Web Routes:**
- Location: `app/routers/wishlist.py`
- Triggers: HTTP GET/POST/DELETE requests
- Responsibilities: Request validation, calling services, database queries, template rendering

**API Routes:**
- Location: `app/routers/wishlist.py` (api_router)
- Triggers: HTTP requests with `X-API-Key` header
- Responsibilities: JSON request/response, same business logic as web routes

**Background Scheduler:**
- Location: `app/scheduler.py`
- Triggers: APScheduler fires at configured interval (default 6 hours)
- Responsibilities: Scan all active items, send emails for new deals

## Error Handling

**Strategy:** Fail gracefully; continue processing on individual failures

**Patterns:**
- Source adapters (Discogs, Shopify) catch exceptions and return empty list on error (logged to stdout)
- Notifier catches SMTP errors, logs and returns False
- Database operations wrapped in try/finally to ensure session cleanup
- Route handlers raise `HTTPException` for validation failures, return 404 for missing items
- Scanner continues processing remaining items even if one fails

## Cross-Cutting Concerns

**Logging:** Print statements to stdout (captured by Railway logs); no external logging service

**Validation:** Pydantic schemas for API input (`WishlistItemCreate`, `ListingResponse`); form validation in routes

**Authentication:** API key header validation (`require_api_key` dependency); web routes unauthenticated

**Landed Price Calculation:** Centralized in `_landed()` helper across routers and services; relies on shipping cost lookup table and fallback estimate

---

*Architecture analysis: 2026-04-02*
