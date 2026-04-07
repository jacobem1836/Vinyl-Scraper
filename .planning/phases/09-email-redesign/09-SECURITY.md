---
phase: 09
slug: email-redesign
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-07
---

# Phase 9 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| User data in email template | Wishlist item query and listing data rendered into HTML email body | User-supplied strings (item_name, listing titles) -> HTML output |
| SMTP credentials | Stored in env vars, used to authenticate email sending | Credentials -> SMTP server |
| Email From header | Sender identity in outbound email | Authenticated SMTP user -> recipient inbox |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-09-01 | Injection | templates/deal_alert.html | mitigate | Jinja2 `autoescape=True` on `_email_env` (notifier.py:15); all template variables HTML-escaped at render time | closed |
| T-09-02 | Information Disclosure | templates/deal_alert.html | accept | Email contains pricing/listing data — intentional for single authenticated user. No PII beyond user-owned data. | closed |
| T-09-03 | Injection | notifier.py template rendering | mitigate | Jinja2 `autoescape=True` on module-level `_email_env`; no manual `html.escape()` calls needed | closed |
| T-09-04 | Information Disclosure | _send_smtp SMTP credentials | accept | Credentials read from env vars via pydantic_settings, not hardcoded. Exception handler logs error message only, not credentials. | closed |
| T-09-05 | Spoofing | Email From header | accept | From address is `settings.smtp_user` (the authenticated sender). Single-user tool with no untrusted senders. | closed |

*Status: open / closed*
*Disposition: mitigate (implementation required) / accept (documented risk) / transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-09-01 | T-09-02 | Single-user personal tool; email data is the user's own wishlist and public listing data | Jacob Marriott | 2026-04-07 |
| AR-09-02 | T-09-04 | SMTP credentials stored in environment variables per industry standard; no shared access | Jacob Marriott | 2026-04-07 |
| AR-09-03 | T-09-05 | Single authenticated user sends email to themselves; no spoofing risk surface | Jacob Marriott | 2026-04-07 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-07 | 5 | 5 | 0 | gsd-secure-phase orchestrator |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-07
