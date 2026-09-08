from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url.replace("postgres://", "postgresql://", 1)
IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")


def make_engine(url: str = SQLALCHEMY_DATABASE_URL):
    if url.startswith("sqlite"):
        eng = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(eng, "connect")
        def _sqlite_pragmas(dbapi_conn, _record):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

        return eng
    # ponytail: NullPool so no idle connection keeps Neon's compute awake (that was the bill).
    # Switch to QueuePool(pool_recycle=280, pool_pre_ping=True) only if per-request connect latency matters.
    return create_engine(url, poolclass=NullPool, pool_pre_ping=True)


engine = make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
