---
name: scan-tastings
description: Collect upcoming wine tastings from the watched sources (Wally's, The Wine House, K&L Culver City, Stanley's, Learn About Wine), filter them, analyze lineups, and score them. Use when asked what tastings are coming up, or as the first step of the weekly digest.
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
   - **title**: a short display title, 24 characters or fewer, so it fits on one line next to the logo on a phone: `Querciabella: 3 Villages`, `Failla: Four Pinot Sites`, `Champagne Tent`. Lead with the producer or theme; drop words like "Tasting", "Event", "K&L", the host's name, and dates. The shop's full title can go in `notes`.
   - **time** and **price**: only what the source states (leave `time` out if it isn't published; never write "evening"). Keep them short, like `4–5pm` and `$25` or `$120–150`, so the line under the title fits on a phone. Details like "multiple slots" go in `notes`; a second session ("also Sun 3pm") goes in the verdict and as a second link.
   - **format**: a short label, e.g. `Terroir comparison`, `Vertical`, `Producer deep dive`, `Winemaker-hosted`, `Blind`, `Walk-around`, `Food pairing`, `Theme night`.
   - **lineup**: one object per wine, as listed: `{"wine": "2023 Tenuta di Trinoro Campo di Tenaglia Toscana Rosso IGT", "price": "$160", "scores": ["WA 98", "V 96", "JS 96"]}`. Keep critic scores exactly as the source lists them (their `98WA` becomes `WA 98`) and drop the `scores` field when there are none. Use only what the source shows. If nothing is published, `[]`, and say "lineup not published" in the verdict.
   - **grape** / **region**: set `grape` only when every wine in the lineup is the same variety (`Sangiovese`, `Pinot Noir`), and `region` only when every wine comes from one region, using the most specific region they all share (`Southern Rhône`, not `France`; `Tuscany` if one wine is IGT Toscana). A blend counts as its own thing, not as its main grape. Without a published lineup, set one only if the event itself guarantees it (a Champagne tent, a Burgundy night). Otherwise leave them out; never guess.
   - **highlights**: 2–3 short names of the most interesting wines in the lineup (used on sneak-peek cards). Skip when the lineup is empty.
   - **value**: when retail prices are listed, give the range and the headline access (e.g. "8 wines, $44–160 retail; both Campo single-vineyards at $160 each, for a $35 ticket"). Without prices, only mention value if something is obviously rare or allocated. Never make up prices.
   - **verdict**: 2–3 sentences for a WSET 3 reader. Wrap 2–4 key phrases in `**double asterisks**` so they render bold: the comparison, the standout bottle or producer, and any catch (e.g. `**lineup isn't published**`). Never bold whole sentences. What will you learn by tasting these side by side? What's special about the producer or place? Include any catch (the drive, a generic lineup, a sales-pitch vibe).
   - **score**: apply the Pour score rules in `preferences.md`.
   - Look up producer background with web search when you don't know it well. Don't state scores or awards from memory.
6. **Write** `<run_dir>/scored.json`:
   ```json
   {"events": [{"id": "wallys:2026-10-09:querciabella-tasting", "source": "wallys", "title": "...", "date": "2026-10-09",
                "time": "5pm", "venue": "Wally's Beverly Hills", "location": "Beverly Hills", "price": "$75", "format": "Terroir comparison", "region": "Tuscany",
                "lineup": [{"wine": "...", "price": "$110", "scores": ["V 95"]}], "highlights": ["..."],
                "value": "...", "verdict": "...", "score": 9, "badges": ["Book now"],
                "links": [{"label": "Tickets", "url": "..."}], "notes": "anything else"}],
    "classes": [{"title": "...", "source": "winehouse", "date": "...", "price": "...", "verdict": "...", "links": [...]}],
    "source_notes": ["kl: read via search, lineups partial"]}
   ```
   `id` = `<source>:<date>:<slug of title>` and must stay stable week to week (it's how events are recognized as already seen). `source` is the source key from `sources.md` (it picks the logo, so the shop name isn't repeated); `scout-tastings` uses `scout`. `location` is the branch or off-site place shown next to the logo (`Beverly Hills`, `Calamigos Ranch, Malibu`); leave it out for single-location shops like The Wine House.
