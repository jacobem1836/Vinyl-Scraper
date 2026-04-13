# Stack Research

**Domain:** Vinyl wishlist web app — UX polish, autocomplete, email redesign, web font, design tooling
**Researched:** 2026-04-05
**Confidence:** HIGH (no new frameworks; all additions are narrow, well-documented libraries against an existing stable stack)

> **v1.1 scope only.** The prior STACK.md (v1.0 scraping expansion) has been superseded. Scraping stack is unchanged and validated.

---

## Existing Stack — Do Not Change

| Layer | Technology | Version |
|-------|------------|---------|
| Web framework | FastAPI | 0.115.0 |
| Templates | Jinja2 | 3.1.4 |
| HTTP client | httpx | 0.28.0 |
| ORM | SQLAlchemy | 2.0.36 |
| CSS system | CRATE (hand-rolled) | ~545 LOC, `static/style.css` |
| JS | Vanilla, inline in templates | No build step |
| HTML parser | BeautifulSoup4 + lxml | 4.12.3 + 5.3.0 |
| Deployment | Railway + PostgreSQL | pg8000 1.31.2 |

**Critical constraint:** No JS build step. All frontend JS is inline in Jinja2 templates. Any JS addition must be hand-rolled or delivered via a CDN `<script>` tag — and CDN tags are undesirable (external request, latency, dependency on availability). This means the correct path for new frontend capability is always vanilla JS, not a library.

---

## Recommended Stack Additions

### 1. Discogs Typeahead / Autocomplete

**Architecture: FastAPI proxy endpoint + vanilla JS debounce + hand-rolled dropdown**

No new Python packages. No JS libraries. No CDN dependencies.

**Backend (one new route):**

Add `GET /api/autocomplete` to `app/routers/wishlist.py`. It accepts a `q` query parameter, calls the existing Discogs `/database/search` API (using `_get_headers()` from `app/services/discogs.py`), and returns a JSON array of `{title, release_id, year, thumb}` objects (max 8 results). This keeps the Discogs token server-side and avoids CORS entirely — the browser never calls Discogs directly.

The Discogs API rate limit for authenticated requests is 240 req/min. A 300ms debounce on the input means a fast typist generates at most ~3 req/s, well under the ceiling. The existing `VinylWishlist/1.0` User-Agent header already qualifies for the authenticated limit.

**Frontend (inline JS in `templates/index.html`):**

~50 lines of vanilla JS:
1. Attach `input` listener to the query field when type is "album"
2. Debounce 300ms before calling `/api/autocomplete?q=<value>`
3. Render results as `<ul role="listbox">` absolutely positioned below the input
4. On item selection: populate the query input, store `release_id` in a hidden `<input name="discogs_release_id">`, close dropdown
5. Dismiss on blur or Escape key

This pattern is consistent with the existing codebase style (scan panel, modal, toast are all hand-rolled at similar complexity).

**Supporting Libraries — None new:**

| Need | Solution |
|------|----------|
| HTTP request to Discogs | `httpx` (already in `requirements.txt`) |
| JSON response | FastAPI's `JSONResponse` (already used) |
| DOM manipulation | Vanilla JS (existing pattern throughout) |

---

### 2. Email HTML Redesign

**Architecture: Rewrite `html_body` f-string in `notifier.py` — no library**

The existing email is a plain f-string in `app/services/notifier.py`. The redesign is a HTML/CSS authoring task.

**Email-safe HTML rules (confirmed by research):**

| Rule | Why |
|------|-----|
| `<table>` layout, 600px max-width | Email clients have inconsistent CSS/flexbox/grid support; tables are universal |
| All CSS inline (`style=""` on each element) | Many clients (Gmail, Outlook) strip `<style>` blocks |
| No CSS custom properties | CSS variables not supported in email clients — use literal hex values |
| No shorthand CSS | Write `padding-top: 16px; padding-right: 16px` not `padding: 16px` |
| Add plain-text `MIMEText` part | Email-only HTML is treated as suspicious by spam filters |

