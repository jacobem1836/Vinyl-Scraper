# Pitfalls Research

**Domain:** UX polish + API-backed typeahead + HTML email redesign on FastAPI/Jinja2/vanilla JS
**Researched:** 2026-04-05
**Confidence:** HIGH (codebase directly inspected; Discogs API and email client compatibility verified via web sources)

---

## Critical Pitfalls

### Pitfall 1: Discogs Typeahead Hammers Rate Limit

**What goes wrong:**
Each keypress fires a fetch to the new FastAPI typeahead endpoint, which in turn calls `GET /database/search` on Discogs. At 60 authenticated requests/minute, a fast typist sending ~3 characters per second exhales 180 requests/minute — 3x the limit. Discogs returns HTTP 429, the endpoint errors, and the UI shows nothing or breaks silently.

**Why it happens:**
The existing `discogs.py` pattern (used for scanning) opens a fresh `httpx.AsyncClient` per call and makes multiple sequential API calls. Typeahead reuses the same integration path but has a much higher call frequency driven by a human typing.

**How to avoid:**
- Debounce the JS input at 300-400ms before firing `fetch`. This is the single most important guard.
- Cache typeahead results per query string in-process (a simple `dict` or `functools.lru_cache` on the FastAPI endpoint) so repeated identical queries do not re-hit Discogs.
- The typeahead endpoint should use `type=release&format=Vinyl` and `per_page=5` — the cheapest possible search call, not the multi-step scan path.
- Do NOT reuse `_get_album_listings()` for typeahead. That function makes 3-5 sequential detail requests per result. Write a dedicated lightweight search function that returns only `id, title, thumb` from the search response.
- Respect `X-Discogs-Ratelimit-Remaining` response header and bail early if approaching 0.

**Warning signs:**
- Console network tab shows fetch calls firing on every keypress
- Discogs returns 429 responses; endpoint returns empty arrays silently
- Existing scheduled scans start failing with rate limit errors after typeahead is added

**Phase to address:**
Typeahead implementation phase (the new endpoint + JS). Must be designed in from the start — adding debounce as an afterthought after testing breaks scanning is harder to trace.

---

### Pitfall 2: Typeahead `fetch` Race Condition — Stale Results Overwrite Fresh Ones

**What goes wrong:**
With debounce in place, rapid sequential queries (user types "dark", then "dark side") can produce two in-flight fetches. If the first ("dark") resolves after the second ("dark side"), it overwrites the dropdown with stale results. The user sees suggestions for "dark" while "dark side" is typed in the input.

**Why it happens:**
Vanilla `fetch` has no built-in cancellation or sequence guarantee. This is the classic async race condition in typeahead UI — easy to forget because it rarely shows up in happy-path testing on a local dev server with near-zero latency.

**How to avoid:**
Use an `AbortController` to cancel the previous fetch before issuing a new one:

```js
let currentController = null;

function fetchSuggestions(query) {
  if (currentController) currentController.abort();
  currentController = new AbortController();
  fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal: currentController.signal })
    .then(r => r.json())
    .then(render)
    .catch(e => { if (e.name !== 'AbortError') console.error(e); });
}
```

**Warning signs:**
- Dropdown flickers between different result sets while typing
- Issue appears on Railway (remote latency) but not on local dev

**Phase to address:**
Typeahead JS implementation. A 5-line `AbortController` pattern applied from the start costs nothing and prevents a subtle production bug.

---

### Pitfall 3: CSS Token Change Has Unexpected Blast Radius

**What goes wrong:**
The CRATE design system uses CSS custom properties (`--color-text-faint`, `--text-heading`, `--space-md`, etc.) referenced across ~545 lines of CSS and in both HTML templates via inline `style=""` and class composition. Changing a token value (e.g. bumping `--text-heading` from 24px to 28px, or `--color-text-faint` from `#555555` to `#686868`) fixes the intended element but silently changes every other place that token is used.

**Why it happens:**
CSS custom properties are global by default. The design analysis in `ui-to-improve.txt` recommends several token value changes — these are correct fixes, but each has blast radius across both `index.html` and `item_detail.html` plus the modal, scan panel, toast, and table components.

**How to avoid:**
- Before changing any token value, grep for all usages: `grep -n "var(--color-text-faint" static/style.css templates/*.html`
- Change one token at a time, review both pages in browser before continuing
- When the type scale changes (`--text-heading`), explicitly verify the modal title, section headings, and nav brand all still work — they all reference this token

