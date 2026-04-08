# Phase 10: UI Polish — Research

**Researched:** 2026-04-08
**Domain:** CSS design system, Jinja2 templates, vanilla JS, visual hierarchy, accessibility
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Design tool-driven phase. Use `/design-for-ai` audit, `magic MCP` (`mcp__magic__*`), `stitch` (`mcp__stitch__*`), and `ui-ux-pro-max` skill to design and implement changes.
- **D-02:** Audit scope is broader than the original UIP list. The 4 remaining mechanical fixes are folded into broader design work.
- **D-03:** Card titles: bump from `--text-sm` (14px) to 16px (body size) — simplest approach.
- **D-04:** Create `--text-subheading: 22px` token. Replace inline `style="font-size: 22px"` on detail page H2s. H1 remains at `--text-heading` (28px), H2 at `--text-subheading` (22px).
- **D-05:** Both "Scan Now" (detail page) and "Scan All" (dashboard) get `:disabled` styling (opacity: 0.5, cursor: not-allowed).
- **D-06:** UIP-01, UIP-04, UIP-05, UIP-07, UIP-08, UIP-09, BUG-01 were implemented in Phase 5. Verify they still work — fix only regressions.
- **D-07:** Widen type scale to 3:4 ratio: `--text-label: 12px`, `--text-sm: 14px`, `--text-body: 16px`, `--text-title: 21px`, `--text-price: 28px`, `--text-heading: 36px`, `--text-heading-secondary: 21px`.
- **D-08:** 3-tier spacing: intra-card 6–8px, inter-card 16px, inter-section 40–48px.
- **D-09:** Deal/no-deal card tiers: Tier 1 (deal) = left accent border + deal badge; Tier 2 (normal) = standard; Tier 3 (no listings/scanning) = opacity 0.45–0.55 + muted border.
- **D-10:** Stats bar: stat values at 22–24px/600, stat labels at 11–12px/400 muted.
- **D-11:** Strip table `border-top` row rules; increase row padding to 10–12px; right-align numeric columns.
- **D-12:** Card title weight 600→500 after size carries hierarchy. Price stays 700.
- **D-13:** Monospace/slab for prices only (e.g. JetBrains Mono) — Claude's discretion.
- **Fix typeahead spinner not clearing** — folded into this phase.
- **Fix order:** Spacing tiers first → widen size range → strip table borders → weight adjustments last.

### Claude's Discretion

- **D-13:** Whether to add a monospace typeface for price rendering (e.g. JetBrains Mono). Adds value if it reinforces "data vs label" distinction without exceeding the two-family limit.

### Deferred Ideas (OUT OF SCOPE)

- **TYPE-05 / TYPE-06:** Manual selection of Discogs link / album — typeahead Phase 6 extension, not UI polish.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UIP-01 | `--color-text-faint` ≥ #686868, WCAG AA at 14px on #0a0a0a | Already set to #686868 in current CSS — verify pass, done |
| UIP-02 | Card titles use body size (16px), heading token 28–30px | Card h3 uses `.text-sm`; change class or set size directly; heading token now 36px per D-07 |
| UIP-03 | H1 and H2 visually distinct | H1 uses `.text-heading` (→36px); H2 gets new `--text-subheading` (22px) token per D-04 |
| UIP-04 | `:focus-visible` ring on all button classes | Already implemented — verify |
| UIP-05 | `:active` scale(0.97) on all button classes | Already implemented — verify |
| UIP-06 | Scan Now + Scan All `:disabled` state | Not yet implemented — add CSS + JS disabled toggling |
| UIP-07 | Modal: role="dialog", aria-modal, aria-labelledby, focus management | Already implemented — verify |
| UIP-08 | Inline delete confirmation, no native confirm() | Already implemented — verify |
| UIP-09 | 3-column grid at 1024px | Already implemented — verify |
| UIP-10 | Rogue 12px spacing values replaced with tokens | Audit CSS for hardcoded 12px; replace with space-xs (4) or space-sm (8) or space-md (16) |
| BUG-01 | Overlapping buttons (dashboard bottom-right) | Not reproduced in current scan panel code — visual verify |
| (folded) | Typeahead spinner not clearing after selection/type change | Investigate DOM mismatch or CSS specificity; see todo file |
| (D-07) | Widen type scale to 3:4 ratio | Token-only change in CSS :root |
| (D-08) | 3-tier spacing hierarchy | Card body gap, card-grid gap, section gap |
| (D-09) | Deal/no-deal card visual distinction | New CSS classes; Jinja2 conditional logic in index.html |
| (D-10) | Stats bar upgrade | Inline style changes in index.html stats section |
| (D-11) | Strip table row borders, right-align numbers | CSS .table td rules |
| (D-12) | Card title weight reduction | After size changes confirmed |
</phase_requirements>

