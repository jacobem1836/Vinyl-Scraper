# Stack Research — v1.2 Signal & Polish

**Domain:** Polish/quality milestone for existing FastAPI vinyl scraper
**Researched:** 2026-04-12
**Confidence:** HIGH

## TL;DR

**Use existing stack for ~95% of this milestone.** One optional production dep (`rapidfuzz`) for listing relevance scoring, and one dev-only tool (`pip-audit`) for the security audit. Everything else is custom code against CRATE CSS, Jinja2 templates, existing adapters, and stdlib.

## Per-Feature Stack Decision Matrix

| Feature | Decision | Library | Rationale |
|---------|----------|---------|-----------|
| Listing relevance scoring | **Add `rapidfuzz`** (optional: stdlib `difflib`) | `rapidfuzz>=3.14,<4` | Fuzzy title-match scoring against query; `token_set_ratio` handles artist/album word reordering. C++ impl, ~10–100x faster than `difflib`, MIT license, zero runtime deps. `difflib.SequenceMatcher` is a valid stdlib fallback but worse at multi-word vinyl titles ("Kind of Blue — Miles Davis" vs "Miles Davis: Kind Of Blue (2022 Reissue)"). |
| Filter digital-only listings | **Existing** | — | Heuristic against listing title / format fields per adapter. Pure string checks (`"digital"`, `"mp3"`, `"flac"`, `"download"` in lowercased title/format). Belongs in each adapter's `_build_listing()` or a shared filter in `scanner.py`. |
| Discogs seller location parsing | **Existing** | — | Bug fix in `app/services/discogs.py`. Likely a JSON path / field-name mismatch in the Discogs marketplace response. No lib change. |
| Scan-now spinner / toast feedback | **Existing** | — | CRATE CSS + vanilla JS `fetch()` against existing `/api/scan/{id}` (or new per-item endpoint). Toast pattern: small fixed-position element, CSS transition on `opacity` + `transform`. No toast library — would violate CRATE aesthetic discipline. |
| "Item added, scanning…" modal consistency | **Existing** | — | Reuse CRATE dialog primitive (native `<dialog>` element or existing modal class). Match existing add-item modal styling. |
| Default `type="album"` on add | **Existing** | — | One-line HTML change — `selected` attribute on `<option value="album">` in add-item form. |
| Logo change + email logo match | **Existing** | — | Replace static asset in `app/static/` + update `<img>` in `templates/email/*.html`. Email logo must be `<img>` with absolute URL (self-hosted via FastAPI static mount) — no inline SVG in email (poor client support). |
| Email: back-in-stock / price-drop / deal notification types | **Existing** | — | New Jinja2 templates under `templates/email/` + notifier dispatch logic. `notifier.py` already uses `asyncio.to_thread` + SMTP; just add event types and corresponding templates. Inline CSS convention already established in v1.1. |
| Prettier scrollbars | **Existing** | — | CSS-only: `::-webkit-scrollbar` (WebKit/Blink — Safari, Chrome), `scrollbar-width` + `scrollbar-color` (Firefox + modern spec). Add to CRATE `tokens.css` / `global.css`. No JS, no library. |
| Security audit pass | **Add `pip-audit`** (dev-only) | `pip-audit>=2.10` | Official PyPA tool; scans `requirements.txt` against PyPI advisory DB + OSV. Run locally/CI — not a runtime dep. Optionally pair with `bandit` for static analysis of scraper code paths (SSRF, template injection, SQL). |

## Recommended Additions

### Production (requirements.txt)

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| `rapidfuzz` | `>=3.14.5,<4.0` | Fuzzy string matching for listing relevance score | Fast (C++), zero deps, MIT. `fuzz.token_set_ratio(query, listing_title)` returns 0–100. Threshold (e.g. 60) filters obvious mismatches. Verified latest on PyPI: 3.14.5. |

### Development (requirements-dev.txt — create if not present)

| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| `pip-audit` | `>=2.10.0` | CVE scan of pinned deps | Official PyPA tool; satisfies "security audit pass" objectively. Run: `pip-audit -r requirements.txt`. |
| `bandit` | `>=1.8` *(optional)* | Static security linter for Python | Catches SSRF patterns in scrapers, weak crypto, hardcoded secrets. Optional — keep if signal-to-noise is good after first run. |

### No change needed

Jinja2, httpx, FastAPI, SQLAlchemy, APScheduler, Uvicorn, pg8000, aiosqlite — all current and sufficient.

## Installation

