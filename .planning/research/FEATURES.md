# Features Research

**Domain:** Personal vinyl record wishlist price tracker
**Researched:** 2026-04-02
**Confidence:** MEDIUM-HIGH (community evidence strong; AU-specific shipping figures are estimates)

---

## Table Stakes

Features users expect from any serious vinyl tracker. Missing = product feels incomplete or unprofessional.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Price + availability per wishlist item | Core value — "what does it cost right now?" | Low | Already exists; needs to be fast and reliable |
| Best price highlighted prominently | Users make buy/skip decisions at a glance | Low | Show best landed cost, not just list price |
| Multiple condition grades shown | NM vs VG+ vs VG is a real buying filter for collectors | Low | Discogs condition is the standard: M/NM/VG+/VG/G |
| Email/notification when price drops below threshold | "Tell me when it's cheap enough" is the primary alert need | Med | Already exists; threshold must be per-item, not global |
| Condition filter on alerts | Don't alert on VG when user wants VG+ minimum | Med | Top Discogs complaint — users want per-item condition gates |
| Seller location filter | Shipping from US/EU to AU dominates landed cost | Med | Allow filtering by "ships from AU" or region whitelist |
| Landed cost (price + estimated shipping) | Raw price is meaningless for AU buyers importing | Med | Already computed; must be clearly labelled and accurate |
| Remove item / mark as purchased | Wishlist hygiene — bought records should leave the list | Low | Obvious; easy; missing or clunky = frustration |
| Search / add by artist, album, label | Not everyone knows Discogs release IDs | Low | Already exists via web form + iOS Shortcut |
| Price history / trend | Is $30 cheap for this record, or normal? | Med | Popsike.com built a business on this. Users expect it. |

---

## Differentiators

Features that set this apart from Discogs' own wantlist and generic trackers. Not expected, but genuinely valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Multi-source price aggregation | Discogs only shows Discogs. This shows Discogs + AU stores + Juno + Bandcamp in one view | High | The core differentiator. No other tool does this for AU buyers |
| "Best deal right now" with source breakdown | One clear answer: "Buy from [store X] for $AUD Y landed" | Med | Presentation layer on top of aggregation |
| AU-first store coverage | Clarity Records, Discrepancy Records, Egg Records etc. are invisible to global tools | High | Local store results = no shipping cost; price competitiveness flips |
| AU currency as the default throughout | Every tool defaults to USD. An AU-first tool showing AUD natively is immediately more useful | Low | Apply FX conversion at ingestion; display AUD always |
| Pressing/edition awareness | AU pressing vs US import vs EU repress matters for price AND desirability | High | Requires per-result metadata; complex but powerful |
| Fast scan on demand ("check now") | Scheduled scans are fine; but "check this item now" is a power-user ask | Med | Per-item manual rescan, not full list rescan |
| iOS Shortcut quick-add staying fast | Adding from phone must feel instant — async queue the scan, return immediately | Med | Currently blocks on scan; decoupling scan = huge UX win |
| Clean record artwork as visual anchor | Spotify proved cover art makes a collection feel alive vs spreadsheet | Med | Fetch and cache album art; use as card hero image |
| "Why this price?" transparency | Show the breakdown: base price + shipping estimate + FX = landed cost | Low | Trust-building; users want to know how the number was derived |
| Wishlist priority / ranking | Mark some records as "really want" vs "would be nice" | Low | Simple 3-tier or star rating; affects alert threshold logic |

---

## Anti-Features

Things deliberately NOT worth building for a personal tool.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| User accounts / auth system | Single user; massive overhead for zero gain | Hardcode single-user; API key for iOS Shortcut is sufficient |
| Social / sharing features | Not a social product; adds complexity, creates maintenance surface | Keep it private; "shareable quality" means good visuals, not social features |
| Auction bidding or purchase flow | Discovery only — pulling transaction into the tool adds legal/complexity risk | Link out to marketplace listing; never handle money |
| Mobile-native app | iOS Shortcut handles the mobile add case; web dashboard is fine on desktop | Keep web-only dashboard; invest in quick-add iOS Shortcut reliability instead |
| Record collection tracking | This is a wishlist + price tool; collection management is a different product (Discogs already does it well) | Track wishlist items only; mark as "purchased" to remove |
| AI-generated release recommendations | Creep risk; adds an unpredictable data dependency | Surface what the user asked for; don't guess what else they might want |
| Full marketplace / seller profiles | Not a marketplace; just a price aggregator | Deep-link to the source listing; never replicate seller profiles |
| Complex notification channels (push, SMS, Slack) | For a personal tool, email is enough | One email channel, well-formatted |

