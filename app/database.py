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
    with engine.connect() as conn:
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