---

## Summary

Phase 10 is a design-tool-driven UI polish pass on three files: `static/style.css`, `templates/index.html`, and `templates/item_detail.html`. The design audit identified three interconnected FLAGs (Typography, Composition, Visual Hierarchy), all caused by a compressed 14–28px type scale and uniform 24px spacing. The six convergent interventions address these at the token level: widen the type scale to a 3:4 ratio, introduce three tiers of spacing, add deal-card visual distinction, upgrade the stats bar, differentiate section headings, and strip table row borders.

Roughly half the formal requirements (UIP-01, UIP-04, UIP-05, UIP-07, UIP-08, UIP-09) were already implemented in Phase 5 and have been confirmed present in the current CSS and HTML. The remaining work is a mix of new token additions, CSS rule changes, and targeted JS fixes (typeahead spinner, disabled state toggling). The design tool workflow (ui-ux-pro-max, magic MCP, stitch) is required before each implementation decision per D-01.

**Primary recommendation:** Execute in audit-defined fix order — spacing tiers first, then type scale widening, then table border removal, then weight adjustments — so each change can be visually validated before the next tool is applied.

---

## Standard Stack

### Core (already in project)

| Item | Version/Value | Purpose |
|------|---------------|---------|
| CSS custom properties (`:root`) | Native CSS | All design tokens — spacing, color, type |
| Jinja2 | 3.1.4 [VERIFIED: project requirements.txt] | HTML templating — conditional card classes, stat display |
| Vanilla JS (IIFE) | ES6+ | Typeahead, scan panel, modal, toast — no framework |
| FastAPI static serving | 0.115.0 [VERIFIED: project requirements.txt] | Serves `style.css` and `typeahead.js` from `/static/` |

### Design Tool Stack (required per D-01)

| Tool | Invocation | Purpose |
|------|-----------|---------|
| `ui-ux-pro-max` skill | `python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "..." --design-system` | Design system recommendations, brutalism/dark mode patterns |
| `design-for-ai` skill | CHECKER mode on each changed surface | Post-change audit to confirm hierarchy improvements |
| `mcp__magic__*` | Magic component builder | Component pattern reference before implementing card tiers |
| `mcp__stitch__*` | Screen generation | Visual validation of token changes before writing code |

### No External Dependencies Added

This phase adds no npm packages, Python packages, or CDN resources. All changes are CSS and HTML/JS only.

---

## Architecture Patterns

### Token-First Changes (all CSS changes go through :root)

The existing design system is token-driven. Every change follows this pattern:

1. Update/add token in `:root` block of `style.css`
2. Update component rules to reference the new token
3. No hardcoded pixel values in component rules

```css
/* Pattern: add token, update reference */
:root {
  --text-title: 21px;   /* NEW */
  --text-price: 28px;   /* CHANGED from 20px */
  --text-heading: 36px; /* CHANGED from 28px */
  --text-subheading: 22px; /* NEW */
  --text-label: 12px;   /* NEW */
}

/* Then update class that uses it */
.card-title {
  font-size: var(--text-title);
  font-weight: 500; /* reduced from 600 per D-12, applied last */
}
```