```bash
# Production
pip install 'rapidfuzz>=3.14.5,<4.0'

# Dev-only (security audit)
pip install 'pip-audit>=2.10.0'
pip install 'bandit>=1.8'   # optional

# Pin into requirements.txt after install
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `rapidfuzz` | `difflib` (stdlib) | If avoiding any new dep matters more than match quality. Works for short exact-ish titles; degrades on reissue suffixes and reordered tokens. |
| `rapidfuzz` | `thefuzz` / `fuzzywuzzy` | Don't — `rapidfuzz` is the modern, MIT-licensed successor. `fuzzywuzzy` is GPL + slower. |
| Custom toast JS | `Sonner` / `Notyf` / other JS toast libs | Never — CRATE is hand-rolled; introducing a JS toast lib breaks aesthetic discipline and adds a build step this project has deliberately avoided. |
| `pip-audit` | `safety` | Both work. `pip-audit` is PyPA official and uses OSV — prefer it. |
| CSS `::-webkit-scrollbar` | `overlayscrollbars` / `simplebar` JS libs | Never for this project. CSS covers 100% of target browsers; JS scrollbar libs add weight and accessibility regressions. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `fuzzywuzzy` | GPL-2.0, unmaintained, slower than rapidfuzz | `rapidfuzz` |
| JS toast/modal libraries (`sweetalert2`, `notyf`, etc.) | Violates hand-rolled CRATE principle; adds runtime JS weight | Vanilla JS + CRATE CSS primitive |
| scikit-learn / embeddings for relevance | Massive overkill for title matching at this scale (dozens of listings per scan) | `rapidfuzz.fuzz.token_set_ratio` |
| Adding Tailwind / PostCSS / build pipeline | Project explicitly avoids; CRATE is hand-rolled CSS custom properties | Extend `tokens.css` / CRATE classes |
| Inline SVG logos in email HTML | Poor email-client support (Outlook strips SVG) | `<img src="https://…/static/logo.png">` absolute URL |

## Integration Points

### Relevance scoring (`rapidfuzz`)

- **Where:** `app/services/scanner.py` — after each adapter returns raw listings, before dedup/persist.
- **Shape:** Add helper `score_relevance(query: str, listing_title: str) -> int` using `rapidfuzz.fuzz.token_set_ratio`.
- **Threshold:** Configurable via `Settings` (e.g. `RELEVANCE_MIN_SCORE=60`). Optionally persist score on `Listing` for debugging.
- **Per type:** For `type="artist"` / `type="label"`, score against the appropriate field (artist match, not full title).

### Digital-only filter

- **Where:** Either per-adapter `_build_listing()` (preferred — each source knows its own format field) OR shared filter in `scanner.py`.
- **Heuristics:** lowercase title + format string; reject if contains any of: `digital`, `mp3`, `flac`, `wav`, `download`, `lossless`, `24-bit`. Bandcamp especially noisy here.

### Email notifications (back-in-stock / price-drop / deal)

- **Templates:** `app/templates/email/back_in_stock.html`, `price_drop.html`, `deal.html` (or one template with conditional blocks).
- **Dispatch:** Extend `notifier.py` with an event-type enum; `send_notification(event_type, item, listing, context)`.
- **State tracking:** Back-in-stock needs `is_in_stock=False` → `True` transition. Price-drop needs prior-price comparison. Both require querying prior state during scan — straightforward SQLAlchemy.

### Scrollbar styling

- **Where:** `app/static/css/` (CRATE global or tokens). Add both `::-webkit-scrollbar*` rules and standards-track `scrollbar-width` / `scrollbar-color`.

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `rapidfuzz 3.14.x` | Python 3.11, 3.12, 3.13, 3.14 | Wheels published for all. Runs fine on Railway's Python builder. |
| `pip-audit 2.10` | Python 3.9+ | Dev-only; not deployed. |

## Security Audit Workflow (concrete)

1. `pip-audit -r requirements.txt --strict` — fix or document any CVEs.
2. `bandit -r app/` — review SSRF / template injection / SQL patterns. Most expected hits will be around scraper URL construction and Jinja `autoescape`; triage.
3. Manual: verify `X-API-Key` comparison uses `hmac.compare_digest` (not `==`) to avoid timing attacks.
4. Manual: confirm `/api/artwork` proxy validates/allow-lists Discogs hosts (SSRF guard).
5. Manual: confirm no secrets in Railway logs (check `print()` calls in adapters).

## Sources

- **PyPI** — `rapidfuzz` 3.14.5 verified latest (2026-04-12), MIT, C++ backend
- **PyPI** — `pip-audit` 2.10.0 verified latest (2026-04-12), PyPA-maintained
- **PROJECT.md / CLAUDE.md** — existing stack confirmed (Python 3.11+/3.14, FastAPI 0.115, CRATE hand-rolled CSS, 6 active adapters)
- **MDN** — `scrollbar-width`, `scrollbar-color`, `::-webkit-scrollbar` (cross-browser scrollbar styling is now stable CSS)
- **Can I Email** — email client SVG support (rationale for `<img>` over inline SVG in email logo)

---
*Stack research for: Vinyl Wishlist Manager v1.2 Signal & Polish*
*Researched: 2026-04-12*
