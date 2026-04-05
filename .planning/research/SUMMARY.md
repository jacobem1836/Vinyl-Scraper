# Project Research Summary

**Project:** Vinyl Wishlist Manager v1.1 — UX Polish & Album Selection
**Domain:** Iterative UX improvement on an existing FastAPI/Jinja2 personal tool
**Researched:** 2026-04-05
**Confidence:** HIGH

## Executive Summary

This is a UX polish milestone on a stable, already-deployed personal tool. The existing stack (FastAPI, Jinja2, SQLAlchemy, vanilla JS, CRATE CSS) is validated and stays unchanged — the v1.1 scope adds one new capability (Discogs typeahead), one data quality improvement (image source prioritisation), two aesthetic upgrades (email redesign, brand font), and a CSS polish pass. No new frameworks, no build steps, no infrastructure changes. The recommended approach is incremental: add the typeahead backend endpoint first (validates the Discogs search function shape and has the most cross-file touch points), improve image handling next (independent backend work), then tackle the isolated aesthetic changes, and finish with a comprehensive CSS polish pass once all content-affecting logic is stable.

The single highest-risk area is the Discogs typeahead — not because it is complex, but because it sits adjacent to an existing rate-limited API integration used by scheduled scans. A missing debounce or an `AbortController` omission can exhaust the Discogs rate quota and cause scheduled scans to fail. These are cheap to add (5–50 lines of JS) and must be designed in from the start, not retrofitted. All other features (email redesign, font upgrade, CSS fixes) are isolated, low-risk, and independently revertable.

The iOS Shortcut API contract (`POST /api/wishlist` with `X-API-Key`) is a hard constraint that every phase must respect. If `discogs_release_id` is added to the `WishlistItem` schema, it must be `Optional` with a `None` default — the Shortcut sends no such field. This is the most likely silent breakage vector across the entire milestone.

## Key Findings

### Recommended Stack

The existing stack handles all v1.1 requirements without additions. The only candidate addition is `premailer 3.10.0` (CSS inlining for email templates), and the verdict from research is to skip it unless the email template grows complex enough that per-element inline styles become unmanageable. `lxml` (the primary `premailer` dependency) is already present at 5.3.0, so adding it later is frictionless if needed.

**Core technologies (all existing — no new packages required):**
- **FastAPI 0.115.0:** One new `GET /api/discogs/search` endpoint; existing auth patterns apply
- **Jinja2 3.1.4:** New `templates/email_deal.html` template rendered via standalone `Environment` (no request context needed)
- **httpx 0.28.0:** Reused in the new typeahead endpoint for the single-call Discogs API request
- **CRATE CSS (`static/style.css`):** Targeted edits to tokens, button states, grid breakpoints — no architecture change
- **Vanilla JS (inline in templates):** ~50-line typeahead block following the existing hand-rolled modal/toast pattern
- **Self-hosted WOFF2 + `@font-face`:** Brand font delivered with no CDN dependency; latin subset ~14KB

**What not to add:** Alpine.js, htmx, Tailwind, typeahead libraries (typeahead-standalone, typeahead.js), Google Fonts CDN link, MJML, or any email framework. Each has a documented reason to avoid in STACK.md; all are overengineered for the feature scope.

### Expected Features

