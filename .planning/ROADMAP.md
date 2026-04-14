# Roadmap: v1.3 Visual Overhaul

**Milestone:** v1.3 — Visual Overhaul
**Defined:** 2026-04-14
**Phases:** 3 (continuing from v1.2's Phase 15)

## Overview

Cohesive visual refresh: Warner Music–inspired aesthetic, true black palette, typography hierarchy with item name > price, custom scrollbars, and two targeted consistency fixes. No backend/data changes.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 16 | Visual Foundation | True black palette + scrollbar styling + Warner Music direction | VIS-01, VIS-02, VIS-03 | 3 |
| 17 | Typography Overhaul | Thinner/crispier font + item-name > price hierarchy | TYPO-01, TYPO-02, TYPO-03 | 3 |
| 18 | UI Consistency Fixes | Scan toast unification + item-detail placeholder image | FIX-01, FIX-02 | 2 |

---

## Phase 16: Visual Foundation

**Goal:** Shift the visual foundation to a true black, Warner Music–inspired aesthetic and style scrollbars to match.

**Requirements:** VIS-01, VIS-02, VIS-03

**Success criteria:**
1. Dashboard, item detail, and modal surfaces render on `#000` — no near-black fallbacks
2. Scrollbars in app surfaces use custom track/thumb styling (not browser default)
3. Overall palette, spacing, and restraint read as "Warner Music–inspired" on visual inspection

---

## Phase 17: Typography Overhaul

**Goal:** Swap body/card typography to a thinner, crispier typeface and apply a hierarchy where item name is larger and heavier than price.

**Requirements:** TYPO-01, TYPO-02, TYPO-03

**Success criteria:**
1. New typeface loaded and applied across cards, dashboard, and item detail
2. On each card, item name is visually larger than its price
3. Hierarchy holds in modals and item detail (not just dashboard)

---

## Phase 18: UI Consistency Fixes

**Goal:** Fix two outstanding inconsistencies: the post-add scanning message and the item detail placeholder image.

**Requirements:** FIX-01, FIX-02

**Success criteria:**
1. "Item added, scanning in background" renders via the standard `#toast` primitive (same styling as other toasts) — no separate boxed UI
2. Item detail screen uses the new empty vinyl image asset as placeholder (not the old one)

---
*Roadmap created: 2026-04-14*
