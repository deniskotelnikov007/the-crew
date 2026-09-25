---
name: scan-tastings
description: Collect upcoming wine tastings from the watched shops (Wally's, The Wine House, K&L Culver City), filter them, analyze lineups, and score them. Use when asked what tastings are coming up, or as the first step of the weekly digest.
---

# Scan tastings

Output: `<run_dir>/scored.json`, where `<run_dir>` is `agents/pour-decisions/workspace/runs/<today YYYY-MM-DD>/`.

1. **Read** `agents/pour-decisions/knowledge/sources.md` and `agents/pour-decisions/knowledge/preferences.md`.
2. **Fetch the script sources:**
   ```bash
   mkdir -p <run_dir> && python3 agents/pour-decisions/bin/fetch_sources.py <run_dir>
   ```
   This writes `events.json` and `fetch-report.md`. If a source shows `FAILED`, try its page once with WebFetch; if that fails too, carry on and note it for the digest footnotes.
3. **K&L Culver City by web search**, following `sources.md`. Run 2–3 searches, collect each upcoming Culver City event (title, date, time, price, Tock URL, whatever lineup is visible), and add them to your working list with `"source": "kl"`. Never guess a date or price; leave out what you can't find.
4. **Filter** by `preferences.md`: past events, wrong locations (Las Vegas, other K&L stores), members-only, and categories that are off (spirits, beer, sake-only). WSET courses go to a separate `classes` list. Merge duplicates (the same producer event can appear at two shops; keep both but mention it).
5. **Analyze each remaining event**:
   - **format**: a short label, e.g. `Terroir comparison`, `Vertical`, `Producer deep dive`, `Winemaker-hosted`, `Blind`, `Walk-around`, `Food pairing`, `Theme night`.
   - **lineup**: the wines as listed (vintage, producer, cuvée). Use only what the source shows. If nothing is published, `[]`, and say "lineup not published" in the verdict.
   - **value**: when retail prices are listed, give the range and the headline access (e.g. "8 wines, $44–160 retail; both Campo single-vineyards at $160 each, for a $35 ticket"). Without prices, only mention value if something is obviously rare or allocated. Never make up prices.
   - **verdict**: 2–3 sentences for a WSET 3 reader. What will you learn by tasting these side by side? What's special about the producer or place? Include any catch (the drive, a generic lineup, a sales-pitch vibe).
   - **score**: apply the Pour score rules in `preferences.md`.
   - Look up producer background with web search when you don't know it well. Don't state scores or awards from memory.
6. **Write** `<run_dir>/scored.json`:
   ```json
   {"events": [{"id": "wallys:2026-10-09:querciabella-tasting", "source": "wallys", "title": "...", "date": "2026-10-09",
                "time": "5pm", "venue": "Wally's Beverly Hills", "price": "$75", "format": "Terroir comparison",
                "lineup": ["..."], "value": "...", "verdict": "...", "score": 9,
                "links": [{"label": "Tickets", "url": "..."}], "notes": "anything else"}],
    "classes": [{"title": "...", "date": "...", "price": "...", "url": "..."}],
    "source_notes": ["kl: read via search, lineups partial"]}
   ```
   `id` = `<source>:<date>:<slug of title>` and must stay stable week to week (it's how events are recognized as already seen).
