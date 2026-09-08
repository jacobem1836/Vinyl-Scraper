# Phase 21: Bug Fixes - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix two isolated UI bugs: the typeahead spinner failing to clear in all cases, and the image loading skeleton using a horizontal grey pulse instead of a barely-visible diagonal black shimmer. No backend changes. No new features — pure bug fixes in `static/typeahead.js` and `static/style.css`.

</domain>

<decisions>
## Implementation Decisions

### Typeahead Spinner Fix (BUG-03)

- **D-01:** Thorough fix — both root causes addressed:
  1. `closeDropdown()` must hide the spinner (currently missing — covers Escape, blur, and any close-without-select path)
  2. Debounce timer must be cancelled on result select AND on type dropdown change (eliminates the race where debounce fires after the user has already picked a result, then shows a stale spinner that never clears)
- **D-02:** Success criteria (from ROADMAP): selecting a result hides the spinner immediately; changing the type dropdown while typeahead is open hides the spinner immediately
- **D-03:** Scope: `static/typeahead.js` only — the spinner elements in templates (`addSpinner`, `editSpinner`) are correct HTML, no template changes needed

### Image Skeleton Shimmer (UI-07)

- **D-04:** Replace horizontal pulse (`skeleton-pulse` animation) with a 135° diagonal sweep (`skeleton-shimmer` animation)
- **D-05:** Visual target: barely visible, black-on-black shimmer — the highlight should be almost indistinguishable from the #000 surface. Avoid the current grey appearance (`#1a1a1a`→`#2a2a2a` range). Use very dark values, something close to `#0a0a0a`→`#141414` (Phase 16 established these as the minimum visible range on #000).
- **D-06:** Animation technique: `background-position` sweep on a `background-size: 400% 400%` gradient (matching the chosen option). Duration ~1.4s ease-in-out infinite.
- **D-07:** Scope: `.card-artwork-wrapper` in `static/style.css` only. Item detail page has no image skeleton.
- **D-08:** Rename keyframe from `skeleton-pulse` → `skeleton-shimmer` to reflect the new animation. Update the one reference.

### Claude's Discretion

- Exact color stops (stay within barely-visible range — `#000000` to `#141414`)
- Whether to adjust `background-size` ratio for a crisper diagonal band
- Animation easing function (ease-in-out is fine)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §BUG-03, §UI-07 — Acceptance criteria for both fixes

### Codebase change surfaces
- `static/typeahead.js` — Spinner show/hide logic; `closeDropdown()` (lines 31–39), `selectResult()` (line 167), type change handler (line 279), debounce timer, fetch abort handling
- `static/style.css` — `.card-artwork-wrapper` skeleton animation (currently `@keyframes skeleton-pulse`, approximately lines 628–660)

### Prior decisions
- `.planning/phases/16-visual-foundation/16-CONTEXT.md` §D-03 — Phase 16 established `#0a0a0a`/`#141414` as minimum visible skeleton colors on true black surface. Stay at or below this brightness for the new shimmer.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `closeDropdown()` in `typeahead.js`: already handles hiding dropdown and clearing results — just needs `spinner.classList.add("hidden")` added
- Debounce timer variable already exists in `typeahead.js` — cancel it with `clearTimeout()` on select and type change
- `.card-artwork-wrapper.loaded` already stops the animation via `animation: none` — only the keyframe and gradient definition change

### Established Patterns
- Spinner is shown/hidden via `.classList.remove("hidden")` / `.classList.add("hidden")` — consistent throughout `typeahead.js`
- Skeleton uses `background-position` animation (not `transform`) — keep this pattern for the diagonal version
- Phase 16 decision: skeleton colors must remain visible against `#000000` surface — `#0a0a0a`/`#141414` is the confirmed floor

### Integration Points
- Spinner elements: `#addSpinner` (index.html add modal), `#editSpinner` (index.html edit modal + item_detail.html edit modal) — all initialized via `initTypeahead()` in `typeahead.js`
- Skeleton: `onload`/`onerror` handlers on `<img class="card-artwork">` add `.loaded` to both the img and its parent `.card-artwork-wrapper` — no change needed to this logic

</code_context>

<specifics>
## Specific Ideas

- "Doesn't matter that much — main thing is it should be a barely visible black shimmer rather than the current grey" — the exact angle/speed are implementation details; visual result is what matters
- Diagonal direction: top-left → bottom-right (135°), per ROADMAP success criteria

</specifics>

<deferred>
## Deferred Ideas

None — analysis stayed within phase scope.

### Reviewed Todos (not folded)
- "Add eBay developer keys/configs to project" — completed in Phase 20
- "Remove dead Clarity stuff from project" — completed in Phase 20
- "Add manual selection of Discogs link or album" — Phase 23 scope
- "Fix typeahead spinner not clearing" — in scope for this phase (covered by BUG-03)

</deferred>

---

*Phase: 21-bug-fixes*
*Context gathered: 2026-04-18*
