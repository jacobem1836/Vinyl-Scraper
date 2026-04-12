# Pitfalls Research

**Domain:** Vinyl Wishlist Manager — v1.2 Signal & Polish (quality filters, UI feedback, notification expansion, security audit on existing FastAPI + CRATE + 6-scraper system)
**Researched:** 2026-04-12
**Confidence:** HIGH — grounded in existing codebase patterns (scanner.py, notifier.py, Discogs/Shopify adapters, CRATE CSS), well-documented Discogs API shape, and cross-browser scrollbar standards.

## Critical Pitfalls

### Pitfall 1: Relevance filter too aggressive — hides legitimate results

**What goes wrong:**
A naive title-match scorer (substring / fuzzy ratio threshold) discards valid listings because real-world titles are noisy: `"Kendrick Lamar - DAMN. [2017 TDE 1LP] SEALED"`, `"K.LAMAR *DAMN* vinyl NM"`, `"DAMN (Collectors Ed., red vinyl)"`. A threshold tuned on clean Discogs titles nukes eBay/Bandcamp/Juno results.

**Why it happens:**
Developer tests on Discogs (clean) output, picks a threshold that looks good, ships. Other sources carry catalogue numbers, pressing info, condition grades, and varying artist/album ordering that wreck string similarity.

**How to avoid:**
- Normalize both sides before scoring: lowercase, strip punctuation, collapse whitespace, remove noise tokens (`LP`, `VINYL`, `SEALED`, `NM`, `[...]`, `(...)`).
- Score by **token subset match**, not string similarity — "does every significant query token appear in the normalized title?" Weight artist vs album tokens separately.
- For `item_type == "artist"` or `"label"`, only require that type's tokens.
- **Start permissive, tighten later.** Preserve ~95% of current results on day one. Add a per-item `min_relevance` override so users can rescue known-good items.
- Show a "hidden by filter: N" count with reveal toggle — never drop results silently.

**Warning signs:**
- An item that used to show 8 listings now shows 0–1 post-filter.
- Filter rejection rate >50% on any single source → source-specific title format breaks normalization.

**Phase to address:** Relevance Filter phase — add a regression check that snapshots pre-filter counts and asserts post-filter counts ≥ 80% of baseline per source.

---

### Pitfall 2: Digital-only filter false positives on "digital remaster" vinyl

**What goes wrong:**
A keyword filter like `"digital" in title.lower()` kills legitimate vinyl titled `"(Digital Remaster, 180g)"`, `"Digitally Remastered 2LP"`. `"download"` substring can hit artist/album names too.

**Why it happens:**
"Digital" is overloaded: it means both "digital-only format" and "recorded/mastered digitally, shipped on vinyl". Keyword lists conflate the two.

**How to avoid:**
- Filter on **structured format fields**, not title text, when the source provides them:
  - Discogs: `format` field (`["Vinyl", "LP"]` vs `["File", "FLAC", "MP3"]`).
  - Bandcamp: product type (`Digital Album` vs `Record/Vinyl`).
  - Shopify: product tags/type.
  - eBay: item specifics `Format: Record` vs `Format: Digital`.
- Only fall back to title heuristics when structured data missing, and use **negative phrases only**: `"digital download only"`, `"mp3 only"`, `"flac download"`. Never the bare word `"digital"`.
- Apply at scrape time where possible (Bandcamp especially) rather than post-scan.

**Warning signs:**
- Bandcamp results drop to near-zero.
- Known vinyl with "remaster" in title disappears.
- Unit test: `"DAMN. (Digital Remaster, 180g Vinyl)"` returns "excluded" — bug.

**Phase to address:** Digital Filter phase — per-source fixtures with at least one "vinyl with digital in title" and one "true digital-only" listing; assert correct classification.

---

### Pitfall 3: Discogs seller location pulled from wrong endpoint

**What goes wrong:**
UI shows "no location" for every Discogs listing because seller country isn't on the endpoint the adapter currently calls. Developer assumes it's on search results, adds `.get("country")`, gets `None`, ships.

**Why it happens:**
Discogs separates database from marketplace:

