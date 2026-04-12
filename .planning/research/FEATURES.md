# Feature Research

**Domain:** Personal aggregator dashboard (vinyl marketplace scraper) — polish/signal milestone
**Researched:** 2026-04-12
**Confidence:** HIGH (ecosystem patterns for aggregator UX are well-established; MEDIUM on vinyl-specific relevance scoring since it's bespoke)

## Scope Note

v1.2 is a **polish + signal-quality milestone**. Existing features (adapters, scanning, email alerts, CRATE UI, typeahead, landed cost, iOS Shortcut API) are NOT re-researched. Focus is on nine feature clusters: filtering, feedback, branding, notifications, security.

---

## Feature Landscape

### Category: Filtering & Signal Quality

#### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Relevance filter / scoring** | Every aggregator (eBay, Discogs, Amazon) filters obvious junk. Users expect to not see a t-shirt when searching an album title. | MEDIUM | Token-overlap or fuzzy match (rapidfuzz / difflib) between normalized query and listing title. Score threshold per source. Keep rejected listings logged for debugging, hide from UI. |
| **Digital-only exclusion** | Vinyl-specific: digital downloads (Bandcamp, Discogs, Juno Download) pollute physical-record searches. | LOW | Keyword blocklist in title/format fields: `digital`, `mp3`, `flac`, `wav`, `download`, `lossless`, `24-bit`, `hi-res`. Also check Discogs `format` field (`File`, `FLAC`, `MP3`). Cheap filter, high win. |
| **Seller location display** | Aggregators show "Ships from X" — affects landed cost credibility. Currently broken for Discogs ("no location"). | LOW | Discogs marketplace API returns `seller.location`; fix is usually a field-path/nil-guard bug, not a design problem. |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Transparent relevance score in UI** | Show why a listing was ranked — user trusts the filter. | LOW | Render score as small badge or tooltip on card (e.g. "95% match"). |
| **User override ("show hidden listings")** | Lets power user inspect filter misses without permanently loosening threshold. | LOW | Toggle at item detail level, session-only. |

#### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **ML-based relevance model** | "Smart" ranking | Overkill for a solo tool, opaque, hard to tune, cold-start problem | Deterministic token scoring + format blocklist |
| **Per-source relevance UI config** | Flexibility | Multiplies config surface; one threshold per source in code is enough | Hardcode per-adapter threshold constants |
| **Hard delete of low-score listings** | "Clean DB" | Loses ability to re-tune threshold retroactively | Soft-hide: store score, filter in query |

---

### Category: Per-Action Feedback & Modals

#### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Per-item scan-now feedback (button → spinner → toast)** | Every modern dashboard (Linear, Vercel, GitHub) shows immediate local feedback on async actions. Silent buttons feel broken. | LOW–MEDIUM | Button state machine: `idle → loading → success/error`. Toast with count of new listings (or "no changes"). htmx swap or minimal JS — no SPA needed. |
| **Consistent modal/dialog system** | Mixed dialog styles read as unpolished. CRATE is already defined; the "Item added, scanning…" dialog is the outlier. | LOW | One modal component (class `.crate-modal` or similar) — same padding, border, backdrop, close affordance, motion. Reuse everywhere: add-item confirmation, delete confirm, future notification settings. |
| **Form defaults that match the common case** | 90%+ of adds are albums; defaulting to album saves a click per add. | TRIVIAL | `<select>` with `selected` on `"album"` option. |
| **Toast notifications for async results** | Non-blocking success/error feedback is standard. | LOW | Tiny toast container, auto-dismiss 3–5s, stack. Consistent with CRATE palette. |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Optimistic UI for scan-now** | Spinner appears the instant the click lands; result reconciles when backend returns. | LOW | Button immediately enters `loading` state; no waiting for HTTP round-trip to show change. |
| **Result-aware toast copy** | "3 new listings · 1 below typical" is more useful than "Scan complete". | LOW | Return counts from scan endpoint; template into toast. |

#### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Full page reload on scan-now** | Simple | Loses scroll position, feels slow | Inline swap / toast |
| **Blocking modal during scan** | "Shows it's working" | User can't do anything else; scans take seconds | Non-blocking spinner + toast |
| **Auto-dismiss error toasts** | Tidy UI | User misses failures | Errors persist until dismissed; successes auto-dismiss |

---

### Category: Branding & Visual Polish

#### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Logo parity between web app and email** | Brand consistency is basic hygiene. | TRIVIAL | One canonical SVG + PNG fallback; email uses absolute URL to PNG (Gmail/Outlook strip SVG). |
| **Custom scrollbar styling (subtle)** | Default Chromium/WebKit scrollbars clash with dark CRATE palette on desktop. Subtle styling reads as "designed". | LOW | `::-webkit-scrollbar` + `scrollbar-color` (Firefox). Keep widths standard (10–12px); don't hide them entirely (a11y). |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Dark-mode-aware email logo (PNG@2x, retina)** | Sharp on retina inboxes; respects dark mode in Apple Mail. | LOW | Ship `logo.png` (light bg) + `logo-dark.png`; pick via `prefers-color-scheme` media query in email CSS (Apple Mail supports; Gmail partially). |

#### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Fully hidden scrollbars** | "Cleaner look" | A11y regression; users lose scroll affordance on trackpad-less mice | Slim, low-contrast but visible |
| **Animated logo / loading lottie** | "Feels alive" | Distracting on a utility dashboard; bloats assets | Static logo; motion reserved for feedback (spinner, toast) |

---

### Category: Notification Type Expansion

#### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Back-in-stock alerts** | Core aggregator value — user was interested in a SKU; it went out of stock; it's back. Every wishlist tool (camelcamelcamel, Keepa, vinyl Discord bots) does this. | MEDIUM | Requires tracking listing `is_in_stock` transitions (false → true) across scans. Listings table already stores stock; needs transition detection + dedupe (don't re-alert on flapping). |
| **Price-drop alerts** | Similar: price dropped on a known listing since last scan. Distinct from deal-below-typical because it's relative to *this listing's* prior price, not the typical across all. | MEDIUM | Needs per-listing price history or prior-snapshot comparison. Minimum: compare current scan's price to previously stored price for same (item_id, url). |
| **Deal alerts (existing)** | Already shipped. Listing is X% below computed typical price. | — | Keep as-is. Now one of three notification types, not the only one. |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Per-item notification preferences** | User might care about back-in-stock for rare records but only deals for common ones. | MEDIUM | Columns on `wishlist_items`: `notify_deal`, `notify_back_in_stock`, `notify_price_drop` (booleans). Default all on. |
| **Unified digest email** | Batch all notification types into one email per scan run (instead of three separate emails). | MEDIUM | Group by item; template sections per notification type; skip sections with no events. |
| **Price-drop threshold (min %)** | Avoid spam on $0.50 price jitters. | LOW | Per-item or global setting; e.g. only notify on ≥5% drop. |

#### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Separate email per notification type** | "Clear categorization" | Inbox spam; solo user hates it | Unified digest with sections |
| **Real-time push notifications** | "Instant alerts" | Requires APNs/FCM infra; solo tool doesn't justify | Email is fine; user already checks inbox |
| **Notify on every stock change** | Completeness | Flapping inventory causes alert fatigue | Dedupe: only alert on false→true transition, cool-down 24h |

---

### Category: Security Audit

#### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **API key rotation & secret hygiene** | Shipped product with `X-API-Key` — audit for leaks, constant-time compare, no logging of header value. | LOW | `secrets.compare_digest()` for API key check; verify `.env` in `.gitignore`; scan git history for accidental commits. |
| **Input validation at API boundary** | Pydantic does most of this; audit free-form query field for length caps and control chars before passing to scrapers. | LOW | Max length on `query` field; strip control chars. |
| **Dependency vulnerability scan** | Baseline for any deployed Python app. | LOW | `pip-audit` or GitHub Dependabot. One-off run + optional CI. |
| **Outbound URL allowlist for artwork proxy** | `/api/artwork` proxy could be abused as SSRF vector if it accepts arbitrary URLs. | LOW | Restrict to Discogs/store domains; reject private IP ranges. |
| **Rate limiting on public-ish endpoints** | Even "personal" deployments on Railway get scanned. | LOW | Basic `slowapi` or per-IP token bucket on `/api/wishlist` and `/api/artwork`. |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **SECURITY.md in repo** | Documents threat model + response plan; useful for CHOMP internship portfolio. | LOW | One page: scope, secrets, reporting. |

#### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Full OAuth / user auth system** | "Proper security" | Out of scope — single-user tool; API key is sufficient | Keep `X-API-Key`; rotate + harden |
| **WAF / Cloudflare in front of Railway** | Defense in depth | Overkill for a personal tool with no attack surface beyond API key | Rate limiting + key rotation |

---

## Feature Dependencies

```
Relevance scoring ──enables──> Hide digital listings (shared filter pipeline)
                  └─enables──> Transparent "X% match" UI badge

Seller location fix ──independent──> (Discogs adapter bug; no upstream deps)

Scan-now feedback ──requires──> Consistent modal/toast system
                  └─requires──> Scan endpoint returns result counts

Modal consistency ──enables──> "Item added, scanning…" fix
                  └─enables──> Future delete-confirm, notification settings UI

Form default type="album" ──independent──> (trivial)

Logo update ──enables──> Email logo parity (same asset)

Back-in-stock alerts ──requires──> Listing stock-transition detection in scanner
                    └─requires──> Unified digest email template (or separate, but digest preferred)
Price-drop alerts   ──requires──> Prior-price snapshot (schema: store last-seen price per listing)
                    └─requires──> Unified digest email template
Deal alerts (exists) ──enhanced-by──> Unified digest (co-located with new types)

Per-item notify prefs ──requires──> Schema change on wishlist_items
                      └─enables──> All three notification types (deal / back-in-stock / price-drop)

Custom scrollbars ──independent──> (pure CSS)

Security audit ──touches──> API key check, artwork proxy, rate limits, deps
              └─independent of feature work, runs in parallel
```

### Key Dependency Notes

- **Notification-type expansion depends on existing deal-threshold logic:** The current `notifier.py` + `should_notify()` pattern is the template. Back-in-stock and price-drop are new notification *types* sharing the same dispatch + email-send infrastructure. Refactor `notifier` to accept a list of notification events per item rather than one "deal or not" boolean.
- **Price-drop requires a schema change** (or at minimum: previous-price snapshotting during scan). Back-in-stock can work off the existing `is_in_stock` column by comparing pre-scan vs post-scan state.
- **Scan-now feedback + modal consistency are tightly coupled** — both should use the same toast/spinner primitive. Build the primitive once in this milestone.
- **Relevance filter + digital-only filter share the same listing-filter pipeline.** Build one filter layer in `scanner.py` (post-adapter, pre-persist) that runs ordered filters: digital-format → relevance-score → persist.

---

## MVP Definition for v1.2

### Launch With (v1.2)

- [ ] **Digital-only filter** — trivial, high signal win, unblocks clean listings
- [ ] **Relevance scoring + hide low-score** — MEDIUM; the single highest-value polish item
- [ ] **Seller location fix (Discogs)** — trivial bug fix
- [ ] **Per-item scan-now feedback (spinner + toast)** — core UX parity with modern dashboards
- [ ] **Consistent modal system + fix "Item added, scanning…"** — enables everything downstream
- [ ] **Form default type="album"** — trivial
- [ ] **Logo update + email logo parity** — trivial
- [ ] **Notification type expansion: back-in-stock + price-drop + keep deal** — the milestone headline for signal
- [ ] **Custom scrollbar styling** — trivial CSS
- [ ] **Security audit pass** — baseline hygiene, parallel workstream

### Defer to v1.3+

- [ ] Transparent "X% match" badge in UI (nice-to-have; core filter more important)
- [ ] "Show hidden listings" override toggle (defer until filter mistakes become visible)
- [ ] Per-item notification preferences (global prefs fine for v1.2)
- [ ] Dark-mode-aware email logo (ship light-mode first)

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Digital-only filter | HIGH | LOW | P1 |
| Relevance scoring | HIGH | MEDIUM | P1 |
| Seller location fix | MEDIUM | LOW | P1 |
| Scan-now feedback (per item) | HIGH | LOW | P1 |
| Consistent modal system | MEDIUM | LOW | P1 |
| Form default type="album" | LOW | TRIVIAL | P1 |
| Logo + email parity | MEDIUM | LOW | P1 |
| Back-in-stock alerts | HIGH | MEDIUM | P1 |
| Price-drop alerts | HIGH | MEDIUM | P1 |
| Unified digest email | MEDIUM | MEDIUM | P1 (bundles with above) |
| Custom scrollbars | LOW | LOW | P2 |
| Security audit | MEDIUM | LOW | P1 |
| Per-item notify prefs | MEDIUM | MEDIUM | P2 |
| Relevance % badge in UI | LOW | LOW | P2 |

---

## Competitor / Reference Pattern Analysis

| Feature | camelcamelcamel / Keepa | Discogs marketplace | Our Approach |
|---------|-------------------------|---------------------|--------------|
| Back-in-stock alerts | Core feature, email-driven | Via "Notify me" wantlist | Email, triggered on stock false→true transition |
| Price-drop alerts | Core (graph-based) | No (fixed listings) | Compare current scan price to last-stored price per (item, url) |
| Relevance filter | Minimal (Amazon handles) | Substring + format filter | Token-overlap + format blocklist |
| Digital exclusion | N/A | Format filter in search UI | Keyword + Discogs `format` field block |
| Unified digest | Daily/weekly digest option | Per-listing emails | Single scan-run digest per user |
| Scan feedback | Server-side cron, no UI | Real-time search | Per-item scan-now button with toast |

---

## Sources

- Existing project context: `.planning/PROJECT.md` (v1.1 shipped, CRATE system, 6 adapters)
- Domain patterns: aggregator dashboards (camelcamelcamel, Keepa, Discogs marketplace wantlist), modern dashboard UX (Linear, Vercel for toast/feedback patterns)
- Discogs API: marketplace listing `seller.location` field, release `format` field for digital exclusion
- Python libraries referenced: `rapidfuzz` (relevance scoring), `secrets.compare_digest` (API key), `pip-audit` (deps), `slowapi` (rate limiting)
- Confidence: HIGH on feedback/branding/notification/security patterns (well-established web app conventions). MEDIUM on vinyl-specific relevance scoring tuning (bespoke, will need iteration after ship).

---
*Feature research for: Vinyl Wishlist Manager v1.2 Signal & Polish*
*Researched: 2026-04-12*
