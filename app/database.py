from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

_db_url = settings.database_url.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URL = _db_url

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Safely add new columns to existing databases."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # Add notify_below_pct if it doesn't exist (replaces price_ceiling)
        try:
            conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN notify_below_pct REAL NOT NULL DEFAULT 20.0"))
            conn.commit()
        except Exception:
            pass  # Column already exists
        try:
            conn.execute(text("ALTER TABLE listings ADD COLUMN ships_from TEXT"))
            conn.commit()
        except Exception:
            pass  # Column already exists
        try:
            conn.execute(text("ALTER TABLE listings ADD COLUMN is_in_stock INTEGER NOT NULL DEFAULT 1"))
            conn.commit()
        except Exception:
            pass  # Column already exists
        try:
            conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN artwork_url VARCHAR"))
            conn.commit()
        except Exception:
            pass  # column already exists
        try:
            conn.execute(text("DROP INDEX IF EXISTS ix_listings_url"))
            conn.commit()
        except Exception:
            pass  # index may not exist
        try:
            conn.execute(text('DROP INDEX IF EXISTS "uq_listings_url"'))
            conn.commit()
        except Exception:
            pass  # index may not exist
        # If listings table still has an inline UNIQUE (url) constraint, recreate without it.
        # SQLite does not support DROP CONSTRAINT so the table must be rebuilt.
        try:
            row = conn.execute(text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='listings'"
            )).fetchone()
            if row and "UNIQUE (url)" in row[0]:
                conn.execute(text("PRAGMA foreign_keys = OFF"))
                conn.execute(text("""
                    CREATE TABLE listings_new (
                        id INTEGER NOT NULL,
                        wishlist_item_id INTEGER NOT NULL,
                        source VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        price FLOAT,
                        currency VARCHAR,
                        condition VARCHAR,
                        seller VARCHAR,
                        url VARCHAR NOT NULL,
                        found_at DATETIME,
                        is_active BOOLEAN,
                        ships_from TEXT,
                        is_in_stock INTEGER NOT NULL DEFAULT 1,
                        PRIMARY KEY (id),
                        FOREIGN KEY(wishlist_item_id) REFERENCES wishlist_items (id)
                    )
                """))
                conn.execute(text(
                    "INSERT INTO listings_new SELECT id, wishlist_item_id, source, title, price, "
                    "currency, condition, seller, url, found_at, is_active, ships_from, is_in_stock "
                    "FROM listings"
                ))
                conn.execute(text("DROP TABLE listings"))
                conn.execute(text("ALTER TABLE listings_new RENAME TO listings"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_listings_id ON listings (id)"))
                conn.execute(text("PRAGMA foreign_keys = ON"))
                conn.commit()
        except Exception:
            pass  # non-SQLite or already migrated
        try:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_listing_item_url ON listings (wishlist_item_id, url)"))
            conn.commit()
        except Exception:
            pass  # index already exists
        try:
            conn.execute(text("ALTER TABLE wishlist_items ADD COLUMN discogs_release_id INTEGER"))
            conn.commit()
        except Exception:
            pass  # Column already exists
        try:
            conn.execute(text("ALTER TABLE listings ADD COLUMN image_url VARCHAR"))
            conn.commit()
        except Exception:
            pass  # Column already exists
        # Make notify_below_pct nullable (drop NOT NULL constraint).
        # PostgreSQL: ALTER COLUMN ... DROP NOT NULL
        try:
            conn.execute(text("ALTER TABLE wishlist_items ALTER COLUMN notify_below_pct DROP NOT NULL"))
            conn.execute(text("ALTER TABLE wishlist_items ALTER COLUMN notify_below_pct DROP DEFAULT"))
            conn.commit()
        except Exception:
            pass  # Already nullable or non-PostgreSQL
        # SQLite: cannot ALTER COLUMN — rebuild the table if NOT NULL is present on notify_below_pct.
        try:
            row = conn.execute(text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='wishlist_items'"
            )).fetchone()
            if row and "notify_below_pct" in row[0] and "NOT NULL" in row[0]:
                # Only rebuild if NOT NULL appears on the notify_below_pct column definition
                import re as _re
                col_match = _re.search(r"notify_below_pct[^,)]*NOT NULL", row[0])
                if col_match:
                    conn.execute(text("PRAGMA foreign_keys = OFF"))
                    conn.execute(text("""
                        CREATE TABLE wishlist_items_new (
                            id INTEGER NOT NULL,
                            type VARCHAR NOT NULL,
                            query VARCHAR NOT NULL,
                            notes VARCHAR,
                            notify_below_pct REAL,
                            notify_email BOOLEAN,
                            created_at DATETIME,
                            last_scanned_at DATETIME,
                            is_active BOOLEAN,
                            artwork_url VARCHAR,
                            discogs_release_id INTEGER,
                            PRIMARY KEY (id)
                        )
                    """))
                    conn.execute(text(
                        "INSERT INTO wishlist_items_new "
                        "SELECT id, type, query, notes, notify_below_pct, notify_email, "
                        "created_at, last_scanned_at, is_active, artwork_url, discogs_release_id "
                        "FROM wishlist_items"
                    ))
                    conn.execute(text("DROP TABLE wishlist_items"))
                    conn.execute(text("ALTER TABLE wishlist_items_new RENAME TO wishlist_items"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_wishlist_items_id ON wishlist_items (id)"))
                    conn.execute(text("PRAGMA foreign_keys = ON"))
                    conn.commit()
        except Exception:
            pass  # non-SQLite or already migrated