| Endpoint | Has seller country? |
|----------|---------------------|
| `/database/search` | No — release metadata only |
| `/releases/{id}` | No — release-level, no seller |
| `/marketplace/listings/{listing_id}` | **Yes** — `ships_from` + seller object |
| `/marketplace/search` (HTML) | Yes — `ships_from` in each row |

Existing `discogs.py` builds listings from `/database/search`; the marketplace URL is constructed but never fetched.

**How to avoid:**
- Spike first: query one known release via all relevant endpoints, document which field carries `ships_from`. No UI code until data source confirmed.
- Options:
  - **(a)** HTML-scrape `/sell/release/{id}` marketplace page — 1 extra request per release with listings.
  - **(b)** Authenticated `/marketplace/listings/{id}` per listing — cleaner but N requests per release.
  - **(c)** Accept limitation: show "Discogs Marketplace" or omit chip entirely when unknown — never display "no location" (reads as a bug).

**Warning signs:**
- Column always `None` in DB — inspect real values before UI work.
- 429s after enabling per-listing fetches (Discogs: 60/min authenticated, 25/min unauthenticated).

**Phase to address:** Seller Location phase — gated by a spike artifact confirming the data source before implementation.

---

### Pitfall 4: Scan-now feedback races with existing 2-min dashboard polling

**What goes wrong:**
User clicks "Scan now". Spinner shows. Dashboard poll ticks mid-scan and refreshes state, wiping the spinner. Or scan completes but card shows stale price until next poll. Or user double-clicks → duplicate BackgroundTask → wasted HTTP calls / Discogs 429.

**Why it happens:**
Existing scan is fire-and-forget via `BackgroundTasks`. No per-item scan state exposed to frontend. Polling assumes state is stable between ticks.

**How to avoid:**
- Add per-item scan state: `scan_status` + `scan_started_at` on `WishlistItem` (or in-memory dict — fine for single-worker Railway).
- Frontend uses scan-status to: disable button while scanning, persist spinner across polls, force immediate refresh on transition to `done`.
- Scan-now endpoint idempotent: if already scanning, return 202 with current state, don't enqueue a second task.
- Invalidate dashboard TTLCache on scan completion (existing mutation pattern does this — ensure scan-now hooks in).
- Same guard must protect APScheduler's periodic run — one scan per item at a time across both paths.

**Warning signs:**
- Spinner flickers during scan.
- Toast fires but values don't update until next poll.
- Duplicate insert attempts blocked only by unique constraint.

**Phase to address:** Scan-Now Feedback phase — idempotency + cache invalidation in acceptance criteria, not just "spinner shows".

---

### Pitfall 5: Back-in-stock / price-drop notification spam loops

**What goes wrong:**
Listings flicker in/out of stock (Shopify inventory quirks, Bandcamp edition counters, Discogs marketplace churn). Each transition fires an email. User gets 5 emails for the same listing in 24h, disables notifications entirely. Same for price-drop when a cheap listing reappears.

**Why it happens:**
Naive impl compares current vs previous scan state and fires on any transition. No dedupe window, no magnitude threshold, no notification history.

**How to avoid:**
- Per-notification-type dedupe window: don't re-fire `(item_id, listing_url, type)` within N hours (24h back-in-stock, 48h price-drop, 72h deal).
- Store `last_notified_at` per type on Listing (JSON column or separate table).
- Price-drop: require ≥ X% drop AND below typical price. A $80 → $78 move is not an event.
- Back-in-stock: require out-of-stock state to persist ≥ M hours before in-stock counts — filters flicker.
- Consider **daily digest** option: bundle events into one evening email. Much lower spam risk.

**Warning signs:**
- Same URL appears in multiple emails within a day.
- Email volume jumps sharply after feature ships.
- User self-reports turning off alerts.

**Phase to address:** Notification Types phase — design dedupe/cooldown **before** send logic; write the dedupe test first.

---

### Pitfall 6: Security audit scope creep (or cursory pass)

**What goes wrong:**
"Security audit" either balloons into auth rewrite + CSP + OAuth (milestone never ships) OR is cursory and misses real issues (API key in logs, SSRF via artwork proxy, CVE in a pinned dep).

**Why it happens:**
"Audit" is vague. No defined scope → unbounded work or shallow pass.