**CRATE colour palette mapped to email literals:**

| Token | Hex | Usage in email |
|-------|-----|----------------|
| `--color-bg` | `#0a0a0a` | Email background |
| `--color-surface` | `#111111` | Table cell / card |
| `--color-border` | `#222222` | Table borders |
| `--color-text` | `#f5f5f5` | Primary text |
| `--color-text-muted` | `#777777` | Secondary labels |
| `--color-success` | `#34d399` | Price highlight |
| `--color-accent` | `#ffffff` | CTA text / headers |

The email sends from `notifier.py` via `smtplib` — no SMTP provider change needed.

**Optional: `premailer` for CSS inlining**

`premailer` (PyPI `premailer`, latest 3.10.0) parses an HTML template containing a `<style>` block and outputs fully inline-styled HTML. This allows authoring the email template with readable CSS rather than per-element `style=""` attributes.

- `lxml` is already in `requirements.txt` (version 5.3.0) — premailer's primary dependency is satisfied
- Single line at send time: `html_body = transform(html_template_string)`
- Adds one package and one import

**Verdict: Optional. Skip it if the redesigned template is straightforward.** The CRATE email design is a single-purpose deal notification, not a marketing newsletter. Authoring 20–30 inline style declarations is manageable without a preprocessor. Add `premailer` only if the template becomes complex enough that inline authoring is painful.

**Also add plain-text part (regardless of HTML redesign):**

The existing `notifier.py` attaches only `MIMEText(html_body, "html")` to the `MIMEMultipart("alternative")` message. Email deliverability best practice requires a plain-text alternative. Add a second `msg.attach(MIMEText(plain_body, "plain"))` before the HTML part. No new library needed.

---

### 3. CRATE Brand Font Upgrade

**Technology: Self-hosted WOFF2 + `@font-face` in `style.css`**

**Recommended font: Bebas Neue**

Bebas Neue is an all-caps condensed display sans-serif. The letterforms match the CRATE aesthetic: stark, compressed, no-nonsense. The brand mark "CRATE" in Bebas Neue with `letter-spacing: 0.15em` reads as purposeful rather than generic. Available under SIL Open Font License.

Applied to exactly one element: `.nav-brand`. No other element changes typeface. Body text, card titles, form labels, and price data remain on the system font stack.

**Delivery: Self-hosted, not Google Fonts CDN**

Fetch the WOFF2 file (latin subset, ~14KB) from Google Fonts or gwfh.mranftl.com, place it at `/static/fonts/bebas-neue-regular.woff2`, declare it in `style.css`:

```css
@font-face {
  font-family: 'Bebas Neue';
  src: url('/static/fonts/bebas-neue-regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: block;
}
```

Add a `--font-brand` custom property to `:root` and apply it to `.nav-brand`.

**Why self-hosted, not Google Fonts CDN:**
- No external DNS lookup on page load (reduces latency on Railway deployment)
- No third-party exposure of visitor IP to Google servers
- No CDN availability dependency
- Same file, zero runtime difference once cached

**`font-display: block`** is correct for a single above-the-fold brand mark. `swap` would cause the CRATE wordmark to flash from system font to Bebas Neue on load, which looks broken for a brand element. `block` holds the space blank for up to 3 seconds (font loads in <100ms on a warm cache; on first load the brief block is imperceptible).

**Preload in `base.html`:**

```html
<link rel="preload"
      href="/static/fonts/bebas-neue-regular.woff2"
      as="font"
      type="font/woff2"
      crossorigin>
```

This tells the browser to fetch the font early, before the CSS parser reaches the `@font-face` declaration, eliminating any visible flash.

**Alternative: Barlow Condensed Bold**

Barlow Condensed is slightly less stark than Bebas Neue — it has lowercase support and a more conventional display weight. If Bebas Neue reads as too stylized in context (inspect rendered output before committing), Barlow Condensed Bold is the fallback. Same delivery approach.

