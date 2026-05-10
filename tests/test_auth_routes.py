"""Tests for auth routes (Phase 29, Plan 02).

Covers /login, /signup, /logout endpoints with session management.
Uses an in-memory SQLite database override.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.database import Base, get_db
from app.main import app


# ──────────────────────────────────────────────────────────────
# In-memory SQLite test setup
#
# StaticPool forces all connections to share the same underlying SQLite
# in-memory database connection — required because SQLite `:memory:` is
# per-connection, so without StaticPool each new connection sees an empty DB.
# ──────────────────────────────────────────────────────────────


@pytest.fixture()
def db_engine():
    """Create a shared in-memory SQLite engine per test with StaticPool."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Create a fresh session per test."""
    TestingSession = sessionmaker(bind=db_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient with get_db overridden to use the test session.

    We patch the scheduler start/shutdown to prevent APScheduler from trying
    to interact with a closed event loop when TestClient triggers lifecycle hooks.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with (
        patch("app.main.scheduler.start"),
        patch("app.main.scheduler.shutdown"),
        patch("app.main.setup_scheduler"),
    ):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _signup(client, email="user@example.com", password="password123", next_=""):
    data = {"email": email, "password": password, "next": next_}
    return client.post("/signup", data=data, follow_redirects=False)


def _login(client, email="user@example.com", password="password123", next_=""):
    data = {"email": email, "password": password, "next": next_}
    return client.post("/login", data=data, follow_redirects=False)


# ──────────────────────────────────────────────────────────────
# Test 1: GET /login returns 200 with expected content
# ──────────────────────────────────────────────────────────────

def test_get_login_returns_200(client):
    """GET /login returns 200 and HTML containing 'Sign in' and form action='/login'."""
    r = client.get("/login")
    assert r.status_code == 200
    assert "Sign in" in r.text
    assert 'action="/login"' in r.text


# ──────────────────────────────────────────────────────────────
# Test 2: GET /signup returns 200 with expected content
# ──────────────────────────────────────────────────────────────

def test_get_signup_returns_200(client):
    """GET /signup returns 200 and HTML containing 'Create account' and form action='/signup'."""
    r = client.get("/signup")
    assert r.status_code == 200
    assert "Create account" in r.text
    assert 'action="/signup"' in r.text


# ──────────────────────────────────────────────────────────────
# Test 3: POST /signup creates a user and redirects
# ──────────────────────────────────────────────────────────────

def test_post_signup_creates_user_and_redirects(client, db_session):
    """POST /signup creates a User row with bcrypt hash and 303 redirects to '/'."""
    from app.models import User

    r = _signup(client, email="a@b.com", password="password123")
    assert r.status_code == 303
    assert r.headers["location"] == "/"

    user = db_session.query(User).filter_by(email="a@b.com").first()
    assert user is not None
    assert user.password_hash.startswith("$2b$")


# ──────────────────────────────────────────────────────────────
# Test 4: POST /signup with duplicate email returns 200 with error
# ──────────────────────────────────────────────────────────────

def test_post_signup_duplicate_email_returns_error(client, db_session):
    """POST /signup with a duplicate email returns 200 with 'already' and creates no second user."""
    from app.models import User

    _signup(client, email="dup@example.com", password="password123")
    r = _signup(client, email="dup@example.com", password="password456")

    assert r.status_code == 200
    assert "already" in r.text.lower()

    count = db_session.query(User).filter_by(email="dup@example.com").count()
    assert count == 1


# ──────────────────────────────────────────────────────────────
# Test 5: POST /login with valid creds sets session and redirects
# ──────────────────────────────────────────────────────────────

def test_post_login_valid_creds_redirects_and_sets_session(client):
    """POST /login with valid credentials returns 303 to '/' and sets crate_session cookie."""
    _signup(client, email="login@example.com", password="password123")
    r = _login(client, email="login@example.com", password="password123")

    assert r.status_code == 303
    assert r.headers["location"] == "/"
    # The session cookie should be set
    assert "crate_session" in r.cookies or any(
        "crate_session" in str(c) for c in r.cookies
    )


# ──────────────────────────────────────────────────────────────
# Test 6: POST /login with wrong password returns 200 with error
# ──────────────────────────────────────────────────────────────

def test_post_login_wrong_password_returns_error(client):
    """POST /login with wrong password returns 200 and HTML containing 'Invalid'."""
    _signup(client, email="bad@example.com", password="password123")
    r = _login(client, email="bad@example.com", password="wrongpassword")

    assert r.status_code == 200
    assert "Invalid" in r.text


# ──────────────────────────────────────────────────────────────
# Test 7: ?next= roundtrip in signup and login
# ──────────────────────────────────────────────────────────────

def test_next_param_redirects_to_specified_path(client):
    """POST /signup or /login with next=/item/5 redirects to '/item/5' (303)."""
    # Test via signup
    r = _signup(client, email="next@example.com", password="password123", next_="/item/5")
    assert r.status_code == 303
    assert r.headers["location"] == "/item/5"

    # Test via login (use a different email to avoid duplicate)
    _signup(client, email="next2@example.com", password="password123")
    r2 = _login(client, email="next2@example.com", password="password123", next_="/item/5")
    assert r2.status_code == 303
    assert r2.headers["location"] == "/item/5"


# ──────────────────────────────────────────────────────────────
# Test 8: POST /logout clears session and redirects to /login
# ──────────────────────────────────────────────────────────────

def test_post_logout_clears_session_and_redirects(client):
    """POST /logout returns 303 to '/login'."""
    _signup(client, email="logout@example.com", password="password123")
    _login(client, email="logout@example.com", password="password123")

    r = client.post("/logout", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


# ──────────────────────────────────────────────────────────────
# Test 9: POST /signup with short password returns error and creates no user
# ──────────────────────────────────────────────────────────────

def test_post_signup_short_password_returns_error(client, db_session):
    """POST /signup with password < 8 chars returns 200 with error and creates no user."""
    from app.models import User

    r = _signup(client, email="short@example.com", password="abc")
    assert r.status_code == 200
    assert "characters" in r.text.lower() or "password" in r.text.lower()

    count = db_session.query(User).filter_by(email="short@example.com").count()
    assert count == 0
