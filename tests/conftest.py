"""Shared fixtures. The app is imported against a throwaway SQLite file so migrations run for real."""
import os
import re
import tempfile

_TMP = tempfile.mkdtemp(prefix="crate-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["ENV"] = "development"
os.environ["SIGNUP_MODE"] = "open"
os.environ["RESEND_API_KEY"] = ""
os.environ["APP_URL"] = "http://testserver"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app import auth as auth_mod  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.scheduler import scheduler  # noqa: E402
from app.services import mailer, scan_status  # noqa: E402

CSRF_RE = re.compile(r'name="csrf_token" value="([^"]+)"')


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def _app_started():
    with TestClient(app) as c:  # runs lifespan (migrations) once
        yield c
    if scheduler.running:
        scheduler.shutdown(wait=False)


@pytest.fixture(autouse=True)
def _clean_db(_app_started):
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name != "schema_migrations":
                conn.execute(text(f"DELETE FROM {table.name}"))
    auth_mod.limiter.reset()
    scan_status._state.clear()


@pytest.fixture
def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def sent_emails(monkeypatch):
    """Capture outbound emails instead of sending."""
    box: list[dict] = []

    async def fake_send(to, subject, html):
        box.append({"to": to, "subject": subject, "html": html})
        return True

    monkeypatch.setattr(mailer, "send_email", fake_send)
    monkeypatch.setattr(mailer, "is_configured", lambda: True)
    return box


class Browser:
    """A TestClient with helpers for CSRF-protected forms."""

    def __init__(self):
        self.c = TestClient(app, follow_redirects=False)

    def csrf(self, path="/login") -> str:
        html = self.c.get(path).text
        m = CSRF_RE.search(html)
        assert m, f"no csrf field on {path}"
        return m.group(1)

    def post(self, path, data=None, **kw):
        data = dict(data or {})
        data["csrf_token"] = self.csrf()
        return self.c.post(path, data=data, **kw)

    def post_json(self, path, **kw):
        return self.c.post(path, headers={"X-CSRF-Token": self.csrf()}, **kw)

    def get(self, path, **kw):
        return self.c.get(path, **kw)

    def signup(self, email, password="correct horse battery"):
        r = self.post("/signup", {"email": email, "password": password})
        assert r.status_code == 303, r.text
        return self

    def login(self, email, password="correct horse battery"):
        r = self.post("/login", {"email": email, "password": password})
        assert r.status_code == 303, r.text
        return self

    def add_item(self, query, **extra):
        data = {"type": "album", "query": query, "notify_below_pct": "20", "notify_email": "on", "discogs_release_id": ""}
        data.update(extra)
        r = self.post("/wishlist/add", data)
        assert r.status_code == 303, r.text
        return self


@pytest.fixture
def browser(_app_started, sent_emails):
    return Browser()


@pytest.fixture
def browser2(_app_started, sent_emails):
    return Browser()


@pytest.fixture
def open_signup(monkeypatch):
    monkeypatch.setattr(settings, "signup_mode", "open")


@pytest.fixture
def invite_signup(monkeypatch):
    monkeypatch.setattr(settings, "signup_mode", "invite")