**How to avoid:**
Lock scope to a concrete checklist BEFORE starting:
1. `X-API-Key` — `hmac.compare_digest`, never logged, not in error messages.
2. `/api/artwork` proxy — host allowlist (Discogs CDN, store CDNs), reject private IP ranges after DNS resolve (SSRF).
3. SQLAlchemy — confirm no raw SQL with user input.
4. Jinja autoescape on all `.html` templates; audit any `| safe` on user-controlled fields.
5. `pip-audit` or `safety check` on `requirements.txt`.
6. Bulk-import endpoint — same API-key guard as single add; per-IP rate limit.
7. Email HTML — user-entered query/artist escaped (autoescape covers if template is `.html`, not `.txt`).
8. Log scrub: grep for any `print` / log that emits headers, API key, SMTP password, DB URL.
9. FastAPI `debug=False` in prod; custom exception handler returns generic message.
10. HTTPS / HSTS at Railway verified.

Timebox: one phase, one pass. Anything outside the checklist → v1.3 backlog.

**Warning signs:**
- "While we're at it…" scope expansion.
- Audit phase longer than all other v1.2 phases combined.

**Phase to address:** Security Audit phase — scope locked at phase start; findings artifact committed (for future audit diffs).

---

### Pitfall 7: Custom scrollbars break cross-browser

**What goes wrong:**
Pretty scrollbars in Chrome (`::-webkit-scrollbar`). Firefox still shows defaults — it uses `scrollbar-width` / `scrollbar-color` (separate spec). Mobile Safari overrides can break momentum scrolling. Worst case: scrollbar invisible in Firefox because only Chrome was tested.

**Why it happens:**
Two non-overlapping standards. Developer copies a Chrome-only snippet and doesn't test elsewhere.

**How to avoid:**
- Always pair the two APIs:
  ```css
  .scroll { scrollbar-width: thin; scrollbar-color: var(--accent) transparent; }
  .scroll::-webkit-scrollbar { width: 8px; }
  .scroll::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 4px; }
  ```
- Never set `scrollbar-width: none` or hide via `display: none` unless replaced with a custom scroll affordance (a11y fail).
- Scope to specific containers — avoid global `html`/`body` overrides.
- Test desktop Chrome + Firefox + Safari and iOS Safari (momentum preserved).

**Warning signs:**
- Scrollbar invisible in Firefox.
- Mobile Safari feels sticky or loses rubber-band.
- Screenshot fine but keyboard tab can't scroll the region.

**Phase to address:** Scrollbar Polish phase — manual 3-browser + iOS screenshot check is acceptance criterion.

---

### Pitfall 8: Default type = "album" silently alters API / Shortcut contract

**What goes wrong:**
Changing modal default to always `"album"` feels harmless, but if the iOS Shortcut or bulk-import relies on the old default (or sends no type field), this silently alters data. The CLAUDE.md constraint explicitly forbids breaking the Shortcut contract.

**Why it happens:**
Developer treats "default" as a UI-only concept. API defaults are the real contract.

**How to avoid:**
- Confirm iOS Shortcut payload sends `type` explicitly (check Shortcut definition). If yes, UI default is harmless. If no, the change alters API behaviour.
- Confirm bulk-import parser — does it require explicit type or infer?
- **UI-only default**: set in the web form, not in the Pydantic model default. Keep API default unchanged for backward compatibility.
- Stretch: persist last-used type in localStorage — often beats a hard-coded default.

**Warning signs:**
- Post-change, Shortcut-added items all have `type=album` when they should be mixed.
- Bulk import produces wrong types.

**Phase to address:** Default Type phase — explicit API regression test: POST without `type` returns identical behaviour before/after.

---

### Pitfall 9: Logo swap misses email / favicon / OG / cached assets

**What goes wrong:**
Logo changed in header; old logo still in: email template (cached by mail clients for weeks), favicon (`.ico`), apple-touch-icon, OG/Twitter meta image, Railway static cache.

**Why it happens:**
Logos live in many places. "Change the logo" that only updates the header looks done in dev.

