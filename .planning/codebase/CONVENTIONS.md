# Coding Conventions

**Analysis Date:** 2026-04-02

## Naming Patterns

**Files:**
- Lowercase with underscores: `models.py`, `discogs.py`, `scanner.py`
- Router files: `wishlist.py` (module-scoped routers)
- Service files: one module per external integration or domain (`scanner.py`, `notifier.py`, `shipping.py`)
- Main app entry: `main.py`

**Functions:**
- Lowercase with underscores: `get_db()`, `scan_item()`, `compute_typical_price()`
- Private/internal functions prefixed with single underscore: `_get_album_listings()`, `_build_listing()`, `_enrich_item()`, `_landed()`
- Async functions use `async def` and named descriptively: `async def scan_item()`, `async def send_deal_email()`

**Variables:**
- Lowercase with underscores: `new_listings`, `best_price`, `total_cost`, `active_priced`
- Temporary variables in comprehensions: short names like `l` for listing, `i` for item
- Boolean variables: `is_active`, `is_in_stock`, `notify_email`, `should_notify()`

**Types/Classes:**
- PascalCase: `WishlistItem`, `Listing`, `Settings`, `WishlistItemResponse`
- Pydantic models: suffixed with intent (`Create`, `Update`, `Response`): `WishlistItemCreate`, `WishlistItemUpdate`, `WishlistItemResponse`

## Code Style

**Formatting:**
- No linting/formatting config detected (no `.eslintrc`, `.prettierrc`, `black` config, `flake8` config)
- Python formatting appears to follow PEP 8 conventions manually
- Indentation: 4 spaces
- Line length: Generally under 100 characters (inferred from code samples)
- String quotes: Double quotes preferred (`"key"`, `"value"`)
- Imports: 4 spaces per indent level

**Linting:**
- No linter configuration detected in repository
- Code follows PEP 8 style by convention

## Import Organization

**Order:**
1. Standard library imports (e.g., `import asyncio`, `from datetime import datetime`)
2. Third-party library imports (e.g., `from fastapi import`, `import httpx`, `from sqlalchemy import`)
3. Local application imports (e.g., `from app.config import settings`, `from app.services import discogs`)

**Path Aliases:**
- No path aliases detected
- Absolute imports from project root: `from app.config import settings`, `from app.database import get_db`
- No relative imports observed

**Examples:**
```python
# app/routers/wishlist.py - ordering observed
from fastapi import APIRouter, Depends, Form, Header, HTTPException  # fastapi
from fastapi.responses import RedirectResponse                       # fastapi submodule
from sqlalchemy.orm import Session                                   # sqlalchemy

from app.config import settings                                      # local
from app.database import get_db                                      # local
from app.models import Listing, WishlistItem                         # local
```

## Error Handling

**Patterns:**
- HTTP exceptions raised explicitly: `raise HTTPException(status_code=404, detail="Item not found")`
- Exception swallowing with `pass` in migrations and API error handlers: `except Exception: pass`
- Print-based logging for errors: `print(f"[Discogs] Error scanning '{query}': {e}")`
- Graceful degradation: returning empty lists on errors instead of raising
- Try-except blocks catch broad `Exception` types, often with logging before silent failure

**Example:**
```python
# app/services/discogs.py
try:
    # business logic
except Exception as e:
    print(f"[Discogs] Error scanning '{query}': {e}")
    return []
```

## Logging

**Framework:** Console via `print()` statements

**Patterns:**
- Prefixed log messages with service name in brackets: `print(f"[Discogs] Error...")`
- Used in error scenarios and exception handlers
- No structured logging or log level separation observed
- No logging configuration file

**Examples:**
```python
print(f"[Discogs] Error scanning '{query}': {e}")
print(f"[Shopify] Error querying {store['key']}: {exc}")
print(f"[Notifier] Failed to send email: {e}")
```

## Comments