**Warning signs:**
- A "fixed" element looks right but something unrelated looks wrong on the same page
- The modal title suddenly looks too large after bumping `--text-heading`

**Phase to address:**
CSS polish phase. Each token change should be its own discrete edit with visual review before the next.

---

### Pitfall 4: HTML Email Uses CSS That Email Clients Strip

**What goes wrong:**
The current email in `notifier.py` is a raw HTML string — no `<style>` block, layout done with a `<table border="1">`. A redesign that adds `<style>` blocks, CSS custom properties, flexbox, or external web fonts will break in Outlook (~10-15% share) and some Gmail configurations where `<style>` blocks are stripped or scoped. The redesigned email looks polished in Apple Mail (58% share) but broken elsewhere.

**Why it happens:**
Modern CSS email pitfalls are counterintuitive. Developers apply the same mental model as web CSS, not realising that:
- CSS custom properties (`var(--color)`) are not supported in any email client
- Flexbox and grid layout are unreliable across Outlook and older Gmail
- Web fonts fail silently in Outlook and fall back to Times New Roman
- `<style>` blocks are sometimes inlined, sometimes stripped, sometimes scoped by Gmail

**How to avoid:**
- Keep layout as `<table>` based — not as a web best practice but as the email client reality for 2025
- Inline all CSS using `style=""` attributes — do not rely on a `<style>` block surviving delivery
- Do not use CSS custom properties in email HTML — write literal color values (`#0a0a0a`, not `var(--color-bg)`)
- Use a web font stack but provide strong fallbacks: `font-family: 'Inter', Arial, Helvetica, sans-serif`
- The CRATE aesthetic can be replicated in email with literal hex values and table layout — it just takes more verbose HTML
- Test against caniemail.com for specific properties before using them

**Warning signs:**
- Email preview in Apple Mail or browser looks great
- No test in Gmail web (where styles are often scoped) or any Outlook variant
- Using `var(--color-...)` anywhere in the email HTML string

**Phase to address:**
Email redesign phase. The email HTML in `notifier.py` should be extracted to a Jinja2 template file to make it editable without touching Python, and must be constrained to email-safe CSS from the start.

---

### Pitfall 5: iOS Shortcut API Contract Broken by Schema Change

**What goes wrong:**
The iOS Shortcut hits `POST /api/wishlist` with an `X-API-Key` header and a JSON body matching `WishlistItemCreate`. Any change to this endpoint — a new required field, a changed response schema, a moved route prefix, or a new auth requirement — silently breaks the Shortcut until manually tested on the phone. Failures show up as silent "Item not added" outcomes on the Shortcut side.

**Why it happens:**
The v1.1 scope does not touch the Shortcut endpoint directly, but adjacent changes can break it:
- Adding a new required field to `WishlistItemCreate` (e.g. a `discogs_release_id` from the typeahead) would cause Shortcut submissions to 422
- Moving `api_router` prefix or changing auth would 401/404 all Shortcut posts
- The typeahead-selected query might become a normalised format ("Artist - Title") that the scanner no longer matches as a freeform string

**How to avoid:**
- `WishlistItemCreate` must remain backward compatible: any new typeahead-derived fields (e.g. `discogs_release_id`) must be `Optional` with `None` default
- The `query` field must remain accepted as a plain string — the Shortcut sends raw text, not a Discogs-resolved release ID
- After any API schema change, manually trigger the iOS Shortcut and verify a 200 response
- The Shortcut endpoint is `POST /api/wishlist` with `X-API-Key` — do not move it

**Warning signs:**
- New field added to `WishlistItemCreate` without `Optional[...] = None`
- Any change to the `api_router` prefix (`/api`)
- Scanner behaviour changes when `discogs_release_id` is present but the Shortcut still sends `None`

**Phase to address:**
Typeahead implementation phase — the schema change is most likely to happen here when `discogs_release_id` is added to the item model.

---

### Pitfall 6: Web Font FOUT Breaks the CRATE Brand Mark

**What goes wrong:**
The CRATE brand mark in the nav relies on its font for its aesthetic identity (all-caps, `letter-spacing: 0.25em`). Adding a web font via `<link>` (Google Fonts or self-hosted) without proper `font-display` configuration causes a Flash of Unstyled Text on load — the brand mark renders briefly in the system fallback font, then snaps to the web font. On slow connections the FOUT period is noticeable and looks broken.

**Why it happens:**
Without `font-display: swap` (or `optional`), the browser blocks rendering until the font is fetched. With `swap`, text renders immediately in the fallback and then swaps — which causes layout shift if the font metrics differ. Neither default behaviour is ideal for a brand mark element that defines the page header.

