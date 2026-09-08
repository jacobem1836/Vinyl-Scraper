"""Versioned schema migrations.

`run_migrations()` runs at startup:
  1. `create_all` creates any table that does not exist yet (fresh databases get the full schema).
  2. Any column present in the ORM models but missing from an existing table is added (nullable).
  3. Numbered migrations in MIGRATIONS run once each, recorded in `schema_migrations`.

Keep migrations idempotent and dialect-aware; local dev is SQLite, production is Postgres.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, inspect, text
from sqlalchemy.engine import Connection, Engine

from app.config import settings
from app.database import Base
import app.models as models  # noqa: F401  (registers tables on Base)


class SchemaMigration(Base):
    __tablename__ = "schema_migrations"

    version = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)


def _add_missing_columns(conn: Connection) -> list[str]:
    """Add any ORM column missing from an existing table. Always nullable; app code fills values."""
    insp = inspect(conn)
    added = []
    for table in Base.metadata.sorted_tables:
        existing = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name in existing:
                continue
            ddl = col.type.compile(dialect=conn.dialect)
            conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN "{col.name}" {ddl}'))
            added.append(f"{table.name}.{col.name}")
    return added


def _fix_sqlite_users_table(conn: Connection) -> None:
    """Legacy SQLite dev DBs created `users` with a Postgres SERIAL id, which never autoincrements.
    Rebuild the table so ids are real INTEGER PRIMARY KEY values."""
    if conn.dialect.name != "sqlite":
        return
    tables = {r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
    if "users_legacy" not in tables:
        row = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")).fetchone()
        if not row or "SERIAL" not in (row[0] or ""):
            return
        conn.execute(text("ALTER TABLE users RENAME TO users_legacy"))
    # From here on we may be recovering from an earlier run that renamed but did not finish.
    conn.execute(text("DROP INDEX IF EXISTS ix_users_email"))  # index names are global in SQLite
    tables = {r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
    if "users" not in tables:
        models.User.__table__.create(conn)
    conn.execute(text(
        "INSERT INTO users (email, password_hash, created_at) "
        "SELECT l.email, l.password_hash, l.created_at FROM users_legacy l "
        "WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.email = l.email)"
    ))
    conn.execute(text("DROP TABLE users_legacy"))
    print("[migrate] rebuilt sqlite users table (legacy SERIAL id)")


def _assign_legacy_owner(conn: Connection) -> None:
    """Pre-auth wishlist rows have no owner. Give them to LEGACY_OWNER_EMAIL, creating that user
    with an unusable password if needed (they set one via password reset or the CLI)."""
    orphans = conn.execute(text("SELECT COUNT(*) FROM wishlist_items WHERE user_id IS NULL")).scalar()
    if not orphans:
        return
    email = (settings.legacy_owner_email or "").strip().lower()
    if not email:
        print(f"[migrate] {orphans} wishlist rows have no owner; set LEGACY_OWNER_EMAIL to assign them")
        return
    uid = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).scalar()
    if uid is None:
        conn.execute(
            text("INSERT INTO users (email, password_hash, email_verified_at, created_at) VALUES (:e, :h, :now, :now)"),
            {"e": email, "h": "!unusable", "now": datetime.utcnow()},
        )
        uid = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).scalar()
    conn.execute(text("UPDATE wishlist_items SET user_id = :u WHERE user_id IS NULL"), {"u": uid})
    print(f"[migrate] assigned {orphans} legacy wishlist rows to {email}")


def _m001_multiuser(conn: Connection) -> None:
    _assign_legacy_owner(conn)
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_wishlist_items_user_id ON wishlist_items (user_id)"))
    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_listing_item_url ON listings (wishlist_item_id, url)"))
    # Legacy rows predate last_seen_at; treat them as seen now so they are not deactivated on the next scan.
    conn.execute(text("UPDATE listings SET last_seen_at = found_at WHERE last_seen_at IS NULL"))


MIGRATIONS: list[tuple[int, str, callable]] = [
    (1, "multiuser", _m001_multiuser),
]


def run_migrations(engine: Engine) -> None:
    with engine.begin() as conn:
        _fix_sqlite_users_table(conn)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        added = _add_missing_columns(conn)
        if added:
            print(f"[migrate] added columns: {', '.join(added)}")
        applied = {r[0] for r in conn.execute(text("SELECT version FROM schema_migrations"))}
        for version, name, fn in MIGRATIONS:
            if version in applied:
                continue
            fn(conn)
            conn.execute(
                text("INSERT INTO schema_migrations (version, name, applied_at) VALUES (:v, :n, :t)"),
                {"v": version, "n": name, "t": datetime.utcnow()},
            )
            print(f"[migrate] applied {version:03d}_{name}")
