<!-- GSD:project-start source:PROJECT.md -->
## Project

**Vinyl Wishlist Manager**

A personal vinyl record wishlist manager that scrapes multiple stores and marketplaces to track prices and availability for records you want to buy. You add records you're after; it finds them across the web, computes landed costs (including shipping to AU), and alerts you to deals. Accessed via a web dashboard and an iOS Shortcut for quick adds.

**Core Value:** Show me the cheapest way to buy the records I want, right now.

### Constraints

- **Compatibility:** iOS Shortcut API contract (`POST /api/wishlist`, `X-API-Key`) must not break
- **Deployment:** Railway + PostgreSQL; no infrastructure changes unless clearly better
- **Scraping:** Respect robots.txt / rate limits; scraper sources must be feasible (public listings, no login required)
- **Solo project:** No team overhead; keep architecture simple
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11+ - Web application, API, background jobs, scraping
## Runtime
- CPython runtime (Python virtual environment)
- Asyncio for async/await operations
- pip (Python package manager)
- Lockfile: `requirements.txt` (pinned versions)
## Frameworks
- FastAPI 0.115.0 - REST API and web application framework
- Uvicorn 0.32.0 - ASGI application server
- SQLAlchemy 2.0.36 - SQL database toolkit and ORM
- aiosqlite 0.20.0 - Async SQLite driver (development)
- pg8000 1.31.2 - PostgreSQL driver (production)
- httpx 0.28.0 - Async HTTP client library
- Jinja2 3.1.4 - HTML template engine
- APScheduler 3.10.4 - Advanced Python Scheduler
- Pydantic Settings 2.6.0 - Settings management from environment
- python-multipart 0.0.12 - ASGI multipart form data parsing
## Key Dependencies
- FastAPI - Core web framework for REST API and templated HTML responses
- SQLAlchemy - Database abstraction and ORM for persistent storage
- httpx - Concurrent HTTP requests to external stores (Discogs, Shopify)
- APScheduler - Background job scheduling for periodic scans
- Uvicorn - ASGI server for both local development and production deployment
- pg8000 - PostgreSQL adapter for Railway deployment
- aiosqlite - SQLite for local development (zero-config database)
- Jinja2 - HTML template rendering for web dashboard
## Configuration
- Configuration via `.env` file (not committed)
- Loaded by: `app/config.py` using `pydantic_settings.BaseSettings`
- Fallback defaults provided for development
- Nixpacks builder configured in `railway.toml`
- Python version detection from project files
- No explicit build step; dependencies installed from `requirements.txt`
## Platform Requirements
- Python 3.11+
- Virtual environment: `venv/`
- Local SQLite database: `vinyl.db`
- SMTP credentials (optional, for email alerts)
- Railway (or any platform supporting Python ASGI applications)
- PostgreSQL database service
- Environment variables for configuration (see README section "Configuration")
- Port binding via `$PORT` environment variable (default 8000)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Lowercase with underscores: `models.py`, `discogs.py`, `scanner.py`
- Router files: `wishlist.py` (module-scoped routers)
- Service files: one module per external integration or domain (`scanner.py`, `notifier.py`, `shipping.py`)
- Main app entry: `main.py`
- Lowercase with underscores: `get_db()`, `scan_item()`, `compute_typical_price()`
- Private/internal functions prefixed with single underscore: `_get_album_listings()`, `_build_listing()`, `_enrich_item()`, `_landed()`
- Async functions use `async def` and named descriptively: `async def scan_item()`, `async def send_deal_email()`
- Lowercase with underscores: `new_listings`, `best_price`, `total_cost`, `active_priced`
- Temporary variables in comprehensions: short names like `l` for listing, `i` for item
- Boolean variables: `is_active`, `is_in_stock`, `notify_email`, `should_notify()`
- PascalCase: `WishlistItem`, `Listing`, `Settings`, `WishlistItemResponse`
- Pydantic models: suffixed with intent (`Create`, `Update`, `Response`): `WishlistItemCreate`, `WishlistItemUpdate`, `WishlistItemResponse`
## Code Style
- No linting/formatting config detected (no `.eslintrc`, `.prettierrc`, `black` config, `flake8` config)
- Python formatting appears to follow PEP 8 conventions manually
- Indentation: 4 spaces
- Line length: Generally under 100 characters (inferred from code samples)
- String quotes: Double quotes preferred (`"key"`, `"value"`)
- Imports: 4 spaces per indent level
- No linter configuration detected in repository
- Code follows PEP 8 style by convention
## Import Organization
- No path aliases detected
- Absolute imports from project root: `from app.config import settings`, `from app.database import get_db`
- No relative imports observed
## Error Handling
- HTTP exceptions raised explicitly: `raise HTTPException(status_code=404, detail="Item not found")`
- Exception swallowing with `pass` in migrations and API error handlers: `except Exception: pass`
- Print-based logging for errors: `print(f"[Discogs] Error scanning '{query}': {e}")`
- Graceful degradation: returning empty lists on errors instead of raising
- Try-except blocks catch broad `Exception` types, often with logging before silent failure
## Logging
- Prefixed log messages with service name in brackets: `print(f"[Discogs] Error...")`
- Used in error scenarios and exception handlers
- No structured logging or log level separation observed
- No logging configuration file
## Comments
- Inline comments explain non-obvious business logic
- Comments on schema columns document intent: `type = Column(String, nullable=False)        # "album", "artist", or "label"`
- Comments on model fields document purpose: `notify_below_pct = Column(Float, nullable=False, default=20.0)  # notify when listing is X% below median price`
- Minimal function-level comments; function names are generally self-documenting
- Used in Python docstrings for helper functions
- Format: triple-quoted docstring with brief description
- Example:
## Function Design
- Small to medium functions (5-20 lines typical)
- Longer functions when they contain list comprehensions or sequential API calls
- Example: `_get_album_listings()` is ~50 lines due to API call chaining and error handling
- FastAPI route handlers use dependency injection via `Depends()`: `db: Session = Depends(get_db)`
- Form handlers use `Form()` for web form parsing: `query: str = Form(...)`
- Helper functions pass instances directly
- Explicit type hints used throughout: `async def scan_item(db: Session, item: WishlistItem) -> list[Listing]:`
- Functions return data structures (dicts, lists) rather than objects
- Optional returns: `float | None`, `list[dict] | None`
## Module Design
- Modules export public functions and classes (no explicit `__all__`)
- Services expose async search functions: `search_and_get_listings()`
- Router modules expose `api_router` and `web_router` objects
- Services use `__init__.py` to re-export from submodules: `from app.services import notifier, scanner`
- `app/__init__.py` is empty (imports handled in `main.py`)
## Type Hints
- Type hints used consistently throughout function signatures
- Union types with `|` syntax (Python 3.10+): `str | None`, `list[dict]`
- Pydantic BaseModel for request/response schemas
- SQLAlchemy ORM models with Column type hints
## Database Query Patterns
- SQLAlchemy ORM query syntax: `db.query(WishlistItem).filter_by(...).first()`
- Chained filters: `.filter_by(is_active=True).order_by(WishlistItem.created_at.desc())`
- Explicit commits: `db.commit()` and `db.refresh()`
- Session cleanup in finally blocks
## Async/Await Patterns
- Route handlers are async for database operations
- External API calls use async HTTP: `async with httpx.AsyncClient() as client:`
- Multiple concurrent API calls use `asyncio.gather()`: `await asyncio.gather(discogs.search_and_get_listings(), shopify.search_and_get_listings())`
- Email sending uses `asyncio.to_thread()` for blocking I/O: `await asyncio.to_thread(_send_smtp, ...)`
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- FastAPI web framework for HTTP endpoints (REST API + server-side rendered pages)
- Modular service layer for business logic (scraping, notifications, shipping calculations)
- Background job scheduler for periodic scanning
- SQLAlchemy ORM for database abstraction (SQLite locally, PostgreSQL in production)
- Clear separation between web routes, services, and data models
## Layers
- Purpose: Handle incoming requests, render templates, enforce API authentication
- Location: `app/routers/wishlist.py`, `app/main.py`
- Contains: Route handlers for web pages and API endpoints
- Depends on: Services, database, Pydantic schemas
- Used by: HTTP clients (browsers, iOS Shortcut, external API consumers)
- Purpose: Execute core domain logic independent of HTTP
- Location: `app/services/` directory
- Contains: Scanner (coordinates scraping), notifier (email alerts), Discogs/Shopify adapters, shipping cost lookup
- Depends on: Models, database, external APIs, configuration
- Used by: Routers, scheduler
- Purpose: Define data structure and persistence
- Location: `app/models.py`, `app/database.py`
- Contains: SQLAlchemy ORM models (WishlistItem, Listing), database engine, session factory
- Depends on: SQLAlchemy, configuration
- Used by: All other layers
- Purpose: Environment-based settings and app initialization
- Location: `app/config.py`, `app/main.py` startup hooks
- Contains: Pydantic settings, database migrations, scheduler setup
- Depends on: Environment variables
- Used by: All layers
## Data Flow
- State lives in PostgreSQL/SQLite database
- Web routes query database per request (no in-memory caching)
- Background scheduler maintains long-lived session for periodic tasks
- No shared state between HTTP requests; each request gets fresh DB session via `Depends(get_db)`
## Key Abstractions
- Purpose: Represents a user's search query (album, artist, label, subject)
- Examples: `app/models.py:WishlistItem`
- Pattern: SQLAlchemy ORM model with relationships to Listing
- Purpose: Individual product found across all sources for a WishlistItem
- Examples: `app/models.py:Listing`
- Pattern: Unique by URL; deduplication on scan; tracks stock status and pricing
- Purpose: Encapsulate scraping logic for each store/API
- Examples: `app/services/discogs.py`, `app/services/shopify.py`
- Pattern: Async functions `search_and_get_listings(query, item_type)` returning standardized dict list
- Purpose: Coordinates scraping from all sources, deduplicates results, persists to database
- Examples: `app/services/scanner.py`
- Pattern: `async def scan_item(db, item)` returns newly created Listing rows
- Purpose: Computes typical price, determines deal threshold, sends email alerts
- Examples: `app/services/notifier.py`
- Pattern: Pure functions for price calculation; async email dispatch via thread pool
## Entry Points
- Location: `app/main.py`
- Triggers: `uvicorn app.main:app` command or Railway deployment
- Responsibilities: App factory, route mounting, startup/shutdown hooks (DB migrations, scheduler init)
- Location: `bulk_import.py`
- Triggers: `python bulk_import.py wishlist.txt`
- Responsibilities: Parse text file, POST items to `/api/wishlist/bulk` endpoint via HTTP
- Location: `app/routers/wishlist.py`
- Triggers: HTTP GET/POST/DELETE requests
- Responsibilities: Request validation, calling services, database queries, template rendering
- Location: `app/routers/wishlist.py` (api_router)
- Triggers: HTTP requests with `X-API-Key` header
- Responsibilities: JSON request/response, same business logic as web routes
- Location: `app/scheduler.py`
- Triggers: APScheduler fires at configured interval (default 6 hours)
- Responsibilities: Scan all active items, send emails for new deals
## Error Handling
- Source adapters (Discogs, Shopify) catch exceptions and return empty list on error (logged to stdout)
- Notifier catches SMTP errors, logs and returns False
- Database operations wrapped in try/finally to ensure session cleanup
- Route handlers raise `HTTPException` for validation failures, return 404 for missing items
- Scanner continues processing remaining items even if one fails
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
