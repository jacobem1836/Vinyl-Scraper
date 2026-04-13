from app.services.digital_filter import is_digital


def test_mp3_format_dropped():
    assert is_digital({"format": "MP3"}) is True


def test_vinyl_not_dropped():
    assert is_digital({"format": "Vinyl"}) is False


def test_bandcamp_digital_item_type():
    assert is_digital({"item_type": "digital track"}) is True


def test_flac_in_title():
    assert is_digital({"title": "Flying Lotus - Cosmogramma [FLAC 24bit]"}) is True


def test_vinyl_with_benign_title():
    assert is_digital({"format": "Vinyl", "title": "Cosmogramma"}) is False


def test_empty_listing_not_dropped():
    assert is_digital({}) is False


def test_case_insensitive():
    assert is_digital({"format": "mp3"}) is True
    assert is_digital({"format": "Mp3"}) is True


def test_format_as_list():
    assert is_digital({"format": ["Vinyl", "FLAC"]}) is True
    assert is_digital({"format": ["Vinyl", "LP"]}) is False