[VERIFIED: read static/style.css — current tokens confirmed]

### Conditional Card Tier Pattern (Jinja2 + CSS)

The deal/no-deal card distinction (D-09) requires Jinja2 to classify cards, then CSS to style tiers:

```jinja2
{# In index.html card loop — classify tier #}
{% set has_deal = item.best_price is not none and item.deal_pct is not none and item.deal_pct >= item.notify_below_pct %}
{% set no_listings = item.listing_count == 0 and item.last_scanned_at is not none %}
{% set is_scanning = item.listing_count == 0 and item.last_scanned_at is none %}

<a href="/item/{{ item.id }}"
   class="card
     {% if has_deal %}card--deal{% endif %}
     {% if no_listings or is_scanning %}card--empty{% endif %}
     {% if is_scanning %}card--scanning{% endif %}"
```

```css
/* Tier 1: deal card */
.card--deal {
  border-left: 3px solid var(--color-success);
}

/* Tier 3: no-listing / scanning */
.card--empty {
  opacity: 0.5;
}
```

**Important:** The template context must expose `listing_count` and `deal_pct` for Jinja2 to classify. Confirm these are available in the route's enriched item objects before writing template code.

[ASSUMED] The dashboard enrichment result includes `listing_count` per item — need to verify field names from `app/routers/wishlist.py`.

### Disabled Button Pattern (UIP-06)

JS disables the button on click; CSS styles the disabled state:

