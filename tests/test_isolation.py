"""User A must never be able to see or touch User B's data through any route."""
from app.models import WishlistItem
from app.services import scan_status


def _item_id(db, email):
    return db.query(WishlistItem).join(WishlistItem.user).filter_by(email=email).one().id


def test_dashboard_shows_only_own_items(browser, browser2, db):
    browser.signup("a@example.com").add_item("Radiohead - OK Computer")
    browser2.signup("b@example.com").add_item("Miles Davis - Kind of Blue")
    a_home = browser.get("/").text
    b_home = browser2.get("/").text
    assert "OK Computer" in a_home and "Kind of Blue" not in a_home
    assert "Kind of Blue" in b_home and "OK Computer" not in b_home


def test_item_routes_reject_other_users(browser, browser2, db):
    browser.signup("a@example.com").add_item("Radiohead - OK Computer")
    browser2.signup("b@example.com")
    item_id = _item_id(db, "a@example.com")

    assert browser2.get(f"/item/{item_id}").status_code == 404
    assert browser2.get(f"/wishlist/{item_id}/status").status_code == 404
    assert browser2.post(f"/wishlist/{item_id}/delete").status_code == 404
    r = browser2.post(f"/wishlist/{item_id}/edit", {"type": "album", "query": "hijacked", "notify_below_pct": "20", "notify_email": "", "discogs_release_id": ""})
    assert r.status_code == 404
    assert browser2.post_json(f"/api/scan/start?item_id={item_id}").status_code == 404

    # Owner is unaffected
    assert browser.get(f"/item/{item_id}").status_code == 200
    assert db.get(WishlistItem, item_id).query == "Radiohead - OK Computer"


def test_scan_status_is_per_user(browser, browser2, db):
    browser.signup("a@example.com")
    browser2.signup("b@example.com")
    a_id = db.query(WishlistItem.user_id).count()  # noqa: F841  (touch db)
    from app.models import User
    a = db.query(User).filter_by(email="a@example.com").one()
    scan_status.start(a.id, total=3)
    scan_status.item_started(a.id, 1, "secret query", "album")
    assert browser.get("/api/scan/status").json()["is_running"] is True
    b_status = browser2.get("/api/scan/status").json()
    assert b_status["is_running"] is False and b_status["current"] == []


def test_anonymous_is_redirected_or_401(browser, db):
    assert browser.get("/item/1").status_code == 303
    assert browser.get("/account").status_code == 303
    assert browser.get("/api/scan/status").status_code == 401
    assert browser.c.post("/api/scan/start").status_code in (401, 403)


def test_delete_account_removes_everything(browser, db):
    browser.signup("a@example.com").add_item("Radiohead - OK Computer")
    assert db.query(WishlistItem).count() == 1
    r = browser.post("/account/delete", {"password": "correct horse battery"})
    assert r.status_code == 303
    db.expire_all()
    assert db.query(WishlistItem).count() == 0
    assert browser.get("/account").status_code == 303  # logged out
