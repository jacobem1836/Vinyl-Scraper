"""Scanner behaviour with fake adapters: upsert, price refresh, deactivation, relevance filter, events."""
import pytest
from sqlalchemy.orm import selectinload

from app.auth import hash_password
from app.models import Listing, User, WishlistItem
from app.services import notifier, scanner

RATES = {"AUD": 1.0, "USD": 1.5}


def _listing(url, price, **kw):
    d = {"source": "fakestore", "title": "Radiohead - OK Computer (LP)", "url": url, "price": price, "currency": "AUD", "ships_from": "Australia", "is_in_stock": True}
    d.update(kw)
    return d


def _fake_adapters(monkeypatch, *results_per_source):
    """Each entry is a list of listing dicts or an Exception to raise."""
    adapters = []
    for i, res in enumerate(results_per_source):
        async def fn(query, item_type, _res=res, **kw):
            if isinstance(_res, Exception):
                raise _res
            return list(_res)
        adapters.append({"name": f"src{i}", "fn": fn, "enabled": True})
    monkeypatch.setattr(scanner, "get_enabled_adapters", lambda: adapters)


@pytest.fixture
def item(db):
    user = User(email="a@example.com", password_hash=hash_password("correct horse battery"))
    db.add(user)
    db.flush()
    it = WishlistItem(user_id=user.id, type="album", query="Radiohead - OK Computer", is_active=True)
    db.add(it)
    db.commit()
    return db.get(WishlistItem, it.id, options=[selectinload(WishlistItem.listings)])


@pytest.mark.anyio
async def test_scan_creates_then_updates_price_and_snapshots_previous(db, item, monkeypatch):
    _fake_adapters(monkeypatch, [_listing("https://s/1", 40.0)])
    res = await scanner.scan_item(db, item)
    assert len(res.new_listings) == 1 and res.failed_sources == []
    l = db.query(Listing).one()
    assert l.price == 40.0 and l.prev_price is None and l.is_active and l.relevance_score == 100.0

    _fake_adapters(monkeypatch, [_listing("https://s/1", 30.0)])
    res = await scanner.scan_item(db, item)
    assert res.new_listings == []
    db.refresh(l)
    assert l.price == 30.0 and l.prev_price == 40.0
    assert notifier.price_dropped(l)


@pytest.mark.anyio
async def test_missing_listing_is_deactivated_only_when_its_source_succeeded(db, item, monkeypatch):
    _fake_adapters(monkeypatch, [_listing("https://s/1", 40.0, source="src0")], [_listing("https://t/1", 45.0, source="src1")])
    await scanner.scan_item(db, item)
    assert db.query(Listing).filter_by(is_active=True).count() == 2

    # src0 now returns nothing (listing gone); src1 fails outright (listing must survive)
    _fake_adapters(monkeypatch, [], RuntimeError("boom"))
    res = await scanner.scan_item(db, item)
    assert res.failed_sources == ["src1"]
    gone = db.query(Listing).filter_by(url="https://s/1").one()
    kept = db.query(Listing).filter_by(url="https://t/1").one()
    assert gone.is_active is False and gone.is_in_stock is False
    assert kept.is_active is True

    # it comes back -> reactivated and flagged back in stock
    _fake_adapters(monkeypatch, [_listing("https://s/1", 40.0, source="src0")], [])
    await scanner.scan_item(db, item)
    db.refresh(gone)
    assert gone.is_active and gone.is_in_stock and notifier.back_in_stock(gone)


@pytest.mark.anyio
async def test_irrelevant_and_digital_listings_are_not_stored(db, item, monkeypatch):
    _fake_adapters(monkeypatch, [
        _listing("https://s/bends", 40.0, title="Radiohead - The Bends"),
        _listing("https://s/flac", 10.0, title="OK Computer [FLAC download]"),
        _listing("https://s/ok", 40.0),
    ])
    res = await scanner.scan_item(db, item)
    assert [l.url for l in res.new_listings] == ["https://s/ok"]
    assert res.hidden_low_relevance == 1


@pytest.mark.anyio
async def test_deal_detection_uses_typical_of_other_listings(db, item, monkeypatch):
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)])
    await scanner.scan_item(db, item)
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)] + [_listing("https://s/cheap", 60.0)])
    res = await scanner.scan_item(db, item)
    events = notifier.collect_events(item, res.new_listings, RATES)
    assert events and [l.url for l in events["deal_alerts"]] == ["https://s/cheap"]
    assert events["price_drops"] == [] and events["back_in_stock"] == []


@pytest.mark.anyio
async def test_scan_user_sends_one_digest_to_verified_user_only(db, item, monkeypatch, sent_emails):
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)])
    await scanner.scan_user(item.user_id, notify=True)
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)] + [_listing("https://s/cheap", 50.0)])
    await scanner.scan_user(item.user_id, notify=True)
    assert sent_emails == []  # unverified

    from datetime import datetime
    db.query(User).update({"email_verified_at": datetime.utcnow()})
    db.commit()
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)] + [_listing("https://s/cheap", 50.0), _listing("https://s/cheaper", 45.0)])
    await scanner.scan_user(item.user_id, notify=True)
    assert len(sent_emails) == 1 and "cheaper" in sent_emails[0]["html"]
    db.expire_all()
    assert db.get(WishlistItem, item.id).last_notified_at is not None

    # cooldown: another deal immediately after does not email again
    _fake_adapters(monkeypatch, [_listing(f"https://s/{i}", 100.0) for i in range(3)] + [_listing("https://s/cheapest", 40.0)])
    await scanner.scan_user(item.user_id, notify=True)
    assert len(sent_emails) == 1
