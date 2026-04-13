# Phase 15: Notification Expansion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-13
**Phase:** 15-notification-expansion
**Mode:** discuss
**Areas analyzed:** Price-drop trigger, Digest scope, Deal alert integration, Cool-down window

## Gray Areas Presented

### Price-drop trigger
| Option | Description |
|--------|-------------|
| Any decrease | Notify on any price decrease |
| Crosses notify threshold | Only if new price crosses notify_below_pct vs median |
| ≥X% drop (configurable) | New configurable threshold |

### Digest scope
| Option | Description |
|--------|-------------|
| One email per scan | All events across all items in single digest |
| One email per item | Each item's events together, separate per item |

### Deal alert integration
| Option | Description |
|--------|-------------|
| Merge — digest replaces it | Phase 15 rolls deal alerts into unified digest |
| Extend — keep existing | Keep send_deal_email, add separate path for new events |

### Cool-down window
| Option | Description |
|--------|-------------|
| 24 hours | ~4 scans before repeat |
| Same as scan interval | Every scan eligible to re-notify |
| 48 hours | Quiet, 2 days |

## User Decisions

### Price-drop trigger
- **Chosen:** Keep existing % approach AND add $ amount option — user can configure one OR the other per item
- **Notes:** "the existing implementation is a % amount, maybe keep this, and also add a $ amount they can set (an option for one or the other, not both)"

### Digest scope
- **Chosen:** One email per scan — all events across all items in single digest

### Deal alert integration
- **Chosen:** Merge — digest replaces existing send_deal_email. Unified code path.

### Cool-down window
- **Chosen:** Configurable setting (not hardcoded)
- **Notes:** "Should be a customisable setting"

## No Corrections Made

All decisions captured directly from user selections. No assumption overrides required.