---

## UI/UX Patterns

What works in Spotify, Discogs, RateYourMusic, and music apps for record browsing and price discovery.

### What Spotify gets right (applicable here)

- **Cover art as the hero.** Tiles and cards replaced lists. Album artwork triggers memory and emotion in a way text cannot. Every record card should lead with the cover at reasonable size.
- **Dark background by default.** Easier on eyes for browsing late at night; makes artwork pop more than a white background. Dark palette is the standard in music/vinyl tooling.
- **Horizontal scrolling rows for category groupings.** Works well for "Best deal today", "Recently added", "Newly available". Avoids the overwhelming full-grid when the list is long.
- **Minimal chrome; content-forward layout.** Navigation hidden or minimal. Sidebar or bottom nav, not persistent top nav bars eating vertical space.
- **One primary action per view.** Spotify's "Play" is always obvious. For this app: each wishlist card should have one obvious CTA — "View listing" or "Buy now" — not a table of actions.

### What Discogs gets wrong (avoid these)

- **Identical release links with no visual differentiation.** Clicking through 6 versions of the same album to find the right pressing is a top complaint. This app should roll up to one wishlist item and show differentiated results (pressing, condition, source) clearly.
- **Price without context.** Discogs shows a price range but not whether today's listing is cheap or expensive. Price history / typical price context is the missing layer.
- **Wantlist as a flat list.** No priority, no grouping, no status. A small amount of structure (priority tier, "checking", "found a deal") makes it far more useful.
- **Notifications with no filtering.** Sending alerts for VG copies when the user wants VG+ is the most-complained-about Discogs limitation. Per-item condition gates are non-negotiable.
- **UI that feels like a database.** RateYourMusic is praised for music knowledge but criticised for visual density. Discogs has the same problem. The goal here is a dashboard, not a database view.

### What RateYourMusic does well

- **Master release view.** Rolls up all pressings of an album into one entry; shows country flags and pressing-specific info at a glance. Avoids the Discogs click-through-versions problem.
- **Incremental complexity.** Simple at first glance; details revealed on drill-down. Good for a wishlist dashboard that needs to show lots of records without overwhelming.

### Effective patterns for price discovery specifically

- **Best price prominently badged on the card** — not buried in a table inside the detail view. Users scanning a 30-item wishlist need to see "AUD $28 landed" at the card level.
- **Color/icon coding for deal status.** Green = below typical price. Red = above. Neutral = normal. Reduces cognitive load to zero for scanning.
- **Price breakdown on hover/tap.** "$22 + ~$8 shipping from US = $30 landed" should be visible without navigating away. Tooltip or slide-out panel.
- **"Last checked" timestamp.** Users need to know if data is fresh. A 6-hour scan cycle means some prices are stale; show when each item was last scanned.
- **Source attribution on every listing.** "From Discogs (AU seller)" vs "From Juno Records (UK)" matters enormously for shipping estimates. Source + location must be on every result row.

---

## AU-Specific Needs

### Currency

- **Display AUD natively throughout.** All prices should be pre-converted to AUD at point of ingestion. Never show USD/GBP/EUR to the user unless as an aside. This is the single biggest quality-of-life gap in global tools.
- **FX rate should be applied consistently** — fetch a daily rate and use it for all conversions in a scan batch. Do not mix stale and fresh FX rates across results.
- **Show FX rate used** (e.g. "1 USD = 1.54 AUD at scan time") in the price breakdown for transparency. Prices can look different day-to-day due to exchange rate alone.

### Shipping cost estimation

- **AU buyers pay dramatically different shipping than US/UK buyers.** A record listed at USD $12 from a US seller can land at AUD $35+ after international shipping ($15-20 USD) + FX conversion. The tool must model this.
- **Shipping tiers by seller region (estimates are fine):**
  - AU seller: AUD $5–15 domestic flat
  - US seller: AUD $20–35 international (1 LP, standard post)
  - UK/EU seller: AUD $18–30 international
  - Japan seller: AUD $15–25 (Japan Post is often cheapest from Asia)
