from types import SimpleNamespace

from app.services.pricing import landed_aud, median, to_aud, typical_price
from app.services.relevance import is_digital, score_listing

RATES = {"AUD": 1.0, "USD": 1.5, "GBP": 2.0}


def test_to_aud_converts_and_passes_aud_through():
    assert to_aud(10, "USD", RATES) == 15.0
    assert to_aud(10, "aud", RATES) == 10.0
    assert to_aud(10, "GBP", RATES) == 20.0
    assert to_aud(10, "XXX", RATES) is None


def test_landed_converts_price_before_adding_aud_shipping():
    # GBP 10 -> A$20, plus UK shipping estimate A$28
    assert landed_aud(10, "GBP", "United Kingdom", RATES) == 48.0
    # unknown origin uses the configured fallback (30)
    assert landed_aud(10, "AUD", None, RATES) == 40.0
    assert landed_aud(None, "AUD", None, RATES) is None


def test_median_and_typical_price_ignore_inactive_and_out_of_stock():
    assert median([]) is None
    assert median([3, 1, 2]) == 2
    assert median([1, 2, 3, 4]) == 2.5
    mk = lambda p, active=True, stock=True: SimpleNamespace(price=p, currency="AUD", ships_from="Australia", is_active=active, is_in_stock=stock)
    listings = [mk(10), mk(20), mk(1000, active=False), mk(2000, stock=False), mk(None)]
    assert typical_price(listings, RATES) == 27.0  # (10+12 + 20+12)/2


def test_relevance_scores():
    assert score_listing("Radiohead - OK Computer", "OK Computer (2LP Reissue)") == 100.0
    assert score_listing("Radiohead - OK Computer", "Radiohead – OK Computer OKNOTOK 1997 2017") == 100.0
    assert score_listing("Radiohead - OK Computer", "Radiohead - The Bends") < 70
    assert score_listing("Kind of Blue", "Blue Train") < 70
    assert score_listing("", "anything") == 0.0


def test_digital_detection():
    assert is_digital("OK Computer [FLAC]")
    assert is_digital("OK Computer", "MP3 320")
    assert not is_digital("OK Computer (Vinyl LP)")