```css
.btn-cta:disabled,
.btn-secondary:disabled,
.btn-destructive:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

```javascript
// In startScan():
function startScan(itemId) {
  const btn = itemId
    ? document.querySelector('[onclick*="startScan(' + itemId + ')"]')
    : document.querySelector('[onclick="startScan()"]');
  if (btn) btn.disabled = true;
  // ... existing fetch ...
  // re-enable in .then() or after poll completes
}
```

**Note:** The current `startScan` is in a closure in `base.html`. The button references it via `onclick="startScan()"` (dashboard) and `onclick="startScan({{ item.id }})"` (detail). Modifying `startScan` to accept and disable the calling button requires either passing `this` from the onclick or querying by a data attribute. Use a `data-scan-btn` attribute for clean selection.

[ASSUMED] The pattern above is viable — exact implementation to be confirmed by executor examining the scan panel JS in `base.html` lines 152–238.

### Spacing Tier Application

The 3-tier spacing system maps to existing token names:

| Tier | Value | Token | Where used |
|------|-------|-------|-----------|
| Intra-card | 6–8px | `var(--space-xs)` (4px) to `var(--space-sm)` (8px) | `.card-body` gap |
| Inter-card | 16px | `var(--space-md)` (16px) | `.card-grid` gap |
| Inter-section | 40–48px | `var(--space-2xl)` (48px) | `.stack-lg` between sections, or add `--space-section: 48px` |

Current state: `.card-body` uses `gap: var(--space-xs)` which is already 4px for intra-card — this is correct. `.card-grid` uses `gap: var(--space-sm)` (8px) — should be `var(--space-md)` (16px) for inter-card. `.stack-lg` uses `gap: var(--space-lg)` (24px) — undershoots the 40–48px target; consider bumping to `--space-2xl`.

[VERIFIED: read static/style.css — confirmed current gap values]

### Typeahead Spinner Fix

The bug: spinner shows then doesn't clear after selection or type change.

**Root cause investigation path (from todo):**

1. **CSS specificity check:** `.typeahead-spinner` has `animation: spin-positioned 0.8s linear infinite`. The `.hidden { display: none }` utility must override this. Confirm `.hidden` isn't overridden by animation specificity.

2. **Element ID mismatch:** `getEls(prefix)` returns `document.getElementById(prefix + "Spinner")`. IDs in templates: `addSpinner` and `editSpinner`. Prefix 'add' → 'addSpinner' ✓. Prefix 'edit' → 'editSpinner' ✓. IDs look correct.

3. **Timing issue:** `spinner.classList.add("hidden")` in `.then()` fires after fetch resolves. But if a new input event fires while fetch is in flight (fast typing), a new debounce timer starts and re-shows the spinner. The `AbortController` aborts the old fetch — but the `.catch(AbortError)` handler correctly hides the spinner. This path looks handled.

4. **Most likely cause:** The `animation` property on `.typeahead-spinner` may conflict with `display: none`. Some browsers continue running animation even with display:none on a parent but not the animated element itself. However since `.hidden` is on the spinner itself, this should work.

5. **Alternative explanation:** The spinner element in `item_detail.html` has the same IDs (`editSpinner`) as in `index.html`. Since both pages use the same `typeahead.js`, there's no conflict. But `item_detail.html` also initializes the edit modal from `initTypeahead('edit', editTypeSelect)` — same prefix as `index.html`. The prefix/ID scheme is shared correctly.

**Recommended investigation approach for executor:**
```javascript
// Add to selectResult() for debugging
console.log('selectResult called, spinner el:', getEls(prefix).spinner);
console.log('spinner classList before hide:', getEls(prefix).spinner?.classList.toString());
```

Check if spinner element exists at the time `selectResult` fires. If it does, the fix is CSS — ensure `.hidden { display: none !important; }` or remove the animation in the hidden state.

[VERIFIED: read static/typeahead.js — confirmed code paths and IDs]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 3:4 type scale values | Manual calculation | The fixed values in D-07 (12, 14, 16, 21, 28, 36px) are already computed from Tschichold's 3:4 ratio | Values are already locked decisions |
| Deal percentage calculation | New backend logic | `item.deal_pct` (or equivalent) — check if route already provides this | Scanner already computes typical_price |
| Design system for brutalism | Ad-hoc decisions | `ui-ux-pro-max` script with "vinyl brutalist dark utility" query | Skill has 67 styles including brutalism with palette/type recommendations |
| Monospace font from CDN | External dependency | Self-host JetBrains Mono woff2 in `static/fonts/` alongside BodoniModa | Project already self-hosts fonts; no CDN policy |

---

## Common Pitfalls

### Pitfall 1: Breaking the `.hidden` / animation conflict

**What goes wrong:** Adding `animation` to an element that also gets `.hidden { display: none }` toggled can behave inconsistently. Some properties (like `animation`) don't compose cleanly with `display: none` without explicit stopping.

**Why it happens:** CSS animations continue internal state even when element is display:none in some rendering paths. The `.typeahead-spinner` has `animation: spin-positioned 0.8s linear infinite`. When `.hidden` is added, display:none should stop layout/paint, but animation state may linger.

**How to avoid:** Add `animation: none` to `.typeahead-spinner.hidden` to explicitly stop the animation. Or add `.hidden { display: none; animation: none; }` — but this would affect all animated hidden elements. Prefer the targeted rule:

```css
.typeahead-spinner.hidden {
  animation: none;
}
```

**Warning signs:** Spinner reappears or flickers after selection.

### Pitfall 2: Type scale change breaks card layout proportions

**What goes wrong:** Bumping `.text-price` from 20px to 28px and `.text-heading` from 28px to 36px can cause overflow or layout collapse in constrained card bodies.

**Why it happens:** Cards have fixed aspect ratio (1:1 artwork). Card body has limited height after artwork. A 28px price + 21px title in a narrow card may overflow or force unwanted wrapping.

**How to avoid:** Test at all 4 grid widths (1 col mobile, 2 col 768px, 3 col 1024px, 4 col 1280px). The price display in `.card-body` uses `text-sm price-best` — confirm the new `text-price` class (28px) fits. If not, use `--text-title` (21px) for card prices specifically and reserve `--text-price` (28px) for detail page deal cards.

**Warning signs:** Price text wraps or overlaps other card content.

### Pitfall 3: Inline style specificity beats token changes

**What goes wrong:** Many elements in `index.html` and `item_detail.html` use inline `style="font-size: ..."` or `style="color: ..."`. Token changes in CSS don't affect these.

**Why it happens:** Inline styles have highest CSS specificity. If the stats bar text uses `style="font-weight: 600"`, changing `.stats-bar` CSS won't override it.

**How to avoid:** When changing token-based styling, grep for inline styles on the target elements. The H2 headings on `item_detail.html` explicitly use `style="font-size: 22px; font-weight: 600;"` — these must be removed and replaced with the new class/token.

**Confirmed inline styles to replace:**
- `item_detail.html` line 79: `<h2 style="font-size: 22px; font-weight: 600;">Best Deals</h2>`
- `item_detail.html` line 105: `<h2 style="font-size: 22px; font-weight: 600;">All Listings</h2>`
- `index.html` lines 13, 27, 33: stats bar inline styles for font sizes/weights

[VERIFIED: read templates/item_detail.html and templates/index.html]

### Pitfall 4: Card tier classification needs backend data

**What goes wrong:** Jinja2 needs `item.deal_pct` or similar to classify deal cards. If the route doesn't expose this, the tier system can't be implemented in the template.

**Why it happens:** The enrichment pipeline in `scanner.py` and `notifier.py` computes typical_price and deal thresholds, but what fields the dashboard route passes to the template may differ.

**How to avoid:** Before writing template code, check `app/routers/wishlist.py` dashboard route to confirm what fields are in the item context object. If `deal_pct` doesn't exist, use `item.best_price` and `item.typical_price` to compute it inline: `{% set deal_pct = ((item.typical_price - item.best_price) / item.typical_price * 100) if item.typical_price else none %}`.

**Warning signs:** Jinja2 UndefinedError when rendering index.html after template changes.

### Pitfall 5: Scan button disabled state interferes with form re-submission

**What goes wrong:** Disabling Scan All/Scan Now button prevents re-trigger, but if the page reloads (which happens after scan completes per the dashboard polling pattern), the button state doesn't reset — the page reload resets it naturally, which is correct.

**Why it happens:** JS `btn.disabled = true` is page-instance state. Page reload resets DOM.

**How to avoid:** No special re-enable logic needed for full-page-reload case. For single-page scan status panel (which doesn't reload), re-enable in the scan completion handler (`stopPolling()` or after the dismiss timer fires). Check the scan panel's `renderStatus` function.

---

## Code Examples

### Token change pattern (style.css)

```css
/* Source: existing style.css :root pattern + D-07 decisions */
:root {
  /* Typography — widened to 3:4 ratio */
  --text-label:   12px;   /* NEW — metadata, secondary labels */
  --text-sm:      14px;   /* unchanged — backward compat */
  --text-body:    16px;   /* unchanged */
  --text-title:   21px;   /* NEW — card album names */
  --text-price:   28px;   /* was 20px */
  --text-heading: 36px;   /* was 28px */
  --text-subheading: 22px; /* NEW — H2 section headings */
  --text-heading-secondary: 21px; /* NEW — "All Listings" vs "Best Deals" */
}
```

### Deal card CSS tiers (style.css)

```css
/* Source: D-09 decisions */
.card--deal {
  border-left: 3px solid var(--color-success);
}

