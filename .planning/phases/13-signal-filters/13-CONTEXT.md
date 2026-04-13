# Phase 13: Signal Filters - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Only relevant, physical, accurately-located listings reach the user. Three requirements in scope:
- FILTER-01: relevance threshold hides bad matches
- FILTER-02: digital-only listings never appear in scan results
- FILTER-03: Discogs listings show correct seller location

Out of scope: notification changes, UI redesign of detail view, new sources.

</domain>

<decisions>
## Implementation Decisions

### Relevance scoring (FILTER-01)
- **D-01:** Use `rapidfuzz` library for fuzzy string matching (fast, C-backed, small dep footprint)
- **D-02:** Score listing title against combined `"{artist} {title}"` from the wishlist item. The core problem is that scans for a *specific album* return *other albums* by the same artist or loosely related titles — combined scoring disambiguates.
- **D-03:** Persist the computed score on the Listing row (new `relevance_score` column, float 0–100)

### Threshold configuration
- **D-04:** Global default threshold = `70` (hard-coded in `config.py` as `RELEVANCE_THRESHOLD_DEFAULT`, env-overridable)
- **D-05:** Add nullable `relevance_threshold` column on `WishlistItem`. When set, overrides the global default for that item.
- **D-06:** Filter logic: `listing.relevance_score >= (item.relevance_threshold or settings.RELEVANCE_THRESHOLD_DEFAULT)`

### Filter vs hide semantics
- **D-07:** Store all scraped listings regardless of score. Apply filter at query time in dashboard + detail view routes. Reversible — threshold changes take effect without rescan.

### Digital detection (FILTER-02)
- **D-08:** Layered detection:
  1. Format-string match (case-insensitive) on any listing format field — strings: `File`, `MP3`, `FLAC`, `Digital`, `Lossless`, `WAV`, `AAC`
  2. Bandcamp URL heuristic — listings whose URL / item payload indicates digital-only (no physical SKU or `item_type` = digital track/album)
- **D-09:** Digital listings are dropped at scan time (not persisted). Unlike relevance, there is no threshold to retune; a digital listing is always wrong.

### Discogs seller location (FILTER-03)
- **D-10:** For each matched release, fetch `/marketplace/listings/{listing_id}` per listing and read the `ships_from` field. This is the authoritative source.
- **D-11:** Populate `Listing.ships_from` (existing column) from that value; fall back to `None` and log a warning if the API call fails. Do not fall back to scraping.
- **D-12:** Respect existing Discogs rate limit posture — no burst retries; accept that a small number of listings may be missing location on a given scan.

### Observability
- **D-13:** Per-scan log line emitted from `scanner.py` after filtering:
  `[filter] item=<id> kept=<N>/<M> (relevance<thr: <a>, digital: <b>, location_missing: <c>)`
- **D-14:** Admin dashboard for filter stats is **deferred** — revisit after Phase 17 or when log-diving becomes painful.

### Claude's Discretion
- Exact `rapidfuzz` scorer choice (`WRatio` vs `token_set_ratio`) — pick during planning based on small test set
- Whether to normalize strings (lowercase, strip punctuation) before scoring
- Schema migration approach (Alembic vs manual SQL — project uses manual migrations)
- Where to inject filter logic (query-level vs service-level helper)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — FILTER-01, FILTER-02, FILTER-03 acceptance criteria
- `.planning/ROADMAP.md` §"Phase 13: Signal Filters" — success criteria and scope anchor

### Existing code touchpoints
- `app/services/discogs.py` — search + listing fetch; currently `seller=None` placeholder at line 24
- `app/services/scanner.py` — scan orchestration, line 67 maps `seller` from result dict
- `app/services/bandcamp.py` — digital filtering gap
- `app/models.py` — `Listing` (seller, ships_from), `WishlistItem` (needs `relevance_threshold`)
- `app/routers/wishlist.py` — dashboard + detail view queries that need filter injection
- `app/config.py` — new `RELEVANCE_THRESHOLD_DEFAULT` setting

No external specs / ADRs for this project.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Listing.ships_from` column already exists — no schema change needed for location fix, just populate it correctly from Discogs
- Scanner already dedupes listings by URL — adding score/filter logic slots in cleanly before persistence (for digital drop) and after (for relevance score compute + store)
- `config.py` uses `pydantic_settings.BaseSettings` — new threshold setting is a one-line add

### Established Patterns
- Source adapters return `list[dict]` with standardized keys (`title`, `price`, `url`, `seller`, etc.) — extend contract to include `format` / `item_type` for digital detection
- Services return empty list on error; scanner continues on per-source failure — keep this posture for listing-detail fetches in Discogs
- Async concurrency via `asyncio.gather` — use for per-listing Discogs detail fetches, respecting rate limits

### Integration Points
- Relevance scoring runs inside scanner after source adapters return, before DB persistence (score computed once, stored)
- Filter applied at route-handler query layer in `routers/wishlist.py` dashboard + detail views
- Digital filter runs inside each source adapter OR in scanner — planner to decide (adapter keeps concerns local; scanner keeps rules central)

</code_context>

<specifics>
## Specific Ideas

- "The issue was more about a specific album returning other album listings" — relevance scoring is fundamentally about *album disambiguation*, not keyword presence. Test cases during planning should include known-bad examples from current DB (e.g., a release returning same-artist unrelated albums).

</specifics>

<deferred>
## Deferred Ideas

- **Admin dashboard for filter stats** — counts of relevance-dropped / digital-dropped / location-missing per scan, visible without log-diving. Revisit after Phase 17 or when observability becomes painful.
- **Per-source relevance tuning** — currently one global algorithm; might later want source-specific weights (e.g., Bandcamp titles are more verbose than Discogs).
- **Retuning workflow** — UI to adjust threshold from the item detail page. Possible in a future UX phase.

</deferred>

---

*Phase: 13-signal-filters*
*Context gathered: 2026-04-13*
