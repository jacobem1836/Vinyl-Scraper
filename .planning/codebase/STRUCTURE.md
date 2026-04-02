# Codebase Structure

**Analysis Date:** 2026-04-02

## Directory Layout

```
vinyl-scraper/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI app factory, route setup, startup/shutdown
│   ├── config.py           # Pydantic settings (env vars)
│   ├── database.py         # SQLAlchemy setup, session factory, migrations
│   ├── models.py           # ORM models (WishlistItem, Listing)
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── scheduler.py        # APScheduler setup and scheduled tasks
│   ├── routers/            # HTTP route handlers
│   │   ├── __init__.py
│   │   └── wishlist.py     # Web and API routes for wishlist CRUD, scanning, enrichment
│   └── services/           # Business logic layer
│       ├── __init__.py
│       ├── scanner.py      # Coordinates scraping from all sources
│       ├── discogs.py      # Discogs API adapter (search + listings)
│       ├── shopify.py      # Shopify store adapter (6 Australian retailers)
│       ├── notifier.py     # Email notifications, price threshold logic
│       └── shipping.py     # Shipping cost lookup table
├── templates/              # Jinja2 server-side templates
│   ├── base.html           # HTML layout template (nav, styles)
│   ├── index.html          # Dashboard view (all wishlist items)
│   └── item_detail.html    # Item detail view (all listings for one item)
├── static/                 # Static assets
│   └── style.css           # CSS stylesheet
├── bulk_import.py          # CLI script for batch-importing items from text file
├── requirements.txt        # Python dependencies
├── Procfile                # Railway deployment config (command to run)
├── railway.toml            # Railway service definition
├── README.md               # Project documentation
├── .env                    # Environment variables (secrets, config) — not committed
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
└── vinyl.db                # SQLite database (development only)
```

## Directory Purposes

**app/:**
- Purpose: Main Python package containing all application code
- Contains: Models, routes, services, config, database setup
- Key files: `main.py` (entry point), `models.py` (data schema)

**app/routers/:**
- Purpose: HTTP request handlers; entry point for web and API clients
- Contains: Route functions with dependency injection, template rendering, form handling
- Key files: `wishlist.py` (all routes for wishlist management and scanning)

**app/services/:**
- Purpose: Core business logic independent of HTTP layer
- Contains: Scraper adapters, notification logic, price computation, shipping data
- Key files: `scanner.py` (coordinates all sources), `discogs.py` and `shopify.py` (source adapters)

**templates/:**
- Purpose: Jinja2 server-side rendered HTML
- Contains: HTML pages for dashboard and item detail views
- Key files: `index.html` (dashboard with all items), `base.html` (layout)

**static/:**
- Purpose: Client-side assets
- Contains: CSS, (no JavaScript in this project)
- Key files: `style.css` (minimal styling)

## Key File Locations

**Entry Points:**
- `app/main.py`: FastAPI application factory; mounts routers, defines web page routes, configures startup/shutdown
- `bulk_import.py`: CLI script; entry point for batch importing items from text file

**Configuration:**
- `.env`: Environment variables (secrets like API keys, database URL) — never committed
- `.env.example`: Template showing required env vars
- `app/config.py`: Pydantic settings class; reads from `.env`
- `railway.toml`: Railway deployment config
- `Procfile`: Command to run app on Railway (`uvicorn app.main:app`)

**Core Logic:**
- `app/models.py`: SQLAlchemy ORM models (WishlistItem, Listing) — defines database schema
- `app/database.py`: Database engine, session factory, migration helpers
- `app/schemas.py`: Pydantic request/response schemas (validation, serialization)

**Route Handlers:**
- `app/routers/wishlist.py`: All HTTP routes (web pages, API endpoints)
  - Web routes: form-based CRUD (`/wishlist/add`, `/wishlist/{id}/edit`, `/wishlist/{id}/delete`, `/wishlist/{id}/scan`)
  - API routes: JSON-based endpoints (`/api/wishlist`, `/api/wishlist/{id}`, `/api/scan`)

