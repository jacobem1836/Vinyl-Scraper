# Phase 23: Discogs Release Selection - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

User can search for and pin a specific Discogs release to a wishlist item from the item detail page. Pinning fixes wrong artwork and ensures scans use the exact release ID instead of running a title/artist search. Artwork updates to the pinned release thumbnail immediately on pin.

New capabilities out of scope: bulk release re-pinning, browsing Discogs outside of item context, managing multiple pins per item.

</domain>

<decisions>
## Implementation Decisions

### Pin Entry Point
- **D-01:** A "Pin Release" button is added to the header action button row on item detail, alongside the existing Edit and Scan Now buttons.
- **D-02:** Clicking "Pin Release" opens a dedicated modal (separate from the Edit modal) with a release search field and results list.

### Search Results Format
- **D-03:** Search results inside the pin modal show small 40×40 thumbnails + "Artist - Title (Year)" text, one row per result. Matches the aesthetic of the existing typeahead dropdown but rendered as a scrollable list inside the modal.
- **D-04:** The existing `typeahead_search()` endpoint logic can be reused to fetch candidates (it already returns `release_id`, `title`, `artist`, `year`, `thumb` for vinyl releases). A dedicated API endpoint `/api/discogs/releases/search?q=...` should be added to serve this cleanly.

### Pin Status Display
- **D-05:** When a release is pinned, show a small muted text line below the 120×120 artwork: `Pinned: [Title] ([Year])`. If nothing is pinned, this line is absent.
- **D-06:** The "Pin Release" button label does not change when pinned (status is conveyed via the artwork label). The modal has a "Clear pin" option to remove the pin.

### Artwork Update on Pin
- **D-07:** When the user selects a release and confirms the pin, `artwork_url` on the `WishlistItem` is updated to the release's `thumb` URL (from the search result). This happens immediately in the pin save endpoint — no re-scan required.
- **D-08:** If the selected result has no thumb, `artwork_url` is left unchanged.

### Claude's Discretion
- Exact modal animation style (match existing edit modal pattern: fade backdrop + slide-up panel)
- Search debounce timing (match existing typeahead: ~300ms)
- Number of results to show (suggest 8–10)
- Error/empty state copy inside the pin modal

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Discogs Release Selection — DISC-01, DISC-02, DISC-03 acceptance criteria

### Roadmap
- `.planning/ROADMAP.md` §Phase 23 — Success criteria and phase boundary

### Existing Implementation
- `app/models.py` — `WishlistItem.discogs_release_id` column (nullable Integer, already exists)
- `app/services/discogs.py` — `typeahead_search()` (reusable for release search) and `search_and_get_listings()` (already respects pinned release)
- `app/routers/wishlist.py` — Edit/add routes already accept and save `discogs_release_id`
- `templates/item_detail.html` — Current item detail layout; pin button and modal go here
- `templates/base.html` — Read for modal/typeahead JS patterns to stay consistent

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `typeahead_search(query, item_type, max_results)` in `discogs.py:30` — already returns `{release_id, title, artist, year, thumb}` per result for vinyl releases. This is the data shape the new release search endpoint should return.
- `_get_release_listings(release_id)` in `discogs.py:87` — fetches the cover image URI from a specific release. Can be used when artwork needs fetching from a release the typeahead thumb didn't cover.
- Edit modal pattern in `item_detail.html:184` — modal-overlay, modal-backdrop, modal-panel with fade + slide animations. Pin modal should follow the same structure exactly.
- `/api/typeahead` endpoint (in wishlist.py) — see how it's wired; new `/api/discogs/releases/search` should follow the same pattern (GET, query param `q` and `type`).

### Established Patterns
- Modal: `modal-overlay` → `modal-backdrop` (fade opacity) + `modal-panel` (opacity + translate-y transition)
- Form POST saves to `WishlistItem` via `/wishlist/{id}/edit`; pin save is a separate targeted endpoint to avoid touching unrelated fields
- `artwork_url` is updated in the scanner when a `_cover_image` key is present in listing results; same field used for pin artwork update
- True black palette, Gothic A1 typography — all new UI must follow Phase 16–17 visual decisions

### Integration Points
- New API endpoint: `GET /api/discogs/releases/search?q={query}` — returns JSON list of release candidates
- New web endpoint: `POST /wishlist/{item_id}/pin-release` — body `{release_id, artwork_url}` — updates `discogs_release_id` and `artwork_url`, redirects back with toast
- Item detail template: add Pin Release button in header actions, pin status label below artwork, and the pin modal HTML + JS

</code_context>

<specifics>
## Specific Ideas

- Modal search results look like the existing typeahead dropdown: thumbnail on left, text on right, clickable rows. No heavy card grid — keep it compact and list-like.
- The "Pinned: Title (Year)" text under the artwork is muted/small — not a badge or card. Understated indicator.
- "Clear pin" action should be available inside the modal (not a separate button in the header) to keep the header clean.

</specifics>

<deferred>
## Deferred Ideas

- Bulk re-pinning across all wishlist items — future phase
- Browsing Discogs master/release hierarchy (master → releases view) — out of scope
- Showing release condition, format, pressing info in search results — future enhancement

</deferred>

---

*Phase: 23-discogs-release-selection*
*Context gathered: 2026-04-19*
