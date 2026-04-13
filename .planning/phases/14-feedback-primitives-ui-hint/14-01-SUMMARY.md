# Phase 14-01 Summary — Feedback Primitives: Toast + UI Hints

## Status
COMPLETE — all three feedback flows verified; API contract confirmed untouched.

## What Was Built

### `showToast(message, durationMs)` helper — `templates/base.html`

**Signature:** `showToast(message: string, durationMs?: number): void`

- Default duration: 4000 ms (used when `durationMs` is `null` or omitted)
- Exposes itself as `window.showToast` for cross-script access
- DOM target: `#toast` container + `#toastMessage` span (lines 103–105)
- Function defined at lines 108–118; exported at line 119

**Call sites in `base.html`:**

| Line | Trigger | Message | Duration |
|------|---------|---------|---------|
| 126 | DOMContentLoaded, `?toast=` query param present | decoded param value | 4000 ms (default) |
| 248 | Scan poll completes (`fromPolling` guard) | `"{N} new listing(s) found"` | 6000 ms |

After reading `?toast=`, the param is stripped from the URL via `window.history.replaceState` (line 127) so it does not reappear on refresh.

### Toast DOM element — `templates/base.html` lines 102–105

```html
<!-- Toast notification -->
<div id="toast" class="hidden toast">
  <span id="toastMessage"></span>
</div>
```

Styled via `.toast` class in `static/style.css` (fixed position, bottom-right, slide-up animation).

### Toast CSS — `static/style.css`

Added `.toast` rule: fixed positioning, `var(--color-surface)` background, `var(--color-accent)` border-left accent, fade/slide keyframe animation, `z-index` above all panels.

### `index.html` — no JS showToast calls

`templates/index.html` contains no direct `showToast` calls. Toast messages are delivered to `index.html` via server-side `?toast=` redirects (see below). The scan-completion toast fires from `base.html`'s scan-poll callback which runs on every page.

## Server-Side `?toast=` Redirects (`app/routers/wishlist.py`)

These are pre-existing redirects that feed the toast system — `app/` code was not modified in this phase.

| Line | Action | Toast value |
|------|--------|-------------|
| 134 | Item added | `Item added, scanning in background` |
| 161 | Item updated | `Item updated` |
| 189 | Manual item scan | `{N} new listings found` |
| 219 | Scan all complete | `{N} new listings found` |

## Feedback Flows Verified (FEEDBACK-01 / 02 / 03)

| Flow | Trigger | Delivery mechanism | Verified |
|------|---------|-------------------|---------|
| FEEDBACK-01 | Add item (POST /wishlist/add) | `?toast=Item+added%2C+scanning+in+background` redirect → `showToast` | Yes |
| FEEDBACK-02 | Edit item (POST /wishlist/{id}/edit) | `?toast=Item+updated` redirect → `showToast` | Yes |
| FEEDBACK-03 | Scan completes (background poll) | `window.showToast` called directly at line 248 of base.html | Yes |

## API Contract Check

- `POST /api/wishlist` with `X-API-Key` header: untouched
- `app/` directory: zero files modified in this phase
- All changes confined to `templates/base.html`, `templates/index.html`, `static/style.css`

## Files Modified

| File | Lines changed | Purpose |
|------|--------------|---------|
| `templates/base.html` | 102–130, 248 | Toast DOM element, showToast helper, query-param reader, scan-complete call |
| `templates/index.html` | Minor markup | UI hint / empty-state copy (phase scope) |
| `static/style.css` | `.toast` rule | Toast visual styling |

`app/` — unchanged.
