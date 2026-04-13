# Phase 13: Signal Filters - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in 13-CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-13
**Phase:** 13-signal-filters
**Mode:** discuss
**Areas discussed:** scoring algorithm, threshold config, filter semantics, digital detection, Discogs location, observability

## Gray Areas Discussed

### 1. Relevance scoring algorithm
- Options: (a) rapidfuzz combined artist+title, (b) stdlib difflib, (c) custom token-overlap
- **Decision:** a (rapidfuzz, combined scoring)
- **User nuance:** "The issue was more about a specific album returning other album listings" — emphasized album disambiguation as the real problem to solve.

### 2. Threshold configuration
- Options: (a) global default + per-item override, (b) global only, (c) per-item only
- **Decision:** a (both)

### 3. Filter vs hide semantics
- Options: (a) store + filter at query, (b) drop at scan
- **Decision:** a (store all, filter at query — reversible)

### 4. Digital format detection
- Options: (a) format-string + Bandcamp URL heuristic layered, (b) format string only, (c) per-source rule
- **Decision:** a (layered)

### 5. Discogs seller location
- Options: (a) per-listing `/marketplace/listings/{id}` fetch, (b) search-result-first + scrape fallback, (c) user-known fix
- **Decision:** a (marketplace listings endpoint, authoritative)

### 6. Observability
- Options: (a) per-scan log line, (b) admin dashboard, (c) nothing
- **Decision:** a now, (b) deferred with explicit note in CONTEXT.md deferred section
