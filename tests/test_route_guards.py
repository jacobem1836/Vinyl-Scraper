"""Tests for route guards (Phase 29, Plan 03).

Covers:
- Unauthenticated access to guarded web routes -> 303 redirect to /login?next=...
- Authenticated access to guarded web routes -> 200
- /api/health remains accessible without auth
- /api/wishlist with X-API-Key still works (iOS Shortcut contract)
- /api/wishlist without X-API-Key -> 401 or 422 (not 303)
- Session persistence (login + follow-up request with same cookies)
- /login and /signup accessible without auth
- /api/scan/start requires session or api key
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.config import settings
from app.database import Base, get_db
from app.main import app


# ──────────────────────────────────────────────────────────────
# In-memory SQLite test setup
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

    Patches scheduler start/shutdown to prevent APScheduler event loop issues.
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


def _signup_and_login(client, email="test@example.com", password="password123"):
    """Sign up then log in; returns the login response."""
    client.post("/signup", data={"email": email, "password": password, "next": ""}, follow_redirects=False)
    return client.post("/login", data={"email": email, "password": password, "next": ""}, follow_redirects=False)


# ──────────────────────────────────────────────────────────────
# Test 1: Unauthenticated GET / -> 303 with next=%2F
# ──────────────────────────────────────────────────────────────


def test_unauthenticated_index_redirects_to_login(client):
    """Unauthenticated GET / -> 303 with Location starting /login?next=%2F."""
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303
    location = r.headers.get("location", "")
    assert location.startswith("/login?next=%2F"), f"Expected /login?next=%2F, got: {location}"


# ──────────────────────────────────────────────────────────────
# Test 2: Unauthenticated GET /item/5 -> 303 with next=%2Fitem%2F5
# ──────────────────────────────────────────────────────────────


def test_unauthenticated_item_detail_redirects_to_login(client):
    """Unauthenticated GET /item/5 -> 303 with next=%2Fitem%2F5."""
    r = client.get("/item/5", follow_redirects=False)
    assert r.status_code == 303
    location = r.headers.get("location", "")
    assert "next=%2Fitem%2F5" in location, f"Expected next=%2Fitem%2F5 in location, got: {location}"


# ──────────────────────────────────────────────────────────────
# Test 3: Unauthenticated POST /wishlist/add -> 303 to /login
# ──────────────────────────────────────────────────────────────


def test_unauthenticated_add_wishlist_redirects_to_login(client):
    """Unauthenticated POST /wishlist/add -> 303 with Location starting /login."""
    r = client.post(
        "/wishlist/add",
        data={"type": "album", "query": "test", "notify_below_pct": "20"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    location = r.headers.get("location", "")
    assert "/login" in location, f"Expected /login in location, got: {location}"


# ──────────────────────────────────────────────────────────────
# Test 4: Unauthenticated POST /scan-all -> 303 to /login
# ──────────────────────────────────────────────────────────────


def test_unauthenticated_scan_all_redirects_to_login(client):
    """Unauthenticated POST /scan-all -> 303 with Location starting /login."""
    r = client.post("/scan-all", follow_redirects=False)
    assert r.status_code == 303
    location = r.headers.get("location", "")
    assert "/login" in location, f"Expected /login in location, got: {location}"


# ──────────────────────────────────────────────────────────────
# Test 5: GET /api/health -> 200 without auth
# ──────────────────────────────────────────────────────────────


def test_health_check_accessible_without_auth(client):
    """GET /api/health -> 200 with {"status": "ok"} without any auth."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ──────────────────────────────────────────────────────────────
# Test 6: GET /api/wishlist with valid X-API-Key -> 200
# ──────────────────────────────────────────────────────────────


def test_api_wishlist_with_api_key_returns_200(client):
    """GET /api/wishlist with valid X-API-Key -> 200 (iOS Shortcut contract)."""
    original_api_key = settings.api_key
    settings.api_key = "test-api-key-12345"
    try:
        r = client.get("/api/wishlist", headers={"X-API-Key": "test-api-key-12345"})
        assert r.status_code == 200
    finally:
        settings.api_key = original_api_key


# ──────────────────────────────────────────────────────────────
# Test 7: GET /api/wishlist without X-API-Key -> 401 or 422 (not 303)
# ──────────────────────────────────────────────────────────────


def test_api_wishlist_without_api_key_returns_401_or_422(client):
    """GET /api/wishlist without X-API-Key -> 401 or 422 (NOT 303 redirect)."""
    r = client.get("/api/wishlist", follow_redirects=False)
    # Must not be a redirect (which would break iOS Shortcut)
    assert r.status_code in (401, 422), f"Expected 401 or 422, got: {r.status_code}"


# ──────────────────────────────────────────────────────────────
# Test 8: Authenticated GET / -> 200 with user email in response
# ──────────────────────────────────────────────────────────────


def test_authenticated_index_returns_200_with_email(client):
    """Authenticated GET / -> 200 and the response body contains the user's email."""
    email = "auth-index@example.com"
    _signup_and_login(client, email=email)

    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200
    assert email in r.text, f"Expected '{email}' in response body"


# ──────────────────────────────────────────────────────────────
# Test 9: Session persistence — follow-up GET / after login stays 200
# ──────────────────────────────────────────────────────────────


def test_session_persists_after_login(client):
    """After login, a follow-up GET / using the same TestClient stays 200 (AUTH-03)."""
    _signup_and_login(client, email="persist@example.com")

    # Follow-up request with same TestClient (cookies are preserved automatically)
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200


# ──────────────────────────────────────────────────────────────
# Test 10: GET /login and GET /signup remain accessible without auth
# ──────────────────────────────────────────────────────────────


def test_login_and_signup_accessible_without_auth(client):
    """GET /login and GET /signup both return 200 without any auth."""
    r_login = client.get("/login")
    assert r_login.status_code == 200, f"GET /login returned {r_login.status_code}"

    r_signup = client.get("/signup")
    assert r_signup.status_code == 200, f"GET /signup returned {r_signup.status_code}"


# ──────────────────────────────────────────────────────────────
# Test 11: POST /api/scan/start with valid session -> 200
# ──────────────────────────────────────────────────────────────


def test_scan_start_requires_auth(client):
    """POST /api/scan/start without session or api key -> 303 to /login.
    POST /api/scan/start with valid session -> 200 (or {"started": ...}).
    """
    # Unauthenticated: should redirect to /login
    r_unauth = client.post("/api/scan/start", follow_redirects=False)
    assert r_unauth.status_code == 303, f"Expected 303 for unauthenticated scan/start, got: {r_unauth.status_code}"
    assert "/login" in r_unauth.headers.get("location", ""), "Expected /login in redirect location"

    # Authenticated: should succeed
    _signup_and_login(client, email="scanauth@example.com")
    r_auth = client.post("/api/scan/start", follow_redirects=False)
    # Accept 200 or 303 (if scan is already running — but on fresh test DB it should start)
    # The key is it's not redirecting to /login
    assert r_auth.status_code in (200, 303), f"Expected 200 or 303 for authenticated scan/start, got: {r_auth.status_code}"
    if r_auth.status_code == 303:
        # Should not redirect to /login
        assert "/login" not in r_auth.headers.get("location", ""), "Authenticated scan/start should not redirect to /login"
    else:
        # Should have a JSON body with "started" key
        data = r_auth.json()
        assert "started" in data, f"Expected 'started' key in response: {data}"