- **"Ships from AU" filter is high value.** For identical records, an AU seller at $5 more is often cheaper landed than an overseas seller at $5 less.
- **Australian stores (non-Discogs):** Clarity Records, Discrepancy Records, Egg Records, Red Eye Records, JB Hi-Fi, Bandcamp AU artists — these have no shipping from overseas at all and represent the cheapest landed cost when they have stock.

### Import duties and GST

- **No customs duty on vinyl records** for packages under AUD $1,000 imported value. This is the effective threshold (ATO/ABF de minimis). For personal vinyl buying this threshold is almost never exceeded.
- **GST (10%)** may be collected by the overseas seller/platform if they are registered under Australia's low-value goods GST regime (applies to most major online platforms). Bandcamp, for example, adds GST at checkout for AU buyers. Discogs does not collect GST on behalf of sellers; this is an inconsistency the tool cannot easily resolve.
- **Practical recommendation:** Don't model duty/GST in landed cost calculations — it's inconsistently applied and rarely materialises for individual LP purchases. Keep the landed cost model as: list price + shipping estimate + FX conversion. Flag this as an approximation.

### Local store proximity

- Out of scope for a personal tool (no geolocation needed), but the store coverage list matters. Discrepancy Records (Melbourne/online) is AU's largest online vinyl store with 800,000+ LPs and free domestic delivery — this is a high-value scraping target.
- Clarity Records (Adelaide, online) and Red Eye Records (Sydney, online) are smaller but meaningful for indie/specialist titles.
- Priority AU stores for scraping: Discrepancy Records, Red Eye Records, Clarity Records (if Shopify-based).

### Australian pressing vs import

- AU pressings of local artists often exist and are priced in AUD on local sites; these are undervalued by global price guides (Discogs median is skewed toward US/EU buyers).
- For international releases, AU pressings (labeled "Australia") often command a slight premium or discount vs US pressing depending on the record — this is collector knowledge, not something the tool needs to model explicitly.
- The app should surface pressing/country information from Discogs result metadata where available, even without acting on it — collectors will use it to decide.

---

## Sources

- [Discogs Wantlist Feature Overview](https://www.discogs.com/about/features/wantlist/)
- [How Wantlist Works — Discogs Support](https://support.discogs.com/hc/en-us/articles/360007331594-How-Does-The-Wantlist-Feature-Work)
- [Discogs Acquires Wantlister — Billboard](https://www.billboard.com/pro/discogs-wantlister-stoat-labs-wantlist-upgrades/)
- [Wantlister Feature Announcement — Discogs](https://www.discogs.com/about/updates/wantlist-improvements-coming-soon-with-wantlister/)
- [Discdogs FAQ — Real-time Discogs notifications](https://discdogs.app/faq)
- [Discogs Forum — Feature requests thread](https://www.discogs.com/forum/thread/702926)
- [Discogs Forum — Maximum price for notifications](https://www.discogs.com/forum/thread/396008)
- [Discogs App UX Update 2024](https://www.discogs.com/about/updates/app-experience-update-2024/)
- [Why Are Vinyl Records So Expensive in Australia — Bondi Records](https://bondirecords.com/blogs/news/why-are-vinyl-records-so-expensive-the-true-cost-of-running-a-record-store-in-australia)
- [Australia Import Tax Guide — Instarem](https://www.instarem.com/blog/import-tax-australia/)
- [GST on Low Value Imported Goods — ATO](https://www.ato.gov.au/businesses-and-organisations/international-tax-for-business/gst-for-non-resident-businesses/gst-on-low-value-imported-goods)
- [Discrepancy Records — Australia's largest online vinyl store](https://www.discrepancy-records.com.au/)
- [Where to Shop for Vinyl Records — CHOICE AU](https://www.choice.com.au/electronics-and-technology/home-entertainment/home-audio/articles/where-to-shop-for-vinyl-records)
- [Spotify UX Analysis — UX Collective](https://uxdesign.cc/ux-ui-analysis-spotify-31f3855a1740)
- [RateYourMusic vs Discogs Usability — Discogs Forum](https://www.discogs.com/forum/thread/164421)
- [Design Critique: RateYourMusic — IXD Pratt](https://ixd.prattsi.org/2024/01/design-critique-rateyourmusic-com-desktop-version/)
- [Best Apps to Catalog Vinyl — The Rings of Vinyl](https://theringsofvinyl.com/best-apps-to-catalog-your-vinyl-collection/)