**When to Comment:**
- Inline comments explain non-obvious business logic
- Comments on schema columns document intent: `type = Column(String, nullable=False)        # "album", "artist", or "label"`
- Comments on model fields document purpose: `notify_below_pct = Column(Float, nullable=False, default=20.0)  # notify when listing is X% below median price`
- Minimal function-level comments; function names are generally self-documenting

**JSDoc/TSDoc:**
- Used in Python docstrings for helper functions
- Format: triple-quoted docstring with brief description
- Example:
```python
def compute_typical_price(listings: list[Listing]) -> float | None:
    """Compute the median landed price (price + AU shipping) across active priced listings."""
```

## Function Design

**Size:** 
- Small to medium functions (5-20 lines typical)
- Longer functions when they contain list comprehensions or sequential API calls
- Example: `_get_album_listings()` is ~50 lines due to API call chaining and error handling

**Parameters:**
- FastAPI route handlers use dependency injection via `Depends()`: `db: Session = Depends(get_db)`
- Form handlers use `Form()` for web form parsing: `query: str = Form(...)`
- Helper functions pass instances directly

**Return Values:**
- Explicit type hints used throughout: `async def scan_item(db: Session, item: WishlistItem) -> list[Listing]:`
- Functions return data structures (dicts, lists) rather than objects
- Optional returns: `float | None`, `list[dict] | None`

**Example structure:**
```python
# Simple sync helper
def _landed(listing: Listing) -> float:
    """Return listing price + estimated shipping to Australia."""
    return listing.price + get_shipping_cost(listing.ships_from, settings.shipping_estimate_usd)

# Async API handler
async def scan_item(db: Session, item: WishlistItem) -> list[Listing]:
    discogs_results, shopify_results = await asyncio.gather(...)
    # ... process results
    return new_listings
```

## Module Design

**Exports:**
- Modules export public functions and classes (no explicit `__all__`)
- Services expose async search functions: `search_and_get_listings()`
- Router modules expose `api_router` and `web_router` objects

**Barrel Files:**
- Services use `__init__.py` to re-export from submodules: `from app.services import notifier, scanner`
- `app/__init__.py` is empty (imports handled in `main.py`)

**Example structure:**
```python
# app/services/__init__.py (empty or minimal imports)
from app.services import discogs, shopify, scanner, notifier
```

## Type Hints

**Style:**
- Type hints used consistently throughout function signatures
- Union types with `|` syntax (Python 3.10+): `str | None`, `list[dict]`
- Pydantic BaseModel for request/response schemas
- SQLAlchemy ORM models with Column type hints

**Examples:**
```python
async def search_and_get_listings(query: str, item_type: str, max_results: int = 5) -> list[dict]:
def _landed(listing: Listing) -> float:
def compute_typical_price(listings: list[Listing]) -> float | None:
```

## Database Query Patterns

**Observed:**
- SQLAlchemy ORM query syntax: `db.query(WishlistItem).filter_by(...).first()`
- Chained filters: `.filter_by(is_active=True).order_by(WishlistItem.created_at.desc())`
- Explicit commits: `db.commit()` and `db.refresh()`
- Session cleanup in finally blocks

**Example:**
```python
item = db.query(WishlistItem).filter_by(id=item_id, is_active=True).first()
if not item:
    raise HTTPException(status_code=404, detail="Item not found")
```

## Async/Await Patterns

**When Used:**
- Route handlers are async for database operations
- External API calls use async HTTP: `async with httpx.AsyncClient() as client:`
- Multiple concurrent API calls use `asyncio.gather()`: `await asyncio.gather(discogs.search_and_get_listings(), shopify.search_and_get_listings())`
- Email sending uses `asyncio.to_thread()` for blocking I/O: `await asyncio.to_thread(_send_smtp, ...)`

**Example:**
```python
async def scan_item(db: Session, item: WishlistItem) -> list[Listing]:
    discogs_results, shopify_results = await asyncio.gather(
        discogs.search_and_get_listings(item.query, item.type),
        shopify.search_and_get_listings(item.query, item.type),
    )
```

---

*Convention analysis: 2026-04-02*