.card--deal .card-price {
  font-size: var(--text-price);
  font-weight: 700;
}

.card--empty {
  opacity: 0.5;
  border-style: dashed;
}
```

### Stats bar upgrade (index.html)

```html
<!-- Source: D-10 decisions — stat values large, labels small/muted -->
<span class="stats-value" style="font-size: var(--text-subheading); font-weight: 600; color: var(--color-text);">{{ items|length }}</span>
<span class="stats-label" style="font-size: var(--text-label); color: var(--color-text-faint); display: block;">items watching</span>
```

### Table row border removal (style.css)

```css
/* Source: D-11 — Tufte 1+1=3 principle */
.table td {
  padding: 10px var(--space-md); /* was var(--space-md) — increase to 10-12px */
  /* border-top: 1px solid rgba(51, 65, 85, 0.7); — REMOVE */
}

/* Right-align numeric columns */
.table td.col-price,
.table td.col-landed {
  text-align: right;
}
.table th.col-price,
.table th.col-landed {
  text-align: right;
}
```

### Typeahead spinner animation fix (style.css)

```css
/* Source: Pitfall 1 — stop animation when hidden */
.typeahead-spinner.hidden {
  animation: none;
}
```

### Disabled button CSS (style.css)

```css
/* Source: UIP-06, D-05 */
.btn-cta:disabled,
.btn-secondary:disabled,
.btn-destructive:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Verification Status of Phase 5 Carry-Forwards

