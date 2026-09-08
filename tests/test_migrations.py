"""Migrating a legacy (pre-auth, SQLite) database must add columns, fix the users table and assign an owner."""
import os
import tempfile

from sqlalchemy import inspect, text

from app.config import settings
from app.database import make_engine
from app.migrations import run_migrations

LEGACY_SCHEMA = """
CREATE TABLE wishlist_items (
    id INTEGER NOT NULL PRIMARY KEY, type VARCHAR NOT NULL, query VARCHAR NOT NULL, notes VARCHAR,
    notify_below_pct REAL NOT NULL DEFAULT 20.0, notify_email BOOLEAN, created_at DATETIME,
    last_scanned_at DATETIME, is_active BOOLEAN, artwork_url VARCHAR, discogs_release_id INTEGER
);
CREATE TABLE listings (
    id INTEGER NOT NULL PRIMARY KEY, wishlist_item_id INTEGER NOT NULL, source VARCHAR NOT NULL, title VARCHAR NOT NULL,
    price FLOAT, currency VARCHAR, condition VARCHAR, seller VARCHAR, url VARCHAR NOT NULL, found_at DATETIME,
    is_active BOOLEAN, ships_from TEXT, is_in_stock INTEGER NOT NULL DEFAULT 1, image_url VARCHAR,
    FOREIGN KEY(wishlist_item_id) REFERENCES wishlist_items (id)
);
CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR NOT NULL UNIQUE, password_hash VARCHAR NOT NULL, created_at TIMESTAMP);
CREATE UNIQUE INDEX ix_users_email ON users (email);
INSERT INTO wishlist_items (type, query, is_active, created_at) VALUES ('album', 'OK Computer', 1, '2026-04-01');
INSERT INTO listings (wishlist_item_id, source, title, price, currency, url, found_at, is_active) VALUES (1, 'discogs', 'OK Computer', 40, 'USD', 'https://x/1', '2026-04-02', 1);
INSERT INTO users (email, password_hash) VALUES ('jacob@example.com', '$2b$12$abc');
"""


def test_legacy_sqlite_db_migrates_cleanly(monkeypatch):
    path = os.path.join(tempfile.mkdtemp(), "legacy.db")
    eng = make_engine(f"sqlite:///{path}")
    with eng.begin() as conn:
        for stmt in LEGACY_SCHEMA.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
    monkeypatch.setattr(settings, "legacy_owner_email", "jacob@example.com")

    run_migrations(eng)
    run_migrations(eng)  # idempotent

    insp = inspect(eng)
    cols = {c["name"] for c in insp.get_columns("wishlist_items")}
    assert {"user_id", "last_notified_at"} <= cols
    lcols = {c["name"] for c in insp.get_columns("listings")}
    assert {"prev_price", "prev_is_in_stock", "last_seen_at", "relevance_score"} <= lcols
    assert "waitlist" in insp.get_table_names() and "schema_migrations" in insp.get_table_names()

    with eng.connect() as conn:
        uid, email = conn.execute(text("SELECT id, email FROM users")).one()
        assert uid == 1 and email == "jacob@example.com"  # SERIAL table rebuilt with a real id
        assert conn.execute(text("SELECT user_id FROM wishlist_items")).scalar() == uid
        assert conn.execute(text("SELECT last_seen_at FROM listings")).scalar() is not None
        assert conn.execute(text("SELECT COUNT(*) FROM schema_migrations")).scalar() == 1


def test_legacy_owner_created_when_missing(monkeypatch):
    path = os.path.join(tempfile.mkdtemp(), "legacy2.db")
    eng = make_engine(f"sqlite:///{path}")
    with eng.begin() as conn:
        for stmt in LEGACY_SCHEMA.strip().split(";"):
            if stmt.strip() and "INSERT INTO users" not in stmt:
                conn.execute(text(stmt))
    monkeypatch.setattr(settings, "legacy_owner_email", "owner@example.com")
    run_migrations(eng)
    with eng.connect() as conn:
        row = conn.execute(text("SELECT email, password_hash, email_verified_at FROM users")).one()
        assert row[0] == "owner@example.com" and row[1] == "!unusable" and row[2] is not None