**How to avoid:**
- If the font is for the brand mark only (narrow use), prefer `font-display: optional` — it uses the font only if it loads within the first frame; otherwise falls back permanently. No FOUT, no layout shift, no jarring swap.
- Preload the font file: `<link rel="preload" href="..." as="font" crossorigin>` placed above the stylesheet link
- If self-hosting, serve the font from the same Railway deployment as `style.css` to avoid an extra DNS lookup
- Keep a condensed monospace fallback (`"Courier New", monospace`) with similar visual weight so the fallback brand mark does not look comically different

**Warning signs:**
- The nav CRATE text flickers on page load in devtools throttled network simulation
- Testing only on local dev where the font loads instantly from the browser cache

**Phase to address:**
Font implementation phase. Decide `font-display` strategy before choosing or loading the font.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Reusing `_get_album_listings()` for typeahead | No new code needed | 3-5 sequential Discogs API calls per keypress — guaranteed 429 errors | Never — typeahead needs a dedicated lightweight search function |
| Inline CSS in email HTML string | Works today | Template unreadable; impossible to redesign without touching Python | Acceptable for the current plain-table email; must change for redesign |
| Hardcoding color values in email HTML | Reliable rendering | Design system drift — email colors diverge from CRATE tokens | Acceptable (email has different constraints than web); document the mapping |
| Skipping AbortController on typeahead fetch | Less code | Race condition on slow connections or Railway cold starts | Never — 5 lines of code, permanent protection |
| Google Fonts `<link>` without preload | Quick to add | FOUT on cold visits; extra DNS/connection overhead | Never for brand mark use — add `rel="preload"` |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Discogs `/database/search` for typeahead | Calling the existing scan path (which fetches release detail pages for each result) | Write a dedicated endpoint that calls `/database/search` once with `per_page=5` and returns only `id, title, thumb` — no detail fetches |
| Discogs rate limit headers | Ignoring `X-Discogs-Ratelimit-Remaining` in responses | Check the header in the typeahead endpoint and return an empty list (not a 429) if the remaining budget is low |
| HTML email with CRATE design | Using CSS custom properties or flexbox layout | Inline literal hex values; use `<table>` for layout; provide font fallbacks. Verify on caniemail.com |
| Google Fonts / self-hosted web font | Linking font without `rel="preload"` or without `font-display` declaration | Add `<link rel="preload">` and use `font-display: optional` for narrow brand-mark use |
| Typeahead dropdown closing on click | Dropdown closes on `blur` before the click on a suggestion registers | Delay the `blur` close handler by 150-200ms so the click event fires first |
| Image source prioritisation in listing dicts | `_cover_image` key only ever set on `listings[0]` in the current Discogs adapter | When store adapters return their own image URL, check store image first; do not assume `_cover_image` is always Discogs-derived |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| No debounce on typeahead input | Discogs 429s spike; scheduled scans fail; Railway logs fill with httpx errors | 300ms debounce in JS before fetch fires | Immediately on any sustained typing — does not require scale |
| Typeahead results not cached | Same query hits Discogs twice if user types, deletes, retype | Simple in-process dict cache with TTL on the FastAPI endpoint | Every repeated keypress in the same session |
| `asyncio.sleep(0.5)` inside typeahead | Existing scan delays carried over; typeahead takes 1-2s per result | Remove scan-pacing delays from the dedicated typeahead function | Immediately — user expects sub-500ms dropdown response |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Typeahead endpoint unauthenticated | Anyone can hammer the app's Discogs rate limit quota via the proxy endpoint | Add `Depends(require_api_key)` to the typeahead endpoint, matching the API auth pattern already in use |
| User query string reflected into email HTML without escaping | XSS in email clients that render raw HTML | The current `notifier.py` uses `html.escape()` — ensure the redesigned template preserves this for all user-sourced values |
| `discogs_release_id` stored without validation | Malformed IDs cause Discogs API errors that could exhaust rate limit | Validate as integer > 0 before storing or using in a fetch |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Typeahead closes when mouse moves to click a suggestion | User cannot select a suggestion — dropdown closes on `blur` before click registers | Delay the `blur` close handler by 150-200ms so the click event fires first |
| Typeahead selection overwrites query with no confirmation | User selects a release but the input just changes text — unclear if it worked | Show a small "selected" indicator (e.g. checkmark badge or pill) next to the input when a release is pinned |
| Web font causes nav layout shift on load | CRATE brand mark jumps position when font swaps | Use `font-display: optional` — no swap, no shift |
| Email redesign loses the `text/plain` fallback | Recipients with text-only clients see nothing | Add `MIMEText(plain_body, "plain")` to the `MIMEMultipart("alternative")` — text part should always be present |
| CSS token change applied globally | Modal title, section headings, and nav elements all change unexpectedly | Change one token, review both full pages before the next change |

