# Phase 24: Per-Item Notification Thresholds - Discussion Log (Assumptions Mode)

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-21
**Phase:** 24-per-item-notification-thresholds
**Mode:** assumptions
**Areas analyzed:** Data Model, Global Default, Notification Logic, Edit Form & Item Detail, Item Detail Display

## Assumptions Presented

### Data Model
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Make `notify_below_pct` nullable; existing 20.0 items keep value (not reset to NULL) | Likely | `app/models.py:13` — `nullable=False, default=20.0`; `app/database.py:27-29` — hand-written SQL migrations |
| `WishlistItemResponse` schema must change to `Optional[float]` | Likely | `app/schemas.py:50` — currently `float`; DB will have NULLs after migration |

### Global Default
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Global default as env var `NOTIFY_BELOW_PCT_DEFAULT` in Settings (default 20.0); no web UI | Likely | `app/config.py` — all settings env-var backed; no DB settings table |

### Notification Logic
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Fallback: `item.notify_below_pct if not None else settings.notify_below_pct_default` in notifier | Confident | `app/services/notifier.py:42` — reads field directly; scheduler uses same path |

### Edit Form UI
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Optional number input; blank → NULL in DB (= use global default) | Likely | `app/routers/wishlist.py:130` — currently `float = Form(20.0)`; update schema at `app/schemas.py:19` already `Optional[float]` |

### Item Detail Display
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Show effective threshold; "default" label when no custom value set | Likely | `app/routers/wishlist.py:64` passes raw value to template; `item_detail.html:~47` renders it |

## Corrections Made

No corrections — all assumptions confirmed.
