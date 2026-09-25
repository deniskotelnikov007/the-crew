# Sources

Sites checked every week. `bin/fetch_sources.py` reads the ones marked **script**; the rest you read yourself.
Home base for distances: **90025** (West LA). Radius: **15 miles**, plus the exceptions noted below.

| Key | Site | Category | Read by | Locations that count |
|---|---|---|---|---|
| `wallys` | Wally's Wine & Spirits | wine (spirits too) | script | Santa Monica (preferred), Beverly Hills, Malibu, and off-site LA venues. **Never Las Vegas.** |
| `winehouse` | The Wine House | wine (sake, spirits too) | script | 2311 Cotner Ave, West LA (only location) |
| `kl` | K&L Wine Merchants | wine (spirits too) | web search | **Culver City only.** Skip Hollywood, SF, Redwood City. |

## Wally's — `wallys`
- Page: https://www.wallywine.com/events
- Two kinds of listings:
  1. **Feature events** (winemaker dinners, producer tastings) with venue, date, time, price, and ticket links (OpenTable or Tock).
  2. **Wine-bar tasting series** ("The Great Cabernet Showdown", "$35/Guest"). The button label is the location: keep `MALIBU`, drop `LAS VEGAS`. Descriptions are one line; lineups usually aren't published.
- Dates have no year; the script infers it. Stale past events stay on the page; the script drops them.
- Distances from 90025: Santa Monica ~3.5 mi, Beverly Hills ~5 mi, Malibu ~17 mi (allowed anyway), Calamigos Ranch ~22 mi (allowed for special events; mention the drive).

## The Wine House — `winehouse`
- Real listings: https://www.winehouse.com/classes-and-events (tastings are sold as products).
  `https://www.winehouse.com/events` is a separate calendar widget that is usually empty. Ignore it.
- Each product page often includes **"Wines to be poured"** with scores and retail prices, which makes a value calculation possible.
- The listing also includes WSET courses (multi-day, $325–$1,599). They're not tastings; list them in a short "Classes" line at most.
- ~1.5 mi from 90064/90025.

## K&L Wine Merchants — `kl`
- Culver City events are sold on Tock: https://www.exploretock.com/k-and-l-wine-merchants-culver
- **Both klwines.com and Tock block automated fetches (Cloudflare bot check).** Do not try to get around it: no alternate user agents, no headless-browser tricks. Use web search:
  - `site:exploretock.com k-and-l-wine-merchants-culver event`
  - `"K&L" Culver City tasting <month> <year>`
  - Tock event URLs look like `https://www.exploretock.com/k-and-l-wine-merchants-culver/event/<id>/<slug>`. Link to those.
- **Search is a weak fallback.** Tested 2026-09-25: results were mostly stale (2024 events, sold-out past tents) and missed all five current tastings. Always check that a result's date is upcoming, and when you find nothing current, say "K&L: couldn't read this week's events" in the footnotes instead of padding with old ones.
- When running locally with a real browser available, the Tock page renders fine and has full lineups with retail prices.
- Standing schedule: tasting bar Thu 4–6pm, Fri 4–6pm, Sat 3–6pm, with themed tastings (~$20–25) most weeks, a monthly Wine Club tasting (members only, skip), and big tent events (Champagne, Italy) a few times a year.
- 4235 Sepulveda Blvd, Culver City 90230, ~4 mi.
- Upgrade path (later phase): read K&L's event newsletter from a Gmail label.

## Adding a source
Add a row above and a section with: URL, how the page loads (static HTML / embedded JSON / blocked), where the lineup lives, and which locations count. If it can be read with a plain HTTP GET, add a fetcher to `bin/fetch_sources.py`; otherwise use web search.
