# Sources

Sites checked every week. `bin/fetch_sources.py` reads the ones marked **script**; the rest you read yourself.
Home base for distances: **90025** (West LA). Radius: **15 miles**, plus the exceptions noted below.

| Key | Site | Category | Read by | Locations that count |
|---|---|---|---|---|
| `wallys` | Wally's Wine & Spirits | wine (spirits too) | script | Santa Monica (preferred), Beverly Hills, Malibu, and off-site LA venues. **Never Las Vegas.** |
| `winehouse` | The Wine House | wine (sake, spirits too) | script | 2311 Cotner Ave, West LA (only location) |
| `kl` | K&L Wine Merchants | wine (spirits too) | web search | **Culver City only.** Skip Hollywood, SF, Redwood City. |
| `stanleys` | Stanley's Wet Goods | wine (natural-leaning) | script | Culver City (only location) |
| `learnaboutwine` | Learn About Wine | wine education | script | Arts District (DTLA) classroom and Nick + Sons (Manhattan Beach). **Skip** out-of-area dinners (e.g. Alexander's Steakhouse, Pasadena). |

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

## Stanley's Wet Goods — `stanleys`
- Page: https://stanleys.la/pages/upcoming-events (Shopify). Each event is an image-with-text block; the "Reserve" link is a product whose `.js` endpoint has the price (the script reads it).
- Small wine classes (~6 wines, ~$60) and blind tastings, often built as a style or region ladder. Natural-wine leaning shop, but classes cover classics too.
- 9620 Venice Blvd, Culver City 90232, ~3.5 mi.

## Learn About Wine — `learnaboutwine`
- Wine school run by educator Ian Blackburn. Events are Shopify products: https://learnaboutwine.com/collections/in-person-events/products.json (the script skips trips and interest lists).
- Titles look like `Name | Venue: Weekday, Month Dth at 3PM`. Bodies often list the full lineup with critic scores (e.g. "91 Points — Vinous": write as `V 91`).
- Formats are often comparative or blind (taste-offs, country vs country, region vs region). Some are casual/social ("Wine Friender", "Wine Camp: An Intro to Wine"): score those low.
- Prices rise closer to the date ("Now: $125 | Day Of: $250"): quote the current price and mention the jump. A suspiciously low price (e.g. $50 for a cult Cabernet flight) may be a deposit or partial ticket; say it needs checking rather than calling it a bargain.
- Arts District classroom is ~15 mi from 90025 (allowed; add a `Drive: ~15 mi` badge; `location`: `DTLA`). Nick + Sons, 3307 Highland Ave, Manhattan Beach, ~14 mi (allowed).

## Adding a source
Add a row above and a section with: URL, how the page loads (static HTML / embedded JSON / blocked), where the lineup lives, and which locations count. If it can be read with a plain HTTP GET, add a fetcher to `bin/fetch_sources.py`; otherwise use web search.
Add its logo as `assets/logos/<key>.png`: a 128×88 tile with the logo centered and padded in its own background color (see the existing three) and register it in `LOGOS` in `bin/render_digest.py`.