**Must have (table stakes for v1.1 to feel complete):**
- Typeahead fires within 300ms of typing pause, shows cover thumb + "Artist — Title" + year + label
- Keyboard navigation (Up/Down/Enter/Escape) in the dropdown — universal autocomplete contract
- Typeahead active only when type = "Album" (artist/label queries are fuzzy; only albums benefit)
- Store-sourced images shown when available; graceful fallback to Discogs thumb, then SVG placeholder
- Email body max-width 600px with all styles inline — required for Gmail and Outlook compatibility
- CTA "View listing" as table-based button-link (tappable on mobile)
- Focus-visible ring on all buttons (currently a WCAG A failure)
- `text-faint` contrast fix (#555555 → #686868 to reach 4.5:1 — current value fails WCAG AA at 14px)
- 3-column grid breakpoint at 1024px (2 columns from 768–1279px is the current dead zone)
- Bug fix: overlapping buttons bottom-right
- Bug fix: "no artist results" shown for album type in scan log

**Should have (differentiators):**
- Typeahead shows 8 results (vinyl has hundreds of pressings; users need to distinguish)
- Optional `discogs_release_id` stored on WishlistItem (enables future precise-by-ID scanning)
- Email subject line includes best price (`[CRATE] Dark Side — $28.50 AU`)
- Email shows landed cost breakdown (core app value prop should appear in the alert)
- Email reduced to 5 columns from 8 (8 columns at 600px is unreadable on mobile)
- Brand mark font upgrade (Bebas Neue or Space Grotesk — execute-phase decision after visual comparison)
- Inline delete confirmation (replace native `confirm()` with in-place toggle)

**Defer to v1.2+:**
- Deal badge on dashboard cards (requires `typical_price` per item in route query — adds complexity)
- Typeahead for artist and label types (extend proven album pattern after ship)
- Pinned release badge on card (depends on typeahead being used in practice)

**Never build (anti-features):**
- Auto-select first Discogs result — silent wrong selection is worse than no selection
- Per-keystroke API calls with 0ms debounce — will hit 429 immediately
- Discogs cover art embedded in email — external images blocked by clients; auth token exposure risk
- Full HTML email framework (MJML, Foundation for Emails) — adds Node.js build step to a pure-Python project

### Architecture Approach

All v1.1 changes are additive or targeted modifications to the existing layered architecture. No new services, no migrations, no infrastructure changes are required. The build order is dictated by two dependency chains: the typeahead JS requires the backend endpoint (backend first, then frontend), and the image priority logic in `scanner.py` requires store adapters to emit `_cover_image` (adapters first, then scanner). All aesthetic changes (font, email, CSS) are fully isolated and can run in any order.

**Components changed:**
1. **`app/services/discogs.py`** — ADD `search_suggestions()` (single Discogs search call, no follow-up detail fetches; separate from full scan path to avoid 3–8s latency)
2. **`app/routers/wishlist.py`** — ADD `GET /api/discogs/search` endpoint (thin handler, returns JSON; no auth required — single-user internal browser call)
3. **`app/services/shopify.py`** — MODIFY to emit `_cover_image` from `featured_image.url`
4. **`app/services/scanner.py`** — MODIFY cover image priority: store image wins over Discogs (~8 lines replacement)
5. **`app/services/notifier.py`** — MODIFY to render email via Jinja2 template instead of inline f-string
6. **`templates/email_deal.html`** — ADD CRATE-branded email template (inline CSS only; no CSS custom properties; table layout)
7. **`templates/index.html`** — MODIFY: typeahead dropdown markup + JS in Add and Edit modals; card title hierarchy; button layout fix
8. **`static/style.css`** — MODIFY: button states, contrast token, 3-col breakpoint, spacing cleanup
9. **`static/fonts/`** — ADD WOFF2 file for brand mark font

**Not changed:** `app/models.py`, `app/database.py`, `app/main.py`, `app/scheduler.py`, `app/config.py`. No database migrations needed.

### Critical Pitfalls

1. **Discogs rate limit exhaustion from un-debounced typeahead** — Mandatory 300ms JS debounce + `AbortController` on every new fetch. Use a dedicated `search_suggestions()` function (single `/database/search` call, not the full scan path which makes 3–5 sequential requests). Verify via devtools network tab that fetches only fire after typing pauses. Missing debounce will cause scheduled scans to fail with 429 errors.

2. **Typeahead fetch race condition** — Rapid sequential queries produce two in-flight fetches; the earlier query may resolve after the later one and overwrite the dropdown with stale results. An `AbortController` pattern costs 5 lines and prevents this permanently. Shows up under Railway latency but not on local dev.

3. **Email HTML using CSS that email clients strip** — Never use CSS custom properties (`var(--color-bg)`), flexbox, or `<style>` body blocks in the email template. Inline all color values as hex literals. Table layout only. Verify by sending a test to Gmail web before merging — Apple Mail is not a representative test.

4. **iOS Shortcut API contract broken by schema change** — Any new field added to `WishlistItemCreate` (specifically `discogs_release_id`) must be `Optional[...] = None`. The Shortcut sends a fixed JSON body with no knowledge of new fields. A missing `Optional` causes silent 422 failures. Manually trigger the Shortcut after any schema change.

5. **CSS token blast radius** — The CRATE design system uses global CSS custom properties referenced across 545 lines and both templates. Changing a token value affects every element that uses it. Change one token at a time, review both full pages in browser before the next change.

6. **Web font FOUT on brand mark** — Use `font-display: block` (STACK.md) or `font-display: optional` (PITFALLS.md) — not `swap`. `swap` causes the CRATE wordmark to flash from system font to the web font on load. Add `<link rel="preload">` for the WOFF2 above the stylesheet link.

## Implications for Roadmap

Based on the build order established in ARCHITECTURE.md and the pitfall-to-phase mapping from PITFALLS.md:

### Phase 1: Discogs Typeahead
**Rationale:** Has the most cross-file touch points (discogs.py, wishlist.py, index.html) and introduces the only new backend API surface. Getting it working first validates the Discogs `search_suggestions()` function shape before any other phase depends on it. The iOS Shortcut risk and rate limit risk both live here — front-loading these catches breakage early.
**Delivers:** Album search typeahead in the Add and Edit modals; optional `discogs_release_id` stored on submit
**Addresses features:** Discogs typeahead (all table stakes + differentiators listed in FEATURES.md)
**Avoids:** Rate limit exhaustion (debounce + dedicated function), race condition (AbortController), iOS Shortcut breakage (Optional schema fields), typeahead blur/click timing bug (150ms delay on blur close handler)

### Phase 2: Image Source Prioritisation
**Rationale:** Backend-only change, fully independent of the typeahead. Produces correct data (store images preferred over Discogs thumbs) before any display work is done. Better to have image priority logic correct before the CSS polish phase adds visual improvements.
**Delivers:** Store-sourced cover images shown when available; Discogs thumb as fallback
**Addresses features:** Store image priority (table stakes)
**Avoids:** Storing `_cover_image` on `Listing` model — confirmed anti-pattern; the `_cover_image` sidecar is transient and belongs on `WishlistItem.artwork_url` only

### Phase 3: Brand Font Upgrade
**Rationale:** Fully isolated — one WOFF2 file, one `@font-face` declaration, one CSS rule on `.nav-brand`. Zero risk of regressions. Can be done in a single focused session.
**Delivers:** CRATE wordmark in Bebas Neue or Space Grotesk (final font choice made during execution via visual comparison)
**Addresses features:** Brand font upgrade (differentiator)
**Avoids:** FOUT on brand mark (font-display: block + rel="preload"); Google Fonts CDN dependency (self-hosted)

### Phase 4: Email HTML Redesign
**Rationale:** Self-contained change to `notifier.py` and a new template file. No schema changes, no route changes, no risk to the API contract. Architecture recommends extracting to a Jinja2 template file for maintainability over inline f-string.
**Delivers:** CRATE-branded HTML email with 5-column layout, inline CSS, plain-text alternative, price in subject line
**Addresses features:** Email UI redesign (all table stakes + differentiators)
**Avoids:** CSS custom properties in email (use hex literals), flexbox/grid layout (use table), missing `text/plain` part (always add `MIMEText` plain alternative)

### Phase 5: UI Polish
**Rationale:** CSS polish after all logic changes are in place. A single pass can clean up everything visible at once without risking regressions from prior phases. Changes are confined to `static/style.css` and minor template markup only.
**Delivers:** Button focus/active/disabled states, text-faint contrast fix, 3-column grid breakpoint, card title hierarchy, bug fixes (overlapping buttons, scan log type label)
**Addresses features:** Full UI polish pack (table stakes), bug fixes
**Avoids:** CSS token blast radius (change one token at a time with visual review after each change)

### Phase Ordering Rationale

- Typeahead first because it has the most cross-cutting dependencies and introduces the highest-risk elements (rate limiting, race conditions, schema changes)
- Image priority second because it is backend-only and produces correct data before display work begins
- Font and email third/fourth because both are fully isolated and can run in either order with no risk to each other or to prior phases
- CSS polish last because it makes most sense to do after all content-affecting logic is stable; it also catches any visual regressions introduced by earlier phases
- All phases are independently revertable — no phase depends on the previous one being present to function

### Research Flags

Phases likely needing brief research during planning:
- **Phase 1 (Typeahead):** Confirm the Discogs `/database/search` response shape against the live API before writing the endpoint. Consult shadcn MCP for the ARIA combobox/listbox pattern before writing the dropdown markup.
- **Phase 2 (Image Priority):** Verify the Shopify `suggest.json` `featured_image` field structure against a live store response before modifying `shopify.py`.

Phases with well-documented patterns (research-phase not needed):
- **Phase 3 (Font Upgrade):** Static file + `@font-face` CSS. Delivery and `font-display` strategy are fully documented in STACK.md and PITFALLS.md.
- **Phase 4 (Email Redesign):** HTML email constraints are fully documented. caniemail.com is the execution reference.
- **Phase 5 (UI Polish):** Pure CSS edits against an existing design system. CRATE tokens are all defined in `static/style.css`.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack confirmed from codebase. Only addition is optional premailer (skip by default). All library rejections are documented with rationale. |
| Features | HIGH | Discogs API fields confirmed from codebase + WebSearch. Email patterns from official sources. UI analysis from direct `ui-to-improve.txt` inspection. |
| Architecture | HIGH | Based on direct codebase inspection + FastAPI/Discogs official docs. Build order derived from actual file dependencies. Anti-patterns are specific and traceable to the existing code. |
| Pitfalls | HIGH | Discogs rate limits verified via official docs. Email client compatibility from caniemail.com. iOS Shortcut risk confirmed by reading existing schema. Race condition and FOUT patterns are established. |

**Overall confidence:** HIGH

### Gaps to Address

- **Font selection (Bebas Neue vs Space Grotesk):** Research identifies both as valid. Final decision deferred to Phase 3 execution — render both in the nav before committing. Not a planning blocker.
- **`discogs_release_id` storage decision:** FEATURES.md marks this as optional. ARCHITECTURE.md confirms it requires no migration (nullable column). Decide during Phase 1 planning.
- **Typeahead endpoint auth:** PITFALLS.md flags the unauthenticated endpoint as a potential abuse vector (anyone can exhaust the Discogs quota). ARCHITECTURE.md notes it is acceptable for a single-user private deployment. Resolve explicitly during Phase 1 planning by checking the existing auth pattern in `wishlist.py`.

## Sources

### Primary (HIGH confidence)
- Discogs API developer docs — `/database/search` response fields, 60 req/min rate limit, `X-Discogs-Ratelimit-Remaining` header
- Direct codebase inspection — `app/services/discogs.py`, `app/services/notifier.py`, `app/routers/wishlist.py`, `app/models.py`, `static/style.css`, `templates/base.html`, `templates/index.html`, `ui-to-improve.txt`
- Can I Email (caniemail.com) — HTML/CSS email client compatibility matrix
- Google Fonts Knowledge — WOFF2 self-hosting, font-display strategy, FOUT
- web.dev font best practices — preload + font-display for brand mark use
- Jinja2 docs — standalone `Environment` without FastAPI request context
- FastAPI official docs — endpoint routing

### Secondary (MEDIUM confidence)
- Mailtrap HTML Email Guide — inline CSS, 600px width, table layout confirmed
- Email on Acid — plain-text alternative, inline CSS best practices
- Algolia debounce guide — 300ms standard confirmed
- Typewolf Top 10 Brutalist Fonts — Bebas Neue aesthetic evaluation
- Email client market share 2025 — Apple Mail 58%, Gmail 30%
- stitch-mcp GitHub — outputs HTML/CSS (not React); `get_screen_code` tool confirmed

### Tertiary (reference / advisory)
- typeahead-standalone npm — evaluated and rejected (CDN dependency, ~1 year since last publish)
- premailer PyPI — evaluated as optional; skip unless email template exceeds ~25 inline style declarations

---
*Research completed: 2026-04-05*
*Ready for roadmap: yes*
