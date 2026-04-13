"""Fuzzy relevance scoring for scanned listings (FILTER-01, D-01/D-02)."""
from __future__ import annotations

import re

from rapidfuzz import fuzz


def _normalize(s: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def score_listing(item_query: str, item_artist: str, listing_title: str) -> float:
    """Score a listing title against the wishlist item's "artist query" combination.

    Per D-02: combined "{artist} {query}" disambiguates same-artist noise.
    Returns a float 0.0-100.0.

    Algorithm: min of two signals —
      1. partial_ratio(query, listing_title): does the album title appear in the listing?
      2. token_set_ratio(artist + query, listing_title): does the full combined target match?
    Taking the minimum prevents a strong artist match alone from inflating the score when
    the album title is absent (the core same-artist/wrong-album bug this phase fixes).
    Punctuation is stripped before scoring for consistent case/punctuation insensitivity.
    """
    query = _normalize(item_query)
    candidate = _normalize(listing_title)
    if not query or not candidate:
        return 0.0
    title_score = fuzz.partial_ratio(query, candidate)
    target = _normalize(f"{item_artist} {item_query}".strip())
    combined_score = fuzz.token_set_ratio(target, candidate)
    return float(min(title_score, combined_score))