Reading the current code confirms these Phase 5 items are present and do not need reimplementation:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| UIP-01: `--color-text-faint: #686868` | PRESENT | `style.css` line 31 |
| UIP-04: `:focus-visible` on all buttons | PRESENT | `style.css` lines 254–259 |
| UIP-05: `:active` scale(0.97) | PRESENT | `style.css` lines 261–265 |
| UIP-07: `role="dialog"`, `aria-modal`, `aria-labelledby`, focus on open, restore on close | PRESENT | `index.html` lines 42, 95; `base.html` openModal/closeModal; `item_detail.html` line 184 |
| UIP-08: Inline delete confirmation | PRESENT | `item_detail.html` lines 64–72 |
| UIP-09: 3-column breakpoint at 1024px | PRESENT | `style.css` lines 295–299 |
| BUG-01: Overlapping buttons | NOT REPRODUCED | Scan panel in `base.html` uses fixed positioning separate from page buttons |

[VERIFIED: direct code read of all three templates and style.css]

---

## What Still Needs Implementation

| Item | File(s) | Nature |
|------|---------|--------|
| UIP-02: Card titles to 16px | `index.html`, `style.css` | Change `class="text-sm"` on h3 to new class or direct token |
| UIP-03: H1/H2 distinction via `--text-subheading` | `style.css`, `item_detail.html` | New token + remove inline styles |
| UIP-06: Disabled state CSS + JS | `style.css`, `base.html`, `item_detail.html` | CSS rule + startScan() modification |
| UIP-10: Rogue 12px values | `style.css`, `index.html` | Audit and replace (`.card-body` padding is `var(--space-sm) var(--space-md)` — 8px/16px, correct) |
| D-07: Widen type scale | `style.css` | Token additions and changes |
| D-08: 3-tier spacing | `style.css`, `index.html` | card-grid gap, stack-lg gap, card-body gap |
| D-09: Deal/no-deal card tiers | `index.html`, `style.css` | New card classes + Jinja2 conditional |
| D-10: Stats bar upgrade | `index.html` | Inline style changes or new CSS classes |
| D-11: Table border removal | `style.css` | Remove `border-top` from `.table td` |
| D-12: Card title weight | `style.css` | After type scale applied |
| D-13: Monospace font (discretion) | `style.css`, `static/fonts/` | JetBrains Mono woff2 + font-face + token |
| Typeahead spinner bug | `static/typeahead.js`, `style.css` | Debug + CSS animation fix |

---

## Environment Availability

Step 2.6: SKIPPED — this phase is purely CSS, HTML template, and JS changes. No external tools, services, or CLIs beyond the project's own running server are required. The design tools (`ui-ux-pro-max`, `magic MCP`, `stitch`) are skills/MCPs available in the Claude environment.

---

## Design Tool Workflow (Required per D-01)

The planner must schedule design tool invocations before each implementation wave:

### Before implementing (once per major surface):

