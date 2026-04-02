import asyncio

# Limit concurrent scan requests across all sources.
# Discogs rate limit is 60/min; with 2-3 sources per item, 3 concurrent items stays well under.
scan_semaphore = asyncio.Semaphore(3)
