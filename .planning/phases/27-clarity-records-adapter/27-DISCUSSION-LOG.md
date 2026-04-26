# Phase 27: Clarity Records Adapter - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 27-clarity-records-adapter
**Areas discussed:** Search strategy, Store location & currency, Out-of-stock handling, Pagination limit

---

## Search strategy

| Option | Description | Selected |
|--------|-------------|----------|
| BigCommerce search URL | `/search.php?search_query=...` — query-driven, 1–3 pages | ✓ |
| Full catalogue pagination | Fetch all products, filter locally — heavier | |
| Search with catalogue fallback | Try search, fall back if 0 results | |

**User's choice:** BigCommerce search URL
**Notes:** Consistent with every other adapter; full catalogue too heavy per-scan.

---

## Store location & currency

| Option | Description | Selected |
|--------|-------------|----------|
| Australian store | AUD, ships_from: Australia | ✓ |
| UK/US store | GBP/USD, overseas shipping | |
| Unknown | ships_from: None, AUD guess | |

**User's choice:** Australian store — AUD, ships_from: Australia

---

## Out-of-stock handling

| Option | Description | Selected |
|--------|-------------|----------|
| Filter out-of-stock | Only return available listings | |
| Include all, parse is_in_stock | Mark sold-out accurately, UI handles display | ✓ |
| Default is_in_stock: True | Don't parse stock, simpler | |

**User's choice:** Include all with accurate `is_in_stock`
**Notes:** User wants sold-out items to appear in listings but grayed out with "Sold Out" label. UI already handles this at `opacity: 0.5` via `is_in_stock: False`.

---

## Pagination limit

| Option | Description | Selected |
|--------|-------------|----------|
| Page 1 only | Fast, same as Juno/Bandcamp | ✓ |
| Up to 3 pages | More results, 3 requests per scan | |
| Until empty | All pages, unbounded | |

**User's choice:** Page 1 only ("unless it's likely to miss any regularly")
**Notes:** For targeted artist/album queries on a single store, page 1 covers the relevant results. Agreed this is sufficient.

---

## Claude's Discretion

- CSS selectors for BigCommerce HTML
- BeautifulSoup parser choice (lxml vs html.parser)
- Semaphore value and rate-limit sleep duration
- Logging prefix format
