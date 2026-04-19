# Phase 1: Infrastructure - Discussion Log

**Session:** 2026-04-02
**Areas discussed:** Scan feedback UX, Registry design, Scheduler parallelism

---

## Scan Feedback UX

**Q: After adding an item, what should the user see while the background scan runs?**
Options: Instant redirect + polling / Instant redirect + manual refresh / Stay on page with scan status
**Selected:** Instant redirect, polling — redirect to dashboard immediately; item card auto-refreshes every few seconds until listings appear

**Q: How should a currently-scanning item look on the dashboard?**
Options: Subtle spinner on card / Just empty listings / You decide
**Selected:** Subtle spinner on the card

---

## Registry Design

**Q: How rich should the adapter registry entries be?**
Options: Simple callable list / Named entries with enabled flag / Full metadata per source
**Selected:** Named entries with enabled flag — user noted the app *might become a paid app*, which influenced the recommendation. Enabled flag allows per-source toggling without code changes.

**Q: Where should the registry live?**
Options: app/services/registry.py / Inside scanner.py
**Selected:** Inside scanner.py

---

## Scheduler Parallelism

**Q: Should Phase 1 parallelize the background scheduled scan?**
Options: Yes — parallelize with semaphore / No — leave sequential
**Selected:** Yes — asyncio.gather() all items, semaphore caps concurrency, APScheduler max_instances=1 prevents overlap

**Q: Keep the 6-hour scan interval, or change it?**
Options: Keep 6 hours / You decide
**Selected:** You decide — Claude picks based on source rate limits

---

*Log generated: 2026-04-02*
