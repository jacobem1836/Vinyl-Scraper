# Phase 7: Image Source Priority + Scan Log Fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-07
**Phase:** 07-image-source-priority-scan-log-fix
**Mode:** assumptions (user deferred all decisions to Claude)
**Areas analyzed:** Image storage model, Image priority rule, Scraper updates, Scan log fix

## Assumptions Presented

### Image Storage Model
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Add image_url to Listing model | Confident | models.py shows Listing has no image field; WishlistItem.artwork_url is the only image storage; per-listing images need per-listing storage |

### Image Priority Rule
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Store image > Discogs > existing | Confident | IMG-01 requirement explicit; scanner.py:32-40 already has _cover_image pop pattern to extend |

### Scraper Updates
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Update all 6 non-Discogs adapters | Likely | All adapters parse HTML/API responses; image extraction is incremental; some may not have reliable images |

### Scan Log Fix
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Add item_type to scan_status.item_finished() | Confident | scan_status.py:32-40 stores item_type in current but drops it in log; base.html:223 only shows query+count |

## Corrections Made

No corrections — user deferred all decisions to Claude's judgment.
