import re

from app.models import User, WaitlistEntry

LINK_RE = re.compile(r'href="(http://testserver/[^"]+)"')


def _link(mail):
    m = LINK_RE.search(mail["html"])
    assert m, mail["html"]
    return m.group(1).replace("http://testserver", "")


def test_signup_sends_verification_and_verify_link_works(browser, sent_emails, db):
    browser.signup("a@example.com")
    user = db.query(User).filter_by(email="a@example.com").one()
    assert user.is_verified is False
    assert sent_emails and sent_emails[-1]["to"] == "a@example.com"
    r = browser.get(_link(sent_emails[-1]))
    assert r.status_code == 303
    db.refresh(user)
    assert user.is_verified is True


def test_invite_only_signup_requires_invited_waitlist_entry(browser, invite_signup, db):
    r = browser.post("/signup", {"email": "x@example.com", "password": "correct horse battery"})
    assert r.status_code == 200 and "invite" in r.text.lower()
    assert db.query(User).count() == 0

    db.add(WaitlistEntry(email="x@example.com"))
    db.commit()
    r = browser.post("/signup", {"email": "x@example.com", "password": "correct horse battery"})
    assert r.status_code == 200  # on the list but not invited yet

    from datetime import datetime
    db.query(WaitlistEntry).filter_by(email="x@example.com").update({"invited_at": datetime.utcnow()})
    db.commit()
    r = browser.post("/signup", {"email": "X@Example.com ", "password": "correct horse battery"})
    assert r.status_code == 303
    assert db.query(User).filter_by(email="x@example.com").count() == 1


def test_waitlist_join_is_idempotent(browser, db):
    assert browser.post("/waitlist", {"email": "w@example.com"}).status_code == 303
    assert browser.post("/waitlist", {"email": "W@example.com"}).status_code == 303
    assert db.query(WaitlistEntry).count() == 1


def test_login_wrong_password_and_lockout(browser, sent_emails):
    browser.signup("a@example.com")
    browser.post("/logout")
    for _ in range(8):
        r = browser.post("/login", {"email": "a@example.com", "password": "wrong password!"})
        assert r.status_code == 200 and "Invalid email or password" in r.text
    r = browser.post("/login", {"email": "a@example.com", "password": "correct horse battery"})
    assert r.status_code == 429


def test_login_rotates_session_and_logout_clears(browser, sent_emails):
    browser.signup("a@example.com")
    before = browser.c.cookies.get("crate_session")
    browser.post("/logout")
    assert browser.get("/account").status_code == 303
    browser.login("a@example.com")
    assert browser.c.cookies.get("crate_session") != before
    assert browser.get("/account").status_code == 200


def test_csrf_required_on_forms_and_json(browser, sent_emails):
    browser.signup("a@example.com")
    r = browser.c.post("/wishlist/add", data={"type": "album", "query": "x"})
    assert r.status_code == 403
    assert browser.c.post("/api/scan/start").status_code == 403
    assert browser.c.post("/logout").status_code == 403


def test_password_reset_flow(browser, sent_emails, db):
    browser.signup("a@example.com")
    browser.post("/logout")
    r = browser.post("/forgot-password", {"email": "a@example.com"})
    assert r.status_code == 200
    link = _link(sent_emails[-1])
    assert browser.get(link).status_code == 200
    r = browser.post(link, {"password": "a brand new password"})
    assert r.status_code == 303
    assert browser.get(link).status_code == 400  # single use
    browser.post("/logout")
    browser.login("a@example.com", "a brand new password")
    assert db.query(User).filter_by(email="a@example.com").one().is_verified is True


def test_forgot_password_unknown_email_looks_identical(browser, sent_emails):
    r = browser.post("/forgot-password", {"email": "nobody@example.com"})
    assert r.status_code == 200 and not sent_emails


def test_change_password_requires_current(browser, sent_emails):
    browser.signup("a@example.com")
    r = browser.post("/account/password", {"current_password": "nope nope nope", "new_password": "another good one"})
    assert r.status_code == 200 and "incorrect" in r.text.lower()
    r = browser.post("/account/password", {"current_password": "correct horse battery", "new_password": "another good one"})
    assert r.status_code == 303
    browser.post("/logout")
    browser.login("a@example.com", "another good one")


def test_open_redirect_blocked(browser, sent_emails):
    browser.signup("a@example.com")
    browser.post("/logout")
    r = browser.post("/login", {"email": "a@example.com", "password": "correct horse battery", "next": "https://evil.example"})
    assert r.headers["location"] == "/"
    browser.post("/logout")
    r = browser.post("/login", {"email": "a@example.com", "password": "correct horse battery", "next": "//evil.example"})
    assert r.headers["location"] == "/"


def test_bad_form_input_is_422_not_500(browser, sent_emails):
    browser.signup("a@example.com")
    r = browser.post("/wishlist/add", {"type": "album", "query": "x", "notify_below_pct": "20", "notify_email": "", "discogs_release_id": "abc"})
    assert r.status_code == 422
    r = browser.post("/wishlist/add", {"type": "cassette", "query": "x", "notify_below_pct": "20", "notify_email": "", "discogs_release_id": ""})
    assert r.status_code == 422


def test_security_headers_and_no_docs(browser):
    r = browser.get("/login")
    assert r.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in r.headers
    assert browser.get("/docs").status_code == 404
    assert browser.get("/api/health").json() == {"status": "ok"}
