"""Relevance of a scraped listing title to the wishlist query, 0-100.

Token containment: what fraction of the query's tokens appear in the title. Queries written as
"Artist - Title" also score the title half alone, so store listings that omit the artist still pass.
Also rejects digital-only formats.
"""
import re

_STOPWORDS = {"the", "a", "an", "of", "and", "&"}
_DIGITAL = re.compile(r"\b(mp3|flac|wav|aac|digital|download|lossless)\b", re.I)


def _tokens(s: str) -> set[str]:
    words = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split()
    meaningful = {w for w in words if w not in _STOPWORDS}
    return meaningful or set(words)


def score_listing(query: str, title: str) -> float:
    q_all = _tokens(query)
    t = _tokens(title)
    if not q_all or not t:
        return 0.0
    candidates = [q_all]
    parts = re.split(r"\s[-–—]\s", query or "", maxsplit=1)
    if len(parts) == 2 and _tokens(parts[1]):
        candidates.append(_tokens(parts[1]))
    return max(100.0 * len(q & t) / len(q) for q in candidates)


def is_digital(title: str | None, fmt: str | None = None) -> bool:
    return bool(_DIGITAL.search(title or "") or _DIGITAL.search(fmt or ""))
