# Phase 8: Brand Font Upgrade - Context

**Gathered:** 2026-04-07 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

The CRATE nav wordmark (`<a class="nav-brand">CRATE</a>`) renders in a brutalist display web font loaded from a self-hosted static asset. No request to an external CDN at runtime. No FOUT on page load.

</domain>

<decisions>
## Implementation Decisions

### Font Choice
- **D-01:** Use **Bodoni Moda** — a high-contrast editorial serif. Specific choice by Jacob; no tool-driven exploration needed.
- **D-02:** Download the font file(s) from Google Fonts and self-host under `static/fonts/`. Do not hotlink Google Fonts CDN in production.

### Scope
- **D-03:** Apply the display font to the CRATE wordmark (`.nav-brand`) **only**. Do not apply to headings or any other elements.

### Loading / FOUT Prevention
- **D-04:** Use `font-display: block` on the `@font-face` declaration. This keeps the wordmark invisible for a very short block period rather than flashing a system font. Preferred for a brand mark where a momentary flash would be more disruptive than brief invisibility.

### CSS Integration
- **D-05:** Add a `--font-display` CSS custom property in `:root` (next to `--font-sans`). Apply it to `.nav-brand` via `font-family: var(--font-display), var(--font-sans);`. This keeps the design system clean and provides a system-font fallback chain.

### Font Format
- **D-06:** Ship `woff2` only. All modern browsers (and Railway's deployment target) support woff2. No need for woff fallback.

### Claude's Discretion
- Which Bodoni Moda weight/variant to use (likely Bold or ExtraBold given current `font-weight: 600` on `.nav-brand`)
- Whether to subset the font to uppercase ASCII only (CRATE uses 5 chars + uppercase) to reduce file size
- Exact `@font-face` declaration placement in `style.css`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design system
- `static/style.css` §1 — CSS custom properties (add `--font-display` here alongside `--font-sans` at line 81)
- `static/style.css` §5 — `.nav-brand` rule (lines 176–183) — this is the only selector to update
- `templates/base.html:12` — `<a href="/" class="nav-brand">CRATE</a>` — the wordmark element

### Requirements
- `.planning/REQUIREMENTS.md` §FONT-01 — "CRATE logotype uses a brutalist display web font loaded from a static asset (no external CDN dependency in production)"

### Phase goal
- `.planning/ROADMAP.md` §Phase 8 — Success criteria, especially: no CDN at runtime, no FOUT, font-informed by design tools

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `static/style.css` — The design system already uses CSS custom properties. Adding `--font-display` follows the established pattern.
- `static/` — Root static directory (currently no `fonts/` subdirectory; needs to be created)

### Established Patterns
- CSS custom property naming: `--font-sans`, `--color-*`, `--space-*` — kebab-case, grouped by type
- All static assets served from `static/` directory (images, CSS). Font files belong in `static/fonts/`
- No external CDN dependencies — design system comment explicitly says "No external dependencies"

### Integration Points
- FastAPI static file mounting in `app/main.py` (or equivalent) — confirm `static/` is mounted and `static/fonts/` will be served automatically
- `.nav-brand` is used in `templates/base.html` only — one template to update (none needed, font applies via CSS)

</code_context>

<specifics>
## Specific Ideas

- Font: **Bodoni Moda** specifically — Jacob's direct call, not open to alternatives
- The current `.nav-brand` already has `letter-spacing: 0.25em; text-transform: uppercase;` — these should be preserved, potentially adjusted if Bodoni Moda's proportions change the feel

</specifics>

<deferred>
## Deferred Ideas

- Applying Bodoni Moda to page headings — discussed and deferred; wordmark only for this phase
- Google Fonts CDN link for development convenience — out of scope; always self-hosted per FONT-01

</deferred>

---

*Phase: 08-brand-font-upgrade*
*Context gathered: 2026-04-07*
