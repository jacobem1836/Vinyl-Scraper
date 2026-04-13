"""Digital-listing detection (FILTER-02, D-08, D-09).

Drops listings that are MP3/FLAC/File/Digital/Lossless/WAV/AAC or Bandcamp
digital-only payloads. Runs at scan time; digital listings are never persisted.
"""
from __future__ import annotations

# Case-insensitive tokens matched as whole words or format-string substrings.
DIGITAL_FORMAT_TOKENS: tuple[str, ...] = (
    "file", "mp3", "flac", "digital", "lossless", "wav", "aac",
)


def _contains_digital_token(value: str) -> bool:
    if not value:
        return False
    lowered = value.lower()
    return any(tok in lowered for tok in DIGITAL_FORMAT_TOKENS)


def is_digital(listing: dict) -> bool:
    """Return True if the listing dict represents a digital-only release."""
    if not listing:
        return False

    # Check explicit format / item_type fields first.
    for key in ("format", "item_type"):
        val = listing.get(key)
        if isinstance(val, str) and _contains_digital_token(val):
            return True
        if isinstance(val, list):
            for entry in val:
                if isinstance(entry, str) and _contains_digital_token(entry):
                    return True

    # Fall back to title sniffing (catches Bandcamp "Album [FLAC]" patterns).
    title = listing.get("title")
    if isinstance(title, str) and _contains_digital_token(title):
        return True

    return False