**No new Python packages or npm packages needed.**

---

### 4. Design Tooling During Development

The project specifies four tools that must be used during planning and implementation of every UI phase. These are MCP server tools, not runtime dependencies — they do not affect the deployed app.

| Tool | What It Does | Integration Pattern |
|------|-------------|---------------------|
| `mcp__magic__*` | 21st.dev Magic — generates UI components from natural language | Use as visual reference; output is React/Tailwind and cannot be used directly |
| `mcp__stitch__*` | Google Stitch — generates design screens from prompts; MCP extracts HTML/CSS | `get_screen_code` returns HTML/CSS directly; extract layout skeleton, adapt to CRATE CSS variables |
| `mcp__shadcn__*` | shadcn component registry | Use for ARIA patterns (combobox, dialog), accessibility audits; adapt to vanilla JS |
| `ui-ux-pro-max` skill | Design critique and UX analysis | Invoke before writing any CSS or HTML change |

**Magic MCP output caveat:** Magic generates React + Tailwind. This project has no React and no Tailwind. Use Magic to see what a component should look like and identify the correct ARIA role pattern, then implement the equivalent in vanilla HTML + CRATE CSS. Never paste Magic output directly.

**Stitch MCP output:** Stitch outputs HTML and CSS (not React components). `get_screen_code` returns raw HTML. This is directly actionable — extract the layout structure, replace Stitch class names with CRATE custom properties. Stitch is powered by Gemini 2.5 Pro and as of March 2026 supports generating up to five screens simultaneously.

**shadcn for ARIA patterns:** The typeahead dropdown needs a `role="combobox"` / `role="listbox"` / `aria-autocomplete="list"` pattern. shadcn's Combobox component documents the correct ARIA structure. Adapt to vanilla JS after confirming the accessible pattern.

---

## Summary: New Package Additions

| Package | Version | Condition |
|---------|---------|-----------|
| `premailer` | `3.10.0` | Optional — add only if email template uses `<style>` block authoring |

No other Python packages, no JS libraries, no npm packages added to the production runtime.

---

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `premailer` | `3.10.0` | Converts HTML `<style>` block to inline styles for email clients | Only if redesigned email template is complex enough that per-element inline authoring is unwieldy |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Alpine.js / htmx | A JS framework for one autocomplete field is overengineering; adds a CDN dependency for the entire app | 50 lines of vanilla JS |
| React + build step | Requires bundler, separate build process, deployment change; the app is server-rendered Jinja2 | Vanilla JS inline in templates |
| Tailwind CSS | Conflicts with the CRATE design system; hybrid utility-class + custom-property CSS creates maintenance confusion | CRATE CSS custom properties |
| typeahead-standalone (CDN) | External CDN request + ~8KB for logic that takes 50 lines to write; last published ~1 year ago | Hand-rolled vanilla JS |
| typeahead.js (Twitter) | Deprecated; requires jQuery; last maintained 2016 | Hand-rolled vanilla JS |
| Google Fonts CDN `<link>` | External DNS lookup, third-party privacy exposure, CDN dependency | Self-hosted WOFF2 |
| Mailgun / Postmark / SendGrid SDK | Personal tool sending one alert type; smtplib already works | Keep existing smtplib + `_send_smtp` |
| Select2 / Choices.js / Tom Select | Require CDN or npm/bundler; more code than the feature needs | Hand-rolled dropdown |
| premailer (if template is simple) | Adds a dependency and `lxml` transformation step where it adds no value | Inline styles authored directly |

---

## Integration Points

### Typeahead — Where Code Goes

| File | Change |
|------|--------|
| `app/routers/wishlist.py` | Add `GET /api/autocomplete` route; calls `_get_headers()` from `discogs.py`, uses `httpx` already imported |
| `templates/index.html` | Add typeahead JS block after the modal form; attach to `input[name="query"]` when type select = "album" |
| `templates/item_detail.html` | Same JS (or identical block) if the edit form on the detail page also needs typeahead |

