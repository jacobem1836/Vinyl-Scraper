# Vinyl Scraper

A personal vinyl record price tracker. Add albums, artists, or labels to a wishlist and it automatically scans Australian record stores and Discogs for the best prices, with email alerts when deals are found.

## Features

- **Dashboard** — view all wishlist items, best prices, and listing counts at a glance
- **Multi-source scraping** — searches 6 Australian online stores + Discogs concurrently
- **Landed price** — all prices displayed as landed cost (price + estimated shipping to Australia)
- **Stock status** — out-of-stock listings are flagged and dimmed automatically
- **Email alerts** — get notified when a listing drops below a configurable % threshold
- **Background scanning** — automatically re-scans all items on a configurable interval
- **iOS Shortcut API** — JSON API with key auth for adding items from your phone
- **Bulk import** — add multiple wishlist items at once from a text file

## Sources

| Store | Type |
|---|---|
| [Discogs](https://www.discogs.com) | Marketplace (worldwide) |
| [The Vinyl Store](https://www.thevinylstore.com.au) | Australian retailer |
| [Dutch Vinyl](https://www.dutchvinyl.com.au) | Australian retailer |
| [Strangeworld Records](https://www.strangeworldrecords.com.au) | Australian retailer |
| [Goldmine Records](https://www.goldminerecords.com.au) | Australian retailer |
| [Utopia Records](https://utopia.com.au) | Australian retailer |
| [uMusic Shop AU](https://shop.umusic.com.au) | Universal Music AU official store |

## Setup

**Requirements:** Python 3.11+

```bash
git clone <repo>
cd crate
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials, then:

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DISCOGS_TOKEN` | Yes | Personal token from [discogs.com/settings/developers](https://www.discogs.com/settings/developers) |
| `API_KEY` | Yes | Any random string — used to authenticate the iOS Shortcut / API |
| `DATABASE_URL` | No | Defaults to `sqlite:///./vinyl.db`. Set to a PostgreSQL URL in production |
| `SMTP_HOST` | No | Email server for deal alerts (defaults to iCloud SMTP) |
| `SMTP_PORT` | No | SMTP port (default `587`) |
| `SMTP_USER` | No | Email login |
| `SMTP_PASSWORD` | No | App-specific password |
| `NOTIFY_EMAIL` | No | Address to receive deal alerts |
| `SCAN_INTERVAL_HOURS` | No | How often to auto-scan (default `6`) |

## Bulk Import

Create a text file with one item per line in the format `type: name`:

```
album: Dark Side of the Moon
artist: Radiohead
label: Sub Pop
subject: jazz piano
```

Then run:

```bash
python bulk_import.py wishlist.txt
```

## API

All API routes require the header `X-API-Key: <your API_KEY>`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/wishlist` | List all items with prices |
| `POST` | `/api/wishlist` | Add an item (triggers immediate scan) |
| `DELETE` | `/api/wishlist/{id}` | Delete an item |
| `GET` | `/api/wishlist/{id}/listings` | All listings for an item |
| `POST` | `/api/scan` | Trigger a full scan of all items |

**POST /api/wishlist body:**
```json
{
  "type": "album",
  "query": "Dark Side of the Moon",
  "notify_below_pct": 20,
  "notify_email": true
}
```

`type` must be one of: `album`, `artist`, `label`, `subject`

## Deploying to Railway

1. Push to GitHub and connect the repo in Railway
2. Add a **PostgreSQL** database service to your project — Railway sets `DATABASE_URL` automatically
3. Set the remaining environment variables in Railway's variable editor
4. Deploy — the app runs migrations on startup, no manual steps needed

The `railway.toml` and `Procfile` are already configured.