**How to avoid:**
Surface checklist:
- [ ] `app/static/logo.*` (all sizes)
- [ ] Favicon(s): `.ico`, 16/32 png
- [ ] Apple touch icon
- [ ] Email template `<img>` — **change filename** (`logo-v2.png`) because mail clients aggressively cache by URL
- [ ] OG / Twitter meta image
- [ ] Jinja templates hard-coding the path
- [ ] README screenshots

Mail client specific: Gmail proxies images through `googleusercontent.com` and caches aggressively; Outlook likewise. Cache-bust via filename, not just `?v=`. Consider CID-embedded logo for emails.

**Warning signs:**
- New logo in browser, old in Gmail web.
- Favicon still old in private window (no local cache).

**Phase to address:** Logo Change phase — acceptance includes real test email to Gmail + Apple Mail; verify new logo renders.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keyword-only digital filter | Ship in 1h | False positives on vinyl erode trust | Never |
| Global relevance threshold (no per-item override) | Simpler UI | Can't rescue known-good items | MVP of filter; add override before end of milestone |
| Scan-status in in-memory dict (not DB) | No migration | Lost on restart; breaks if >1 worker | Fine while Railway single-worker; document |
| Skip notification dedupe | Ship faster | Spam loop in prod; trust destroyed | Never |
| Grep-only security audit | Checks a box | Misses SSRF, timing, CVEs | Never — use full checklist |
| Chrome-only scrollbar | Works in dev | Firefox shows default, looks broken | Never |
| Over-write logo file instead of rename | Feels tidy | Mail clients serve cached old logo for weeks | Never — always rename |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Discogs `/database/search` | Expecting seller country | Seller data is marketplace-only; spike before implementing |
| Discogs rate limit | Per-listing marketplace fetch blows budget | Batch per release; TTLCache per release; back off on 429 |
| Bandcamp digital vs vinyl | URL `/album/` ambiguous | Inspect page for shipping/physical indicators; filter at scrape time |
| Shopify inventory | Treating `available: false` as permanent | Flickers during restock; require persistence window before firing |
| eBay Browse API titles | HTML entities / seller noise | Normalize before relevance scoring |
| SMTP remote images | Cached / blocked by clients | Rename file (cache-bust); alt text; consider CID inline |
| APScheduler + scan-now | Race with scheduled run | Single scan-status guard across both paths |
| FastAPI `BackgroundTasks` | Errors silent | Wrap in try/except; log structured; store last-scan-error on item |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Per-listing Discogs marketplace fetch | Scan time multiplies; 429s | Cache per release; degrade to "—" on rate-limit | >~50 Discogs items at 25/min unauth |
| Relevance filter in Python over N listings × M tokens on every dashboard load | Dashboard slows | Score at scan time; persist `relevance_score`; filter cheap at query | >500 listings |
| Notification dedupe table without index | Slow notify run | Index `(listing_id, notification_type)` | >10k listings |
| Scan-status poll every 2s while spinner shown | Extra DB hits | Bounded polling (60s max); or SSE | Always — keep bounded |
| Relevance threshold held in-memory only | User re-tunes on restart | Persist per-item in DB | Immediately |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging `X-API-Key` in request logs | Key leak via Railway log retention | Scrub auth headers; never log `request.headers` wholesale |
| Artwork proxy accepts arbitrary URLs | SSRF to Railway metadata / internal services | Host allowlist; reject private IP ranges post-DNS-resolve |
| `==` string compare for API key | Timing attack (low risk personal tool, trivial fix) | `hmac.compare_digest` |
| Unescaped user query in email HTML | XSS in webmail executing JS | Jinja autoescape on `.html`; no `\| safe` on user fields |
| `requirements.txt` never audited | Known CVEs in transitive deps | `pip-audit` in security phase; schedule quarterly |
| Bulk-import unauth'd / unrate-limited | Abuse if URL leaks | Same API-key guard; per-IP rate limit |
| Stack trace in error response | Info disclosure (paths, DB URL) | `debug=False`; generic exception handler |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silently hiding filtered listings | "Where did X go?" | Show "N hidden" with reveal toggle |
| "no location" chip on every Discogs row | Looks broken | Omit chip when unknown |
| Spinner with no timeout | User thinks app is frozen | 60s cap; show error with retry |
| Toast fires, dashboard unchanged | "Did it actually scan?" | Force refresh on completion |
| Daily back-in-stock emails for same listing | User disables all alerts | 24h dedupe window |
| Modal default changes Shortcut behaviour | Silent API regression | UI-only default |
| Scrollbars hide affordance in one browser | Region appears non-scrollable | Pair Firefox + WebKit rules |
| Logo updated UI, old in emails | Brand inconsistency | Rename file (cache-bust); test in real clients |

