# Phase 6: Discogs Typeahead - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the Q&A.

**Date:** 2026-04-05
**Phase:** 06-Discogs Typeahead
**Mode:** discuss
**Areas analyzed:** Typeahead trigger scope, Pinned release storage, Edit modal pre-state, Post-select behavior

## Assumptions Presented

All 4 gray areas were presented as a multi-select and all were selected for discussion.

## Discussion

### Typeahead Trigger Scope

| Question | Options Presented | Answer |
|----------|------------------|--------|
| When should the typeahead dropdown activate? | Album type only (Recommended); Album + Subject | Album + Subject |

Rationale: Both "Album" and "Subject" item types internally call `_get_album_listings()`, so typeahead is meaningful for both. Artist and Label types use different search paths — no dropdown.

---

### Pinned Release Storage

| Question | Options Presented | Answer |
|----------|------------------|--------|
| What should happen when user selects a release? | Store release ID + autofill query (Recommended); Autofill query only; Store release ID only | Store release ID + autofill query |
| Should Discogs use pinned ID, or all sources use text? | Discogs uses ID, others text-search (Recommended); All sources use autofilled query text | Discogs uses ID, others text-search |

Rationale: Full "linked" release semantics — ID stored, Discogs goes straight to correct release, other sources search by the autofilled title for broad marketplace coverage.

---

### Edit Modal Pre-State

| Question | Options Presented | Answer |
|----------|------------------|--------|
| What does user see when editing an item with a pinned release? | Show linked release badge + re-search option (Recommended); Auto-populate search with current query; Empty search field | Show linked release badge + re-search option |

Rationale: Makes the pinned state explicit and visible. User has to intentionally clear the badge to change it.

---

### Post-Select Behavior

| Question | Options Presented | Answer |
|----------|------------------|--------|
| What happens to query field after selecting a release? | Autofill query with release title, lock editable (Recommended); Autofill query, stays editable; Autofill query, show clear button | Autofill query, lock editable |

Rationale: Locking prevents query/ID drift. User must clear the pinned release to regain free text editing.

---

## Corrections Made

No corrections — all recommended options confirmed.

## Scope Creep Noted

- **CRATE logotype font → Bodoni Moda**: Mentioned by user during the "Done" step. Deferred to Phase 8 (Brand Font Upgrade). Captured in CONTEXT.md deferred section with the specific font preference noted.
