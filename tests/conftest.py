"""Shared pytest fixtures for Phase 15 notification tests."""
from types import SimpleNamespace
import pytest


@pytest.fixture
def mock_item():
    """Return a WishlistItem-like object with default notification attributes."""
    return SimpleNamespace(
        id=1,
        notify_email=True,
        notify_below_pct=20.0,
        notify_drop_mode="pct",
        notify_drop_pct=None,
        notify_drop_usd=None,
        last_notified_at=None,
        listings=[],
    )


@pytest.fixture
def mock_listing():
    """Factory fixture returning a function that creates Listing-like objects."""

    def _make(price=None, prev_price=None, is_in_stock=True, prev_is_in_stock=None, **kwargs):
        return SimpleNamespace(
            id=1,
            price=price,
            prev_price=prev_price,
            is_in_stock=is_in_stock,
            prev_is_in_stock=prev_is_in_stock,
            is_active=True,
            ships_from=None,
            **kwargs,
        )

    return _make


@pytest.fixture
def settings_override(monkeypatch):
    """Fixture that returns a helper to override app.config.settings attributes."""
    import app.config as cfg

    def _override(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setattr(cfg.settings, key, value)

    return _override
