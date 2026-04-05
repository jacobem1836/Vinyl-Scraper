# Phase 6: Discogs Typeahead - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can search and pin a specific Discogs album release when adding or editing a wishlist item. Typing in the album/subject name field shows a dropdown of matching Discogs releases (title, artist, year, cover thumb), debounced ≥300ms, navigable with arrow keys and confirmed with Enter or click. Selecting a release stores its Discogs release ID on the WishlistItem and autofills the query field with the release title.

Creating new item types, adding search to Artist/Label fields, or visual redesign of the dashboard — all out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Typeahead Trigger Scope
- **D-01:** Typeahead dropdown activates when type = "Album" OR "Subject" (both use `_get_album_listings` under the hood). Artist and Label types remain plain text input — no dropdown.

### Pinned Release Storage
- **D-02:** Add `discogs_release_id: int | None` column to `WishlistItem` (DB migration required). When a release is selected, the ID is stored and the query field autofills with the release title. New schema field must be `Optional[int] = None` to preserve iOS Shortcut API compatibility.
- **D-03:** The Discogs adapter uses the pinned `discogs_release_id` directly when set — skips the text search and fetches listings for that specific release. All other adapters (eBay, Juno, Bandcamp, Discrepancy, etc.) continue text-searching using the autofilled query title.

### Edit Modal Pre-State
- **D-04:** When editing an item that has a pinned Discogs release, display the currently linked release as a badge/chip (title + year) above the typeahead search field. User must explicitly clear the badge to re-search and re-link. Makes the pinned state visible and requires intentional action to change.

### Post-Select Behavior
- **D-05:** After a release is selected from the dropdown, the query field autofills with the release title and becomes read-only (locked) while a release is pinned. User must clear the pinned release badge to edit the query freely. This prevents the stored release ID and the query text from drifting apart.

### Claude's Discretion
- Exact dropdown row layout (cover thumb size, artist/year display within each result)
- AbortController implementation for cancelling in-flight requests on rapid typing
- Visual treatment of the locked query field (e.g., reduced opacity, background change, lock icon)
- New API endpoint path for typeahead search (e.g., `GET /api/discogs/search?q=...`)
- Debounce implementation (300ms minimum per TYPE-04)

### Folded Todos
- **"Add manual selection of Discogs link or album"** (2026-04-03): This phase fully addresses the todo's proposed solution — search Discogs, pick the correct release, store release ID, artwork and scanner use the pinned release. Mark as resolved on completion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §TYPE-01 through TYPE-04 — typeahead acceptance criteria (300ms debounce, keyboard nav, re-select on edit, 5-result cap)

### Frontend (templates + JS)
- `templates/index.html` — add modal (`#addItemModal`), edit modal (`#editItemModal`), form field IDs (`editQuery`, `editType`, `editNotifyPct`, etc.), existing modal open/close JS (transition classes, focus management, backdrop click)

### Backend
- `app/models.py` — `WishlistItem` model — needs new `discogs_release_id` column
- `app/schemas.py` — `WishlistItemCreate` / `WishlistItemUpdate` — needs `discogs_release_id: int | None = None`
- `app/routers/wishlist.py` — web and API routers; `create_wishlist_item_api` is the iOS Shortcut endpoint (must not break)
- `app/services/discogs.py` — `_get_album_listings()` fetches releases with title, artist, year, cover thumb — reusable as typeahead data source; note rate limit context (60 req/min Discogs cap)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_get_album_listings()` in `app/services/discogs.py`: Already fetches Discogs releases with title, release_id, cover thumb. A new `/api/discogs/search?q=` endpoint can call a slimmed version of this to return typeahead results (title, artist, year, thumb, release_id) without the lowest-price fetch.
- Modal open/close JS in `templates/index.html`: Pattern for `requestAnimationFrame` transitions, focus management, and backdrop click — new typeahead component should follow same conventions.
- `form-input` CSS class: Existing styled input — typeahead input reuses this.

### Established Patterns
- HTML form POST for add/edit — new `discogs_release_id` sent as hidden input alongside the form submit
- `Optional[...] = None` pattern for iOS Shortcut backwards compatibility — must apply to any new schema field
- Discogs semaphore (Semaphore(3)): rate-limit context; typeahead endpoint shares the same token, so debounce is critical to stay under 60 req/min
- DB migrations handled in `app/main.py` startup — `ALTER TABLE ADD COLUMN IF NOT EXISTS` pattern used in prior phases

### Integration Points
- `WishlistItem.discogs_release_id` (new) → `app/services/discogs.py:search_and_get_listings()` reads it and routes to a direct release fetch when set
- `templates/index.html` add/edit modals → new typeahead JS → new `GET /api/discogs/search` endpoint
- Edit modal JS (`openEdit()` function) → needs to read `data-discogs-release-id` and `data-discogs-release-title` from the edit button's dataset to populate the badge

</code_context>

<specifics>
## Specific Ideas

- No specific design references given — open to standard approaches for typeahead dropdowns
- "Locked" query field while pinned: prevents ID/query drift (user cannot accidentally edit the autofilled title while a release is pinned without explicitly clearing first)

</specifics>

<deferred>
## Deferred Ideas

- **CRATE logotype font changed to Bodoni Moda** — mentioned during discussion; belongs in Phase 8 (Brand Font Upgrade). Note for Phase 8 planner: user preference is Bodoni Moda as the display font.

### Reviewed Todos (not folded)
- "Add ebay developer keys/configs to project" — not relevant to this phase; remains pending

</deferred>

---

*Phase: 06-discogs-typeahead*
*Context gathered: 2026-04-05*