---

## "Looks Done But Isn't" Checklist

- [ ] **Typeahead debounce:** Implemented in JS — verify with devtools network tab that requests fire only after the user pauses, not on every keypress
- [ ] **Typeahead AbortController:** In place — verify with devtools that previous requests are cancelled when new ones start
- [ ] **Typeahead endpoint auth:** Protected — verify that a request without `X-API-Key` returns 401
- [ ] **iOS Shortcut compatibility:** `discogs_release_id` (if added to schema) is `Optional` with `None` default — verify the Shortcut still gets a 200 after the model change
- [ ] **Email HTML safe CSS only:** No `var(--)` tokens, no flexbox/grid, no unguarded external font references — verify by sending a test email to Gmail web
- [ ] **Font FOUT:** Web font loading does not flash — verify by throttling to "Slow 3G" in devtools and watching the nav brand mark on first paint
- [ ] **CSS token blast radius:** Every changed token value verified across both `index.html` and `item_detail.html` — not just the element being targeted
- [ ] **Focus states on buttons:** All three button classes have `:focus-visible` styles — verify by tabbing through the page without using a mouse
- [ ] **Image source priority:** Store-sourced images appear on listings where the adapter provides them; Discogs image is the fallback, not always first

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Rate limit exhaustion from un-debounced typeahead | LOW | Remove or disable the typeahead endpoint temporarily; add debounce; redeploy. Discogs rate limit resets every 60 seconds |
| iOS Shortcut broken by schema change | LOW | Make the new field `Optional` with default `None`; redeploy. No DB migration needed if column is nullable |
| Email redesign broken in Gmail | MEDIUM | Fall back to the existing plain-table template; redesign with inline CSS only; test before shipping |
| Web font FOUT in production | LOW | Switch `font-display` from `swap` to `optional`; redeploy |
| CSS token change breaks unexpected elements | LOW | Revert the token value; re-scope the fix to a specific selector rather than changing the global token |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Rate limit exhaustion from typeahead | Typeahead endpoint + JS implementation | Network tab shows debounced requests; no 429s in Railway logs during test |
| Stale typeahead results (race condition) | Typeahead JS implementation | `AbortController` present in source; race condition tested under throttled network |
| CSS token blast radius | CSS polish phase | Both pages reviewed in browser after each token change before moving to next |
| Email CSS compatibility | Email redesign phase | Test email sent to Gmail web + Apple Mail before merging |
| iOS Shortcut schema break | Typeahead/model schema phase | All new schema fields are `Optional`; Shortcut manually triggered and verified after deployment |
| Web font FOUT | Font implementation phase | Slow 3G devtools simulation passes without visible brand mark flash |
| Unauthenticated typeahead endpoint | Typeahead endpoint implementation | Unauthenticated request returns 401 |

---

## Sources

- Discogs API rate limits: [Discogs Developers](https://www.discogs.com/developers) — 60 req/min authenticated, `X-Discogs-Ratelimit-Remaining` header
- HTML email CSS compatibility: [Can I Email](https://www.caniemail.com/), [Campaign Monitor CSS Guide](https://www.campaignmonitor.com/css/)
- Email client market share 2025: Apple Mail 58%, Gmail 30% — [Email Developer Compatibility Guide 2025](https://email-dev.com/the-complete-guide-to-email-client-compatibility-in-2025/)
- Web font FOUT best practices: [Google Fonts Knowledge — FOUT](https://fonts.google.com/knowledge/glossary/fout)
- Typeahead debounce + AbortController patterns: [Vanilla JS accessible autocomplete](https://dev.to/alexpechkarev/how-to-build-an-autocomplete-component-from-scratch-in-vanilla-js-45g0)
- Direct codebase inspection: `app/services/discogs.py`, `app/services/notifier.py`, `app/routers/wishlist.py`, `static/style.css`, `templates/base.html`, `templates/index.html`, `ui-to-improve.txt`

---
*Pitfalls research for: v1.1 UX Polish & Album Selection — FastAPI/Jinja2/Discogs typeahead/HTML email*
*Researched: 2026-04-05*