The new autocomplete route can reuse `app/services/discogs.BASE_URL` and `_get_headers()` without modification. No new service file needed — the route handler is thin enough to live directly in `wishlist.py`.

### Font — Where Code Goes

| File | Change |
|------|--------|
| `static/fonts/` (new dir) | Add `bebas-neue-regular.woff2` (latin subset, ~14KB) |
| `static/style.css` | Add `@font-face` block at top; add `--font-brand: 'Bebas Neue', var(--font-sans)` to `:root`; apply `font-family: var(--font-brand)` to `.nav-brand` only |
| `templates/base.html` | Add `<link rel="preload">` for WOFF2 file in `<head>` before the stylesheet link |

### Email — Where Code Goes

| File | Change |
|------|--------|
| `app/services/notifier.py` | Replace `html_body` f-string with redesigned table HTML; add `msg.attach(MIMEText(plain_body, "plain"))` before the HTML attach call |

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| Vanilla JS debounce (hand-rolled) | typeahead-standalone via CDN | Never in this project — CDN dep for 50 lines is not a good trade |
| FastAPI `/api/autocomplete` proxy | Direct Discogs call from browser JS | Never — Discogs does not send permissive CORS headers; browser would block it |
| Self-hosted WOFF2 | Google Fonts `<link>` CDN | Only if you need Google Fonts' subsetting tooling and don't want to maintain the file yourself (not a concern here) |
| Inline f-string HTML for email | Jinja2 template file + `premailer` | Use the premailer path if the email template grows beyond ~25 style declarations or if you want to reuse the template in other contexts |
| Bebas Neue (all-caps display) | Barlow Condensed Bold | If Bebas Neue reads as too stylized in context — inspect rendered output before committing |

---

## Version Compatibility

`premailer 3.10.0` requires `lxml` (already `5.3.0`) and `cssutils` (pulled automatically). No version conflicts with FastAPI 0.115, SQLAlchemy 2.0.36, or any existing dependency.

Bebas Neue WOFF2 is a static file — no compatibility concern.

The new `/api/autocomplete` endpoint uses only FastAPI, httpx, and standard library — no compatibility concern.

---

## Sources

- Discogs API developer docs — authenticated rate limit: 240 req/min confirmed; `X-Discogs-Ratelimit` headers documented
- [typeahead-standalone npm](https://www.npmjs.com/package/typeahead-standalone) — v5.4.0, last published ~1 year ago; evaluated, rejected for this stack
- [HTML and CSS in Emails — designmodo.com (2026)](https://designmodo.com/html-css-emails/) — table layout, inline CSS requirement, 600px width confirmed MEDIUM confidence (industry consensus)
- [HTML Email Best Practices — emailonacid.com](https://www.emailonacid.com/blog/article/email-development/email-development-best-practices-2/) — inline CSS, plain-text alternative confirmed
- [premailer PyPI](https://pypi.org/project/premailer/) — lxml dependency, `transform()` API confirmed HIGH confidence
- [Google Fonts self-hosting knowledge](https://fonts.google.com/knowledge/using_type/self_hosting_web_fonts) — WOFF2 + `@font-face` pattern confirmed HIGH confidence
- [web.dev font best practices](https://web.dev/articles/font-best-practices) — preload + `font-display: block` for brand mark confirmed HIGH confidence
- [stitch-mcp GitHub](https://github.com/davideast/stitch-mcp) — outputs HTML/CSS (not React); `get_screen_code` tool confirmed HIGH confidence
- [21st.dev Magic MCP — PulseMCP listing](https://www.pulsemcp.com/servers/21stdev-magic-ui-generator) — outputs React/Tailwind; reference use only HIGH confidence
- [Bebas Neue — Google Fonts](https://fonts.google.com/specimen/Bebas+Neue) — WOFF2 latin subset available, SIL OFL license confirmed

---

*Stack research for: Vinyl Wishlist Manager v1.1 — UX Polish & Album Selection*
*Researched: 2026-04-05*
