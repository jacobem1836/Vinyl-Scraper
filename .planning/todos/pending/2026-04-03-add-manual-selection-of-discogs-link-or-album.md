---
created: 2026-04-03T01:50:15.412Z
title: Add manual selection of Discogs link or album
area: ui
files:
  - app/services/discogs.py
  - app/routers/wishlist.py
  - templates/item_detail.html
---

## Problem

When a wishlist item is scraped, the app automatically picks the first Discogs result and uses its artwork/data. There's no way for the user to manually specify which Discogs release a wishlist item corresponds to — if the auto-match is wrong (wrong pressing, wrong year, wrong region), there's no correction path. The artwork shown may be for the wrong release.

## Solution

Allow the user to search Discogs and pick the correct release manually. Options:
- Add a "Link Discogs Release" button on the detail page
- Search field that queries Discogs search API and returns a list of candidates
- User selects the correct one → stores the Discogs release ID on the WishlistItem
- Artwork and listings then pull from that pinned release ID rather than auto-search
