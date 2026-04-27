# Requirements: Vinyl Wishlist Manager

**Defined:** 2026-04-27
**Core Value:** Show me the cheapest way to buy the records I want, right now.

## v1.6 Requirements

Requirements for the Public Release milestone. Each maps to roadmap phases.

### Infrastructure

- [ ] **INFRA-01**: App is deployed on a non-Railway host
- [ ] **INFRA-02**: PostgreSQL database migrated to new host or managed DB
- [ ] **INFRA-03**: Git push triggers automatic redeploy
- [ ] **INFRA-04**: All env vars (RESEND_API_KEY, eBay creds, DB_URL, API_KEY) configured on new host

### Auth

- [ ] **AUTH-01**: User can sign up with email and password
- [ ] **AUTH-02**: User can sign in with email and password
- [ ] **AUTH-03**: User session persists across browser refresh
- [ ] **AUTH-04**: User can reset password via email link (via Resend)
- [ ] **AUTH-05**: User can sign in with Google (OAuth)

### Data

- [ ] **DATA-01**: Wishlist items are scoped to the authenticated user
- [ ] **DATA-02**: Listings are scoped to the user's wishlist items
- [ ] **DATA-03**: Each user has a personal API key for the iOS Shortcut
- [ ] **DATA-04**: User can share a read-only public link to their wishlist

### Security

- [ ] **SEC-01**: All wishlist routes require authentication (redirect to login if not signed in)
- [ ] **SEC-02**: Rate limiting on auth endpoints (sign-up, sign-in, password reset)
- [ ] **SEC-03**: Passwords stored as bcrypt hashes

## Future Requirements

### Streaming Integrations

- **STREAM-01**: User can sign in with Spotify to auto-populate wishlist from saved albums
- **STREAM-02**: User can sign in with Discogs to auto-add from Discogs wantlist
- **STREAM-03**: User can sign in with Apple Music to auto-populate wishlist

### Notifications Expansion

- **NOTIF-EX-01**: Additional notification types (new-listing-from-preferred-store, rare-pressing-found)

### Mobile

- **MOB-01**: Native mobile app (iOS/Android)
- **MOB-02**: Spine View — shelf view collapsing grid into vertical spines

## Out of Scope

| Feature | Reason |
|---------|--------|
| Admin dashboard | Personal tool — single operator |
| Billing / paid tiers | Not monetising |
| Cassette/CD listings | Vinyl-only scope |
| Real-time chat | Not relevant |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | TBD | Pending |
| INFRA-02 | TBD | Pending |
| INFRA-03 | TBD | Pending |
| INFRA-04 | TBD | Pending |
| AUTH-01 | TBD | Pending |
| AUTH-02 | TBD | Pending |
| AUTH-03 | TBD | Pending |
| AUTH-04 | TBD | Pending |
| AUTH-05 | TBD | Pending |
| DATA-01 | TBD | Pending |
| DATA-02 | TBD | Pending |
| DATA-03 | TBD | Pending |
| DATA-04 | TBD | Pending |
| SEC-01 | TBD | Pending |
| SEC-02 | TBD | Pending |
| SEC-03 | TBD | Pending |

**Coverage:**
- v1.6 requirements: 16 total
- Mapped to phases: 0 (roadmap pending)
- Unmapped: 16 ⚠️

---
*Requirements defined: 2026-04-27*
*Last updated: 2026-04-27 after initial definition*