**Business Logic (Services):**
- `app/services/scanner.py`: Main orchestrator; calls all source adapters, deduplicates, persists results
- `app/services/discogs.py`: Discogs API client (search, fetch marketplace listings)
- `app/services/shopify.py`: Shopify store adapter (searches 6 Australian retailers via `/search/suggest.json`)
- `app/services/notifier.py`: Email notification logic; price threshold computation; SMTP
- `app/services/shipping.py`: Shipping cost lookup table (country → USD cost to Australia)

**Background Scheduler:**
- `app/scheduler.py`: APScheduler setup; defines `scheduled_scan()` task (runs every 6 hours by default)

**Web Templates:**
- `templates/base.html`: HTML layout (nav, forms, CSS includes)
- `templates/index.html`: Dashboard listing all wishlist items with prices
- `templates/item_detail.html`: Detail page showing all listings for a single item

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `wishlist.py`, `discogs.py`, `notifier.py`)
- Templates: `snake_case.html` (e.g., `item_detail.html`, `base.html`)
- Static assets: `snake_case.css` (e.g., `style.css`)

**Directories:**
- Package directories: `snake_case` (e.g., `app/routers`, `app/services`)
- Template directory: `templates/`
- Static directory: `static/`

**Functions/Classes:**
- ORM models: PascalCase (e.g., `WishlistItem`, `Listing`)
- Pydantic schemas: PascalCase (e.g., `WishlistItemCreate`, `ListingResponse`)
- Route handlers: `snake_case` (e.g., `add_wishlist_item_web`, `scan_all_items_api`)
- Service functions: `snake_case` (e.g., `scan_item`, `send_deal_email`)
- Helper functions: `_snake_case` (private, e.g., `_enrich_item`, `_landed`)

**Database/ORM:**
- Table names: `snake_case_plural` (e.g., `wishlist_items`, `listings`)
- Column names: `snake_case` (e.g., `notify_below_pct`, `ships_from`)
- Foreign keys: `{table}_{column}` (e.g., `wishlist_item_id`)

## Where to Add New Code

**New Feature (e.g., new scraper):**
- Primary implementation: `app/services/{store_name}.py` (new adapter following `discogs.py`/`shopify.py` pattern)
- Orchestration: Update `app/services/scanner.py` to call new adapter in `scan_item()`
- Router changes: None needed (scanner handles all sources transparently)

**New HTTP Endpoint:**
- Implementation: Add route function to `app/routers/wishlist.py`
- Request schema: Add Pydantic class to `app/schemas.py` if needed
- Authentication: Use `Depends(require_api_key)` for API routes

**New Database Model:**
- Definition: Add SQLAlchemy class to `app/models.py`
- Migration: Add column-adding code to `app/database.py:run_migrations()` (handles schema evolution)

**New Template/Page:**
- Create: `templates/{page_name}.html`
- Route: Add GET handler to `app/routers/wishlist.py` calling `templates.TemplateResponse()`

**Utilities (shipping costs, price helpers, etc.):**
- Shared helpers: `app/services/{domain}.py` (e.g., `shipping.py` for logistics, pure functions)
- Or: Add to existing service file if closely related (e.g., `notifier.py` for price computation)

**CLI Tools:**
- Create: `{tool_name}.py` at project root (e.g., `bulk_import.py`)
- Pattern: Standalone script using HTTP client to call API endpoints (avoid importing `app/` code)

## Special Directories

**venv/:**
- Purpose: Python virtual environment
- Generated: Yes (created by `python -m venv venv`)
- Committed: No (in `.gitignore`)

**.git/:**
- Purpose: Git repository metadata
- Generated: Yes
- Committed: N/A

**.planning/codebase/:**
- Purpose: GSD mapper output (architecture/structure/conventions documents)
- Generated: Yes (by `/gsd:map-codebase` command)
- Committed: Yes (checked into repo)

**__pycache__/:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No (in `.gitignore`)

---

*Structure analysis: 2026-04-02*
