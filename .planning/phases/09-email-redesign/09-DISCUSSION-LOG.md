# Phase 9: Email Redesign - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
**Phase:** 09-email-redesign
**Areas discussed:** Email layout & hierarchy, Visual treatment, Deal summary content, Template approach

---

## Email Layout & Hierarchy

| Option | Description | Selected |
|--------|-------------|----------|
| Hero summary + listing table | Top section with item name, best price, % below typical as bold callout, then full listing table below | ✓ |
| Card-per-deal | Each deal listing gets its own card block — more visual but longer emails | |
| Compact summary only | Just key stats and a dashboard link — no listing table | |

**User's choice:** Hero summary + listing table
**Notes:** Scannable at a glance — hero for the key signal, table for details.

### Follow-up: Link placement

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, footer link | Single "View on CRATE" link at the bottom of the email | ✓ |
| Yes, in the hero block | Dashboard link in the hero summary | |
| No links needed | Email is informational only | |

**User's choice:** Footer link only
**Notes:** User initially excluded dashboard link from hero and per-listing links from table. Single footer link ensures the email has at least one actionable link.

---

## Visual Treatment

| Option | Description | Selected |
|--------|-------------|----------|
| Full dark | Near-black #0a0a0a body, #111111 content, white text — matches CRATE exactly | |
| Dark with light fallback | Dark primary + Outlook MSO conditional fallback for clients that strip bg-color | ✓ |
| Light with dark accents | White/light body with CRATE accent colors — universally safe but not CRATE | |

**User's choice:** Dark with light fallback
**Notes:** Belt-and-suspenders approach — dark CRATE aesthetic where supported, readable fallback for Outlook.

---

## Deal Summary Content

### Hero block data (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Item name + type badge | e.g. "Daft Punk — Random Access Memories" with [album] badge | ✓ |
| Best landed price | Lowest landed price from deal listings | ✓ |
| % below typical | How much below median landed price | ✓ |
| Dashboard link | Direct link to item detail page | |

**User's choice:** Item name + type badge, Best landed price, % below typical
**Notes:** Dashboard link excluded from hero (moved to footer instead).

### Table columns (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Title + Price + Source | Listing title, landed price in AUD, store/marketplace | ✓ |
| Condition | Vinyl condition (VG+, NM, etc.) | |
| Ships from | Where it ships from | ✓ |
| Direct listing link | "View" link to actual store page | |

**User's choice:** Title, Price, Source, Ships From
**Notes:** Condition and per-listing links excluded — keeps table compact.

---

## Template Approach

### Template structure

| Option | Description | Selected |
|--------|-------------|----------|
| Jinja2 template file | Separate .html file in templates/ — easier to iterate on layout | ✓ |
| Inline in notifier.py | Keep HTML string in Python file like today | |
| You decide | Claude picks | |

**User's choice:** Jinja2 template file
**Notes:** Separates layout from logic. Jinja2 already a project dependency.

### Plain-text fallback

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, auto-generated | Strip HTML to produce text/plain MIME part | ✓ |
| No, HTML only | Current behavior — only sends text/html | |

**User's choice:** Yes, auto-generated
**Notes:** Improves deliverability and supports text-only clients.

---

## Claude's Discretion

- Exact inline CSS implementation details
- MSO conditional comment structure
- HTML-to-plaintext stripping approach
- Email subject line format
- CRATE wordmark/header treatment in email

## Deferred Ideas

None — discussion stayed within phase scope.
