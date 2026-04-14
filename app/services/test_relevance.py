from app.services.relevance import score_listing


def test_exact_album_scores_high():
    assert score_listing("Kid A", "Radiohead", "Radiohead - Kid A (2000 UK 1st press)") >= 85.0


def test_wrong_album_same_artist_scores_low():
    # Core bug this phase fixes: a Kid A scan returning OK Computer
    assert score_listing("Kid A", "Radiohead", "Radiohead - OK Computer") < 70.0


def test_empty_inputs_do_not_crash():
    assert isinstance(score_listing("", "", "title"), float)
    assert score_listing("", "", "") == 0.0


def test_artist_optional():
    assert score_listing("Kid A", "", "Kid A") >= 85.0


def test_case_and_punctuation_insensitive():
    a = score_listing("Kid A", "Radiohead", "Radiohead - Kid A")
    b = score_listing("kid a", "radiohead", "radiohead - KID A!")
    assert abs(a - b) <= 5.0
