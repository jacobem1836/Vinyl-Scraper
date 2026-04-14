"""Failing unit tests for Phase 15 notification helpers.

These tests describe the behaviour of _price_dropped, _back_in_stock,
_within_cooldown, and send_digest_email — functions that will be added to
app.services.notifier by Plan 03.

RED state is expected: import will fail until Plan 03 implements the helpers.
"""
import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.notifier import (
    _back_in_stock,
    _price_dropped,
    _within_cooldown,
    send_digest_email,
)


# ---------------------------------------------------------------------------
# NOTIF-01: Back-in-stock detection
# ---------------------------------------------------------------------------


def test_back_in_stock(mock_listing):
    """prev_is_in_stock=False + is_in_stock=True fires event."""
    listing = mock_listing(is_in_stock=True, prev_is_in_stock=False)
    assert _back_in_stock(listing) is True


def test_back_in_stock_first_scan(mock_listing):
    """prev_is_in_stock=None (first scan) does NOT fire event."""
    listing = mock_listing(is_in_stock=True, prev_is_in_stock=None)
    assert _back_in_stock(listing) is False


# ---------------------------------------------------------------------------
# NOTIF-02: Price-drop detection
# ---------------------------------------------------------------------------


def test_price_drop_pct(mock_item, mock_listing, settings_override):
    """Drop of 30% >= 20% threshold in pct mode fires event."""
    settings_override(notify_drop_pct_default=20.0)
    item = mock_item
    item.notify_drop_mode = "pct"
    item.notify_drop_pct = None  # use global default
    listing = mock_listing(prev_price=100.0, price=70.0)
    assert _price_dropped(listing, item) is True


def test_price_drop_usd(mock_item, mock_listing, settings_override):
    """Drop of $7 >= $5 threshold in usd mode fires event."""
    settings_override(notify_drop_usd_default=5.0)
    item = mock_item
    item.notify_drop_mode = "usd"
    item.notify_drop_usd = None  # use global default
    listing = mock_listing(prev_price=100.0, price=93.0)
    assert _price_dropped(listing, item) is True


def test_price_drop_no_prev(mock_item, mock_listing):
    """prev_price=None (first scan) does NOT fire event."""
    listing = mock_listing(prev_price=None, price=70.0)
    assert _price_dropped(listing, mock_item) is False


# ---------------------------------------------------------------------------
# NOTIF-03: Cool-down / deduplication
# ---------------------------------------------------------------------------


def test_cooldown_suppresses(settings_override):
    """last_notified_at = now - 1h with 24h cooldown → within cooldown → True."""
    settings_override(notify_cooldown_hours=24)
    last_notified_at = datetime.utcnow() - timedelta(hours=1)
    assert _within_cooldown(last_notified_at) is True


def test_cooldown_expired(settings_override):
    """last_notified_at = now - 48h with 24h cooldown → outside cooldown → False."""
    settings_override(notify_cooldown_hours=24)
    last_notified_at = datetime.utcnow() - timedelta(hours=48)
    assert _within_cooldown(last_notified_at) is False


# ---------------------------------------------------------------------------
# NOTIF-04: Digest email aggregation
# ---------------------------------------------------------------------------


def test_no_digest_on_zero_events():
    """send_digest_email with empty list sends no email and returns False/None."""
    with patch("app.services.notifier._send_smtp") as mock_smtp:
        result = asyncio.run(send_digest_email([]))
    assert not result
    mock_smtp.assert_not_called()


def test_digest_aggregates(mock_item, mock_listing, settings_override):
    """Two items with events → exactly one _send_smtp call; subject contains event count."""
    settings_override(
        smtp_user="test@example.com",
        smtp_password="secret",
        notify_email="dest@example.com",
    )

    listing_a = mock_listing(price=50.0, prev_price=80.0)
    listing_b = mock_listing(is_in_stock=True, prev_is_in_stock=False)

    item_a = mock_item
    item_b = mock_item

    digest_items = [
        (item_a, {"deal_alerts": [], "price_drops": [(listing_a, 80.0, 50.0)], "back_in_stock": []}),
        (item_b, {"deal_alerts": [], "price_drops": [], "back_in_stock": [listing_b]}),
    ]

    with patch("app.services.notifier._send_smtp") as mock_smtp:
        result = asyncio.run(send_digest_email(digest_items))

    assert result is True
    assert mock_smtp.call_count == 1
    subject_arg = mock_smtp.call_args[0][0]
    assert "2" in subject_arg  # total event count across items
