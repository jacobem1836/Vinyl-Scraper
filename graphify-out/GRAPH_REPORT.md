# Graph Report - /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper  (2026-04-21)

## Corpus Check
- 30 files · ~69,182 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 188 nodes · 296 edges · 17 communities detected
- Extraction: 68% EXTRACTED · 32% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 23 edges
2. `WishlistItem` - 12 edges
3. `Listing` - 10 edges
4. `scan_item()` - 9 edges
5. `invalidate_dashboard_cache()` - 8 edges
6. `mock_listing()` - 8 edges
7. `item_detail()` - 7 edges
8. `_enrich_item()` - 7 edges
9. `should_notify()` - 7 edges
10. `send_deal_email()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `post_bulk()` --calls--> `get()`  [INFERRED]
  /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/bulk_import.py → /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/services/scan_status.py
- `add_wishlist_item_web()` --calls--> `WishlistItem`  [INFERRED]
  /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/routers/wishlist.py → /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/models.py
- `create_wishlist_item_api()` --calls--> `WishlistItem`  [INFERRED]
  /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/routers/wishlist.py → /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/models.py
- `bulk_create_wishlist_items_api()` --calls--> `WishlistItem`  [INFERRED]
  /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/routers/wishlist.py → /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/models.py
- `scan_item()` --calls--> `Listing`  [INFERRED]
  /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/services/scanner.py → /Users/jacobmarriott/Documents/Personal/projects/Vinyl-Scraper/app/models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (24): Search Bandcamp for physical vinyl listings.      Bandcamp's search does not exp, search_and_get_listings(), _build_listing(), _get_album_listings(), _get_artist_listings(), _get_headers(), _get_label_listings(), _get_release_listings() (+16 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (26): mock_item(), mock_listing(), Shared pytest fixtures for Phase 15 notification tests., Factory fixture returning a function that creates Listing-like objects., Fixture that returns a helper to override app.config.settings attributes., Return a WishlistItem-like object with default notification attributes., settings_override(), Failing unit tests for Phase 15 notification helpers.  These tests describe the (+18 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (19): Base, BaseModel, Base, Safely add new columns to existing databases., run_migrations(), DeclarativeBase, Listing, WishlistItem (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (15): get_cached_dashboard(), set_cached_dashboard(), convert_to_aud(), format_orig_display(), get_rate(), FX rate service — fetches and caches currency conversion rates.  Uses exchangera, Fetch exchange rate from from_currency to to_currency.      Returns cached rate, Convert amount from currency to AUD using the given rate.      Returns None if r (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (18): _html_to_plaintext(), Tests for email rendering and plain-text fallback in app/services/notifier.py., Render deal_alert.html with the given data (defaults to SAMPLE_DATA)., Tags are removed; text content is preserved., Table rows produce line-separated output; cell content is preserved with separat, Template renders without raising a Jinja2 exception., Rendered HTML uses inline hex colors, not CSS custom properties., Item name, best landed price, and listing title appear in rendered output. (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (12): invalidate_dashboard_cache(), add_wishlist_item_web(), create_wishlist_item_api(), delete_wishlist_item_api(), delete_wishlist_item_web(), edit_wishlist_item_web(), _enrich_item(), _landed() (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.19
Nodes (10): get_enabled_adapters(), ListingDict, finish(), item_finished(), item_started(), reset(), scan_all_items(), scan_item() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (7): load_env_api_key(), main(), parse_line(), post_bulk(), Try to read API_KEY from .env file., Parse 'album: Dark Side of the Moon' -> {"type": "album", "query": "Dark Side of, POST all items to /api/wishlist/bulk in one request. Returns count added.

### Community 8 - "Community 8"
Cohesion: 0.54
Nodes (6): compute_typical_price(), _landed(), send_deal_email(), should_notify(), scan_all_items_web(), scan_single_item_web()

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 0.6
Nodes (4): closeDropdown(), getEls(), renderResults(), updateActiveRow()

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): _get_token(), search_and_get_listings()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **37 isolated node(s):** `Try to read API_KEY from .env file.`, `Parse 'album: Dark Side of the Moon' -> {"type": "album", "query": "Dark Side of`, `POST all items to /api/wishlist/bulk in one request. Returns count added.`, `Safely add new columns to existing databases.`, `Search Bandcamp for physical vinyl listings.      Bandcamp's search does not exp` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get()` connect `Community 0` to `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 12`?**
  _High betweenness centrality (0.282) - this node is a cross-community bridge._
- **Why does `_html_to_plaintext()` connect `Community 4` to `Community 8`, `Community 2`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `scan_item()` connect `Community 6` to `Community 8`, `Community 0`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `get()` (e.g. with `post_bulk()` and `item_detail()`) actually correct?**
  _`get()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `WishlistItem` (e.g. with `Base` and `Compute landed cost. If fx_rates provided, converts to AUD.`) actually correct?**
  _`WishlistItem` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Listing` (e.g. with `Base` and `Compute landed cost. If fx_rates provided, converts to AUD.`) actually correct?**
  _`Listing` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `scan_item()` (e.g. with `_scan_in_background()` and `scan_single_item_web()`) actually correct?**
  _`scan_item()` has 8 INFERRED edges - model-reasoned connections that need verification._