# Phase 23: Discogs Release Selection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-19
**Phase:** 23-discogs-release-selection
**Mode:** discuss
**Areas analyzed:** Pin entry point, Search results format, Pin status display, Artwork update behavior

## Codebase Scout Findings

Key pre-existing infrastructure that informs decisions:
- `WishlistItem.discogs_release_id` column already exists (nullable Integer)
- `typeahead_search()` already returns `{release_id, title, artist, year, thumb}` for vinyl releases
- `search_and_get_listings()` already fast-paths on `discogs_release_id` when set
- Edit/add routes already accept and save `discogs_release_id`
- Item detail edit modal already carries `discogs_release_id` hidden input

The database model, scan integration, and save endpoints are complete.
Phase 23 is purely a UI surface problem — making the pin workflow discoverable and visible.

## Assumptions Presented

### Pin entry point
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| A dedicated modal (Pin Release button) is cleaner than inline or new section | Likely | Existing edit modal pattern; keeps header uncluttered |

### Search results format
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Thumbnail + text rows match existing typeahead aesthetic | Confident | typeahead_search() returns thumb; existing dropdown uses same shape |

### Pin status display
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Small muted text label under artwork is appropriate | Likely | Minimal, consistent with Phase 16–17 understated aesthetic |

### Artwork update
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Artwork should update on pin (not deferred to rescan) | Likely | artwork_url already set from scanner cover_image; same field, same mechanism |

## User Selections

All four gray areas were selected for discussion.

### Pin entry point
- **User chose:** Dedicated modal ("Pin Release" button alongside Edit/Scan Now)
- **Reason:** Keeps concerns separate; dedicated modal parallels the existing Edit modal pattern

### Search results format
- **User chose:** Thumbnail + text row (40×40 thumb + Artist - Title (Year))
- **Reason:** Visual richness helps identify correct pressing; consistent with typeahead style

### Pin status display
- **User chose:** Small muted text label below the 120×120 artwork — "Pinned: Title (Year)"
- **Reason:** Understated, doesn't change layout

### Artwork update
- **User chose:** Yes — update artwork_url immediately on pin
- **Reason:** Immediate feedback; the cover art changing confirms the pin worked

## No corrections — all recommended options accepted.
