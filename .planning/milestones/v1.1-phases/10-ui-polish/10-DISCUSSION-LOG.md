# Phase 10: UI Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
**Phase:** 10-ui-polish
**Areas discussed:** Card title sizing, H2 token formalization, Disabled button scope, Design tooling requirement

---

## Card Title Sizing

| Option | Description | Selected |
|--------|-------------|----------|
| Use `--text-body` (16px) | Matches body text size, consistent with token system | |
| Create `--text-card-title` token | Dedicated token at 15-16px for card contexts | |
| You decide | Claude picks simplest approach meeting UIP-02 | ✓ |

**User's choice:** You decide
**Notes:** None — straightforward fix, Claude has discretion.

---

## H2 Token Formalization

| Option | Description | Selected |
|--------|-------------|----------|
| New `--text-subheading` token at 22px | Replace inline styles, own token distinct from H1's 28px | ✓ |
| Reuse `--text-heading` with utility class | `.text-subheading` class without new CSS variable | |
| You decide | Claude picks approach | |

**User's choice:** New `--text-subheading` token at 22px
**Notes:** None.

---

## Disabled Button Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Scan Now only | Strictly what UIP-06 says (detail page only) | |
| Both Scan Now and Scan All | Consistent behavior, both disable while scanning | ✓ |
| All buttons | Add `:disabled` to base button classes | |

**User's choice:** Both Scan Now and Scan All
**Notes:** None.

---

## Design Tooling Requirement

| Option | Description | Selected |
|--------|-------------|----------|
| Skip it | Fixes are mechanical, tooling adds overhead | |
| Light pass | Quick design audit after implementation | |
| Follow it fully | Invoke tools as specified | ✓ |

**User's choice:** Follow it fully
**Notes:** User clarified the point of this phase was to "majorly increase the impact of the UI" using design tools. The workflow is: `/design-for-ai` audits current UI, then `magic MCP` + `stitch` + `ui-ux-pro-max` drive the improvements. Mechanical fixes are folded into the broader design work.

---

## Folded Todos

- **Fix typeahead spinner not clearing** — folded into Phase 10 scope

## Deferred Ideas

- **Add manual selection of Discogs link or album** — deferred, belongs in v2 typeahead work

---

## Claude's Discretion

- Card title sizing approach (UIP-02)
