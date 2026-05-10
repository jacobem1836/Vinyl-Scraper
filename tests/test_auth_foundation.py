"""Tests for auth foundation (Phase 29, Plan 01).

Tests 1-5: bcrypt hashing and User model (Task 1).
Tests 6-8: current_user session logic (Task 2).
"""

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from types import SimpleNamespace


# ──────────────────────────────────────────────────────────────
# Tests 1-3: bcrypt hashing (app.auth created in Task 2 — RED until then)
# ──────────────────────────────────────────────────────────────

def test_hash_password_produces_bcrypt_string():
    """hash_password returns a string starting with '$2b$'."""
    from app.auth import hash_password
    result = hash_password("hunter2")
    assert isinstance(result, str)
    assert result.startswith("$2b$"), f"Expected $2b$ prefix, got: {result[:10]}"
    assert result != "hunter2"


def test_verify_password_matches():
    """verify_password returns True when plaintext matches the stored hash."""
    from app.auth import hash_password, verify_password
    h = hash_password("hunter2")
    assert verify_password("hunter2", h) is True


def test_verify_password_rejects_mismatch():
    """verify_password returns False when plaintext does not match the stored hash."""
    from app.auth import hash_password, verify_password
    h = hash_password("hunter2")
    assert verify_password("wrong", h) is False


# ──────────────────────────────────────────────────────────────
# Test 4: User model has expected columns
# ──────────────────────────────────────────────────────────────

def test_user_model_columns():
    """User model has columns: id, email, password_hash, created_at with email unique."""
    from app.models import User
    columns = {c.name for c in User.__table__.columns}
    required = {"id", "email", "password_hash", "created_at"}
    assert required.issubset(columns), f"Missing columns: {required - columns}"

    # email column should have unique=True
    email_col = User.__table__.columns["email"]
    assert email_col.nullable is False, "email column must be NOT NULL"


# ──────────────────────────────────────────────────────────────
# Test 5: users table is created by Base.metadata.create_all
# ──────────────────────────────────────────────────────────────

def test_users_table_created():
    """After Base.metadata.create_all on a fresh sqlite DB, the users table exists."""
    from app.database import Base
    from app.models import User  # noqa: F401 — ensures User registered on Base

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables, f"users table not found; tables: {tables}"

    col_names = {c["name"] for c in inspector.get_columns("users")}
    expected = {"id", "email", "password_hash", "created_at"}
    assert expected.issubset(col_names), f"Missing columns: {expected - col_names}"

    engine.dispose()


# ──────────────────────────────────────────────────────────────
# Tests 6-8: current_user session logic (app.auth created in Task 2 — RED until then)
# ──────────────────────────────────────────────────────────────

def _make_request(session_data: dict):
    """Build a fake Request-like stub with a .session dict."""
    return SimpleNamespace(session=session_data, url=SimpleNamespace(path="/", query=""))


def _make_db_with_user(email="test@example.com", password_hash="$2b$12$fake"):
    """Return an in-memory sqlite session containing one User row."""
    from app.database import Base
    from app.models import User

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return db, user, engine


def test_current_user_returns_none_when_no_session():
    """current_user returns None when session has no user_id key."""
    from app.auth import current_user
    db, user, engine = _make_db_with_user()
    request = _make_request({})
    result = current_user(request, db)
    assert result is None
    db.close()
    engine.dispose()


def test_current_user_returns_user_for_valid_session():
    """current_user returns the User row when session['user_id'] is a valid id."""
    from app.auth import current_user
    db, user, engine = _make_db_with_user()
    request = _make_request({"user_id": user.id})
    result = current_user(request, db)
    assert result is not None
    assert result.id == user.id
    assert result.email == user.email
    db.close()
    engine.dispose()


def test_current_user_returns_none_for_nonexistent_user():
    """current_user returns None when session['user_id'] points to a non-existent user."""
    from app.auth import current_user
    db, user, engine = _make_db_with_user()
    request = _make_request({"user_id": 9999})
    result = current_user(request, db)
    assert result is None
    db.close()
    engine.dispose()
