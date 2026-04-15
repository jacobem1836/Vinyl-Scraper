# Phase 16: Visual Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-14
**Phase:** 16-visual-foundation
**Mode:** discuss
**Areas discussed:** True Black surfaces, Warner Music accent direction, Scrollbar rework

---

## Gray Areas Presented

| # | Area | Requirement |
|---|------|-------------|
| 1 | Surface elevation strategy (bg=#000 context) | VIS-01 |
| 2 | Warner Music accent direction | VIS-03 |
| 3 | Scrollbar scope and rework level | VIS-02 |

---

## Area 1: Surface Elevation (VIS-01)

**Options presented:**
| Option | Description |
|--------|-------------|
| Flat black — all #000 | bg, surface, surface-alt all #000; borders only for separation |
| Slight elevation — cards ~#0a0a0a | Tiny lift on cards/modals |
| More contrast — cards #111 | Obvious lift, slightly less dark-luxury |

**User chose:** Flat black — all #000
**Reason:** Maximum darkness; separation via borders only

---

## Area 2: Warner Music Accent (VIS-03)

**Options presented:**
| Option | Description |
|--------|-------------|
| Stay white — stark/editorial | Keep #fff; Warner Music digital is stark white-on-black |
| Shift to gold/amber (~#c9a84c) | Warmer, label feel |
| Dark red / burgundy (~#8b2020) | Vinyl label reference |

**User chose:** Stay white
**Additional context:** User shared a Warner Music vinyl product grid screenshot — confirms #000 bg, pure white text, no card chrome, editorial restraint. White accent aligns with the reference.

---

## Area 3: Scrollbar Scope (VIS-02)

**Options presented (two questions):**

Style level:
| Option | Description |
|--------|-------------|
| Update to match #000 | Track=#000, thumb #333/#555 |
| Keep existing (#1a1a1a/#444) | Already partially done |
| Full rework — thinner + refined | 4px, transparent track, white rgba thumb |

**User chose:** Full rework — 4px, transparent, rgba(255,255,255,0.2) rest / rgba(255,255,255,0.4) hover

Scope:
| Option | Description |
|--------|-------------|
| Page only | Global ::-webkit-scrollbar |
| Include component scrollers | Also style .typeahead-dropdown and .table-container |

**User chose:** Include component scrollers

---

## Corrections Made

No corrections — all choices were direct selections from presented options.

---