```bash
# Generate design system context for brutalist dark vinyl tracker
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py \
  "vinyl brutalist dark utility personal tool dashboard" \
  --design-system -p "CRATE"
```

```bash
# Get UX rules for accessibility and loading states
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py \
  "accessibility animation disabled states" --domain ux
```

### After implementing each wave:

Run `design-for-ai` CHECKER mode on changed templates to confirm hierarchy improvements hold.

### For card tier design:

Use `mcp__magic__*` to reference card component patterns before writing deal/no-deal CSS.

Use `mcp__stitch__*` for visual screen generation to preview token changes.

---

## Open Questions

1. **Deal percentage field availability**
   - What we know: The dashboard route passes enriched items; `typical_price` is computed during scanning.
   - What's unclear: Does the enriched item dict in `app/routers/wishlist.py` include a pre-computed deal percentage, or does the template need to compute it from `best_price` / `typical_price`?
   - Recommendation: Executor reads `app/routers/wishlist.py` dashboard route before writing template code.

2. **Typeahead spinner root cause**
   - What we know: `spinner.classList.add("hidden")` is called in selectResult(), resetTypeahead(), and type change handler. IDs appear correct.
   - What's unclear: Whether CSS animation on the spinner element is preventing `display:none` from visually taking effect.
   - Recommendation: Add `animation: none` to `.typeahead-spinner.hidden` as the first attempted fix; if spinner still shows, use browser devtools to confirm element state.

3. **D-13 monospace font decision**
   - What we know: JetBrains Mono woff2 can be self-hosted (consistent with current BodoniModa self-hosting pattern). Would give price cells distinct data identity.
   - What's unclear: Whether the visual benefit at 28px price size justifies adding a third woff2 to static assets.
   - Recommendation: Include if the design tool audit (mcp__magic__*, ui-ux-pro-max) confirms it adds hierarchy signal. Skip if audited result shows size alone is sufficient.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Dashboard item context includes `listing_count` and `typical_price` for deal tier logic | Code Examples, Pitfall 4 | Template would error; need to compute from available fields or add to route |
| A2 | Scan button disable pattern using data attribute + startScan modification is viable | Architecture Patterns | May require refactoring startScan signature or using event.currentTarget |

---

## Sources

### Primary (HIGH confidence)

- Direct code read: `static/style.css` — all current token values, component rules, confirmed Phase 5 implementations
- Direct code read: `templates/index.html` — card structure, stats bar, modal, JS scan handlers
- Direct code read: `templates/item_detail.html` — H2 inline styles, delete confirmation, scan button
- Direct code read: `templates/base.html` — modal JS, scan panel JS, focus management
- Direct code read: `static/typeahead.js` — spinner flow, getEls(), selectResult(), initTypeahead()
- `.planning/phases/10-ui-polish/10-CONTEXT.md` — locked decisions D-01 through D-13
- `.planning/phases/10-ui-polish/10-DESIGN-AUDIT.md` — 10-point checker results, deep dives, convergence list
- `ui-to-improve.txt` — original full audit with contrast ratios and priority fix list
- `.planning/todos/pending/2026-04-07-fix-typeahead-spinner-not-clearing.md` — spinner bug details and root cause hypotheses

### Secondary (MEDIUM confidence)

- `~/.claude/skills/ui-ux-pro-max/SKILL.md` — confirmed skill availability and invocation pattern
- `~/.claude/skills/design-for-ai/SKILL.md` — confirmed CHECKER mode workflow

---

## Metadata

**Confidence breakdown:**
- Verification status of Phase 5 carry-forwards: HIGH — direct code read
- Type scale tokens (D-07): HIGH — values locked in context decisions
- Deal card tier implementation: MEDIUM — depends on route context fields (A1)
- Typeahead spinner fix: MEDIUM — root cause hypothesized, not confirmed
- Design tool invocation pattern: HIGH — skill files read directly

**Research date:** 2026-04-08
**Valid until:** No expiry — all findings are from direct codebase reads and locked context decisions
