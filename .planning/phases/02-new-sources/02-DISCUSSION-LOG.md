# Phase 2: New Sources - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-02
**Phase:** 02-new-sources
**Areas discussed:** eBay credentials, Currency handling, Bandcamp approach, Per-source rate limits

---

## eBay Credentials

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, I have credentials | Proceed with Browse API | |
| Not yet — plan to set up | Implement with config guard, skip if EBAY_APP_ID not set | ✓ |
| No — skip eBay for now | Drop SRC-01 from Phase 2 | |

**User's choice:** Implement eBay adapter with config guard — user has applied for eBay Developer Program, credentials pending.

---

## eBay Token Caching

| Option | Description | Selected |
|--------|-------------|----------|
| Cache the token | Module-level or TTL cache, reuse for ~2hr lifespan | ✓ |
| Fetch fresh each scan | Simpler, extra HTTP call per scan | |

**User's choice:** Cache the OAuth app token.

---

## Currency Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Adapters return native currency; Phase 3 UI converts | Consistent with Discogs (USD), FX deferred | ✓ |
| Adapters convert to AUD at scan time | Simpler dashboard, FX lookup per scan | |

**User's choice:** Adapters return native currency. Phase 3 handles display/conversion.

---

## FX Rate Source (Phase 3 decision, noted here)

| Option | Description | Selected |
|--------|-------------|----------|
| Live rate via free API | exchangerate.host or similar, cached with TTL | ✓ |
| Hardcoded rate | Zero external dependency, manual updates | |

**User's choice:** Live rate API in Phase 3.

---

## Bandcamp Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Scrape bandcamp.com/search HTML | item_type=p filter for physical merch | ✓ |
| Skip Bandcamp in Phase 2 | Deprioritise, Discogs covers most of same catalogue | |
| Target artist/label pages directly | More reliable but misses album-level searches | |

**User's choice:** Scrape Bandcamp search HTML.

---

## Bandcamp Digital-Only Results

| Option | Description | Selected |
|--------|-------------|----------|
| Return empty list silently | Consistent with other adapters | ✓ |
| Return digital results with a note | Shows user Bandcamp has it digitally | |

**User's choice:** Return empty list silently.

---

## Per-Source Rate Limits

| Option | Description | Selected |
|--------|-------------|----------|
| Per-source semaphores in registry | Registry schema extension | |
| Global semaphore + internal delays | Keep Phase 1 approach | |
| Claude's discretion | Best for production | ✓ |

**User's choice:** Claude decides — "best for a production app."

**Claude's decision:** Module-level semaphores in each adapter. eBay: Semaphore(5), HTML scrapers: Semaphore(1) + sleep(1–2s). Remove global scan_semaphore from rate_limit.py.

---

## Deferred Ideas

- AUD FX conversion display → Phase 3
- Per-item condition filtering (DATA-01) → v2
- Egg Records, international stores → v2