## "Looks Done But Isn't" Checklist

- [ ] **Relevance filter:** per-item override exists — verify known-good item can be rescued.
- [ ] **Relevance filter:** hidden count is visible, not silent.
- [ ] **Digital filter:** consults format/media fields first, not title.
- [ ] **Digital filter:** "Digital Remaster" vinyl fixture passes.
- [ ] **Seller location:** DB column actually populates with country strings, not `None`.
- [ ] **Scan-now:** double-click does not enqueue two scans.
- [ ] **Scan-now:** dashboard cache invalidated on completion (no waiting for next poll).
- [ ] **Notifications:** dedupe window test — firing twice rapidly, second suppressed.
- [ ] **Notifications:** out-of-stock must persist ≥ M hours before back-in-stock fires.
- [ ] **Default type:** API regression — POST without `type` unchanged.
- [ ] **Logo:** test email in Gmail + Apple Mail shows new logo.
- [ ] **Logo:** favicon in private window is new.
- [ ] **Scrollbars:** Chrome + Firefox + Safari desktop + iOS Safari all styled.
- [ ] **Security audit:** `pip-audit`, artwork proxy allowlist, constant-time API key compare, log scrub all done.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Relevance filter too aggressive | LOW | Lower threshold / add override; no data loss (listings hidden, not deleted) |
| Digital filter excludes vinyl | LOW | Revert to format-field logic; re-scan |
| Seller location ships with `None` | MEDIUM | Implement correct endpoint; backfill via targeted scan; show "—" in interim |
| Scan-now race duplicate listings | LOW | Unique constraint prevents duplicates; only wasted requests |
| Notification spam sent | MEDIUM | Global notifications off via env flag; fix dedupe; apologize; re-enable |
| Security issue found post-ship | HIGH | Rotate API key; force redeploy; review logs for exploitation |
| Scrollbars broken in Firefox | LOW | Add `scrollbar-width` rules; redeploy |
| Logo old in emails | LOW | Rename file; redeploy; future sends fixed |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Relevance filter too aggressive | Relevance Filter | Baseline listing-count regression per source |
| Digital false positives | Digital Filter | Fixture: "Digital Remaster vinyl" included; "MP3 download only" excluded |
| Seller location wrong endpoint | Seller Location | Spike artifact before UI; DB column populates real data |
| Scan-now race | Scan-Now Feedback | Idempotency + cache invalidation tests |
| Notification spam | Notification Types | Dedupe window test; flicker persistence test |
| Security scope creep | Security Audit | Locked checklist at phase start; findings artifact |
| Scrollbar breakage | Scrollbar Polish | Manual 3-browser + iOS screenshots |
| Default type breaks API | Default Type | API regression: POST without `type` unchanged |
| Logo misses surfaces | Logo Change | Surface checklist + test emails in 2 clients |

## Sources

- Existing codebase: `app/services/discogs.py`, `app/services/shopify.py`, `app/services/scanner.py`, `app/services/notifier.py`, `app/routers/wishlist.py`, CRATE CSS.
- Discogs API: long-stable separation of `/database` vs `/marketplace` endpoints; rate limits 60/min authenticated, 25/min unauthenticated.
- MDN scrollbar docs: `scrollbar-width` (Firefox standard) vs `::-webkit-scrollbar` (WebKit non-standard) — two distinct APIs, both needed.
- Webmail image caching: Gmail proxies through `googleusercontent.com`; Outlook caches aggressively — rename-file cache-bust is standard.
- Project CLAUDE.md: iOS Shortcut contract immutable; Railway single-worker assumption.

---
*Pitfalls research for: Vinyl Wishlist Manager v1.2 Signal & Polish*
*Researched: 2026-04-12*
