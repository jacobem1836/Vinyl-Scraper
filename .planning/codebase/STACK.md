# Technology Stack

**Analysis Date:** 2026-04-02

## Languages

**Primary:**
- Python 3.11+ - Web application, API, background jobs, scraping
  - Currently running: Python 3.14.3
  - See: `app/main.py`, `app/models.py`, `bulk_import.py`

## Runtime

**Environment:**
- CPython runtime (Python virtual environment)
- Asyncio for async/await operations

**Package Manager:**
- pip (Python package manager)
- Lockfile: `requirements.txt` (pinned versions)

## Frameworks

**Core Web:**
- FastAPI 0.115.0 - REST API and web application framework
  - See: `app/main.py`, `app/routers/wishlist.py`

**Web Server:**
- Uvicorn 0.32.0 - ASGI application server
  - Configured in: `railway.toml`, `Procfile`
  - Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Database ORM:**
- SQLAlchemy 2.0.36 - SQL database toolkit and ORM
  - See: `app/database.py`, `app/models.py`

**Database Drivers:**
- aiosqlite 0.20.0 - Async SQLite driver (development)
- pg8000 1.31.2 - PostgreSQL driver (production)
  - See: `app/database.py` (line 6-7) - dynamic dialect switching
  - Used on Railway with PostgreSQL service

**HTTP Client:**
- httpx 0.28.0 - Async HTTP client library
  - See: `app/services/discogs.py`, `app/services/shopify.py`

**Templating:**
- Jinja2 3.1.4 - HTML template engine
  - Templates directory: `templates/`
  - See: `app/main.py` (line 17)

**Background Jobs:**
- APScheduler 3.10.4 - Advanced Python Scheduler
  - Configured in: `app/scheduler.py`
  - Runs recurring scans on configurable intervals

**Configuration:**
- Pydantic Settings 2.6.0 - Settings management from environment
  - See: `app/config.py`

**Multipart Handling:**
- python-multipart 0.0.12 - ASGI multipart form data parsing
  - Used by FastAPI for form submission handling

## Key Dependencies

**Critical:**
- FastAPI - Core web framework for REST API and templated HTML responses
- SQLAlchemy - Database abstraction and ORM for persistent storage
- httpx - Concurrent HTTP requests to external stores (Discogs, Shopify)
- APScheduler - Background job scheduling for periodic scans
- Uvicorn - ASGI server for both local development and production deployment

**Infrastructure:**
- pg8000 - PostgreSQL adapter for Railway deployment
- aiosqlite - SQLite for local development (zero-config database)
- Jinja2 - HTML template rendering for web dashboard

## Configuration

**Environment:**
- Configuration via `.env` file (not committed)
- Loaded by: `app/config.py` using `pydantic_settings.BaseSettings`
- Fallback defaults provided for development

**Build:**
- Nixpacks builder configured in `railway.toml`
- Python version detection from project files
- No explicit build step; dependencies installed from `requirements.txt`

## Platform Requirements

**Development:**
- Python 3.11+
- Virtual environment: `venv/`
- Local SQLite database: `vinyl.db`
- SMTP credentials (optional, for email alerts)

**Production:**
- Railway (or any platform supporting Python ASGI applications)
- PostgreSQL database service
- Environment variables for configuration (see README section "Configuration")
- Port binding via `$PORT` environment variable (default 8000)

---

*Stack analysis: 2026-04-02*
