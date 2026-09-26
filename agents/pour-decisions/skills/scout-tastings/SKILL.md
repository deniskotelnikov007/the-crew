---
name: scout-tastings
description: Look beyond the watched shops for wine tastings worth adding to the digest (one-off events, festivals, splurge dinners) and for new venues to watch. Use as part of the weekly digest, or when asked to scout for something interesting.
---

# Scout tastings

Adds to `<run_dir>/scored.json` (see `scan-tastings`) and keeps `memory/scout-log.md` and `memory/candidates.md` current. Run after `scan-tastings`.

1. **Read** `agents/pour-decisions/knowledge/watchlist.md` (what to check and how often, plus dead ends), `memory/scout-log.md` (when each item was last checked), and `memory/candidates.md`.
2. **Due watchlist items:** check every item whose cadence has passed since its last check in `scout-log.md`. Most of these sites block automated access, so use web search and read the results; never try to get around a block.
3. **Open search, every week:** run 3–4 web searches for one-off tastings in the next 8 weeks within the radius in `sources.md`. Rotate angles week to week and note which you used in `scout-log.md`:
   - winemaker or importer dinners at West LA / Santa Monica / Culver City / Beverly Hills restaurants
   - verticals, library or retrospective tastings, blind seminars in Los Angeles
   - producer or regional trade-to-consumer walk-arounds (Rhône Rangers, Grower Champagne, regional boards)
   - new wine bars or shops starting tasting series
   Skip anything already covered by a source in `sources.md` and anything listed under "Dead ends" in `watchlist.md`.
4. **For each real find:** confirm the date is upcoming and the place is in range, then analyze and score it exactly like `scan-tastings` step 5. Keep it only if it scores **6 or more** (the bar is higher for things we don't watch every week). Add it to `scored.json` `events` with `"source": "scout"` (the renderer gives it a 🔭 tile instead of a shop logo, so no extra badge is needed), plus the venue name in `location`. If it's at a watched shop after all, use that shop's key instead.
5. **New venues:** when a venue looks like it runs structured tastings regularly, add it to `memory/candidates.md` (name, URL, what they run, distance, whether a plain fetch works: try `curl -s -o /dev/null -w "%{http_code}"`). Don't add it to `sources.md` yourself; that needs the user's OK. Mention new candidates in the digest footnotes in one line each.
6. **Log** the run in `memory/scout-log.md`: date, watchlist items checked (and what they showed), search angles used, finds kept, and dead ends discovered (also add those to "Dead ends" in `watchlist.md`).
