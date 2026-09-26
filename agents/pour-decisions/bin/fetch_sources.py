#!/usr/bin/env python3
"""Fetch upcoming tastings from the sites that can be read without a browser.

Usage: fetch_sources.py <out_dir>

Writes <out_dir>/events.json (a list of raw events) and <out_dir>/fetch-report.md.
Standard library only, so it runs anywhere (laptop or GitHub Actions).
K&L is not here: klwines.com and Tock sit behind a Cloudflare bot check, so the
agent reads K&L through web search instead (see knowledge/sources.md).
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
TODAY = dt.date.today()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def html_to_text(fragment):
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", "", fragment, flags=re.S)
    fragment = re.sub(r"</(p|div|li|h\d)>|<br\s*/?>", "\n", fragment)
    text = html.unescape(re.sub(r"<[^>]+>", "", fragment))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def guess_date(text):
    """'Friday, October 9' or 'Sunday, Nov 1, 2026' -> ISO date.

    Without a year, pick the year whose weekday matches (sites leave stale events up),
    else the year that puts the date closest to today.
    """
    m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b(?:,?\s*(\d{4}))?", text, re.I)
    if not m:
        return None
    month = MONTHS.index(m.group(1)[:3].lower()) + 1
    day = int(m.group(2))
    if m.group(3):
        return dt.date(int(m.group(3)), month, day).isoformat()
    candidates = []
    for y in (TODAY.year - 1, TODAY.year, TODAY.year + 1):
        try:
            candidates.append(dt.date(y, month, day))
        except ValueError:
            pass
    wd = re.search(r"\b(" + "|".join(WEEKDAYS) + r")\b", text, re.I)
    if wd:
        matching = [d for d in candidates if d.weekday() == WEEKDAYS.index(wd.group(1).lower())]
        candidates = matching or candidates
    return min(candidates, key=lambda d: abs((d - TODAY).days)).isoformat()


# --- Wally's -----------------------------------------------------------------
# Shopify Hydrogen (React Router). Page data is embedded as a turbo-stream:
# a flat JSON array where {"_<keyIdx>": <valueIdx>} objects point into the array.

def _decode_turbo_stream(flat):
    sys.setrecursionlimit(100000)
    memo = {}

    def h(i):
        if i < 0:
            return None
        if i in memo:
            return memo[i]
        v = flat[i]
        if isinstance(v, dict):
            o = memo[i] = {}
            for k, vi in v.items():
                o[flat[int(k[1:])]] = h(vi)
            return o
        if isinstance(v, list):
            if v and isinstance(v[0], str) and len(v[0]) == 1:  # tagged value (promise, date...)
                memo[i] = v
                return v
            o = memo[i] = []
            o.extend(h(x) for x in v)
            return o
        return v

    return h(0)


def _portable_text(blocks):
    lines = []
    for b in blocks or []:
        lines.append("".join(c.get("text", "") for c in b.get("children") or []))
    return [l.strip() for l in lines if l.strip()]


def fetch_wallys():
    url = "https://www.wallywine.com/events"
    page = get(url)
    chunk = re.search(r'streamController\.enqueue\("((?:[^"\\]|\\.)*)"\)', page).group(1)
    root = _decode_turbo_stream(json.loads(json.loads('"' + chunk + '"')))
    route = next(v for k, v in root["loaderData"].items() if isinstance(v, dict) and "page" in v)
    events = []

    def add(ev, venue, when):
        text = _portable_text(ev.get("content"))
        buttons = ev.get("buttons") or []
        events.append({
            "source": "wallys",
            "title": text[0] if text else (ev.get("title") or "?"),
            "description": "\n".join(text[1:]),
            "venue": venue,
            "when": when,
            "date": guess_date(when),
            "tickets": [{"label": b.get("label"), "url": b.get("externalLink")} for b in buttons if b.get("externalLink")],
            "page": url,
        })

    for s in route["page"]["data"]["sections"]:
        if s.get("_type") == "eventSection":
            ev = s["event"]
            add(ev, (ev.get("leftSide") or "").strip(), (ev.get("rightSide") or "").strip())
        elif s.get("_type") == "eventCollectionSection":
            # Wine-bar tasting series. The button label is the location (e.g. MALIBU, LAS VEGAS).
            for ev in s.get("eventCollection") or []:
                labels = [b.get("label") for b in ev.get("buttons") or [] if b.get("label")]
                add(ev, "Wally's " + " / ".join(labels).title(), (ev.get("timings") or "").strip())
    return events


# --- The Wine House ----------------------------------------------------------
# Santé storefront (Next.js). Tastings are sold as products in "Classes and Events";
# the listing is server-rendered, and each product page carries the full description
# (often including "Wines to be poured" with retail prices).

def fetch_winehouse():
    base = "https://www.winehouse.com"
    listing = get(base + "/classes-and-events")
    links = list(dict.fromkeys(re.findall(r'href="(/product/[^"]+)"', listing)))
    events = []
    for path in links:
        page = get(base + path)
        ld = re.search(r'<script type="application/ld\+json">(\{"@context":"https://schema.org","@type":"Product".*?)</script>', page)
        product = json.loads(ld.group(1)) if ld else {}
        title = product.get("name") or path
        text = html_to_text(page)
        desc = ""
        if "\nDescription\n" in text:
            desc = text.split("\nDescription\n", 1)[1]
            desc = re.split(r"\n(?:You may also like|Related products|Footer)\n", desc)[0]
        offer = product.get("offers") or {}
        events.append({
            "source": "winehouse",
            "title": title,
            "description": desc[:6000],
            "venue": "The Wine House, 2311 Cotner Ave, Los Angeles, CA 90064",
            "when": title,
            "date": guess_date(title),
            "price": offer.get("price"),
            "availability": (offer.get("availability") or "").rsplit("/", 1)[-1],
            "tickets": [{"label": "Buy", "url": base + path}],
            "page": base + path,
        })
    return events


# --- Stanley's Wet Goods ------------------------------------------------------
# Shopify page; each event is an <image-with-text> block (kicker, title, date/time, description,
# "RESERVE" link to a product whose .js endpoint has the price).

def fetch_stanleys():
    base = "https://stanleys.la"
    page = get(base + "/pages/upcoming-events")
    main = re.search(r"<main.*?</main>", page, re.S).group(0)
    events = []
    for block in re.split(r"<image-with-text[^>]*>", main)[1:]:
        block = block.split("</image-with-text>")[0]
        lines = html_to_text(block).splitlines()
        when = next((l for l in lines if guess_date(l) and re.search("|".join(WEEKDAYS), l, re.I)), None)
        if not when:
            continue
        i = lines.index(when)
        title = " · ".join(lines[max(0, i - 2):i])
        time_line = lines[i + 1] if i + 1 < len(lines) and re.search(r"\d(:\d\d)?\s*[AP]M", lines[i + 1], re.I) else ""
        desc = "\n".join(l for l in lines[i + 1:] if l != time_line and not l.upper().startswith("RESERVE"))
        link = re.search(r'href="(https://stanleys\.la/products/[^"?]+)', block)
        price = None
        if link:
            try:
                price = json.loads(get(link.group(1) + ".js"))["price"] / 100
            except Exception:
                pass
        events.append({
            "source": "stanleys",
            "title": title,
            "description": desc[:4000],
            "venue": "Stanley's Wet Goods, 9620 Venice Blvd, Culver City, CA 90232",
            "when": f"{when} {time_line}".strip(),
            "date": guess_date(when),
            "price": price,
            "tickets": [{"label": "Reserve", "url": link.group(1)}] if link else [],
            "page": base + "/pages/upcoming-events",
        })
    return events


# --- Learn About Wine ---------------------------------------------------------
# Shopify store; in-person events are products in one collection, readable as JSON.
# Titles look like "Pinot Taste Off: Pizza Edition | Arts District: Saturday, October 17th at 3PM".
# Trips and interest lists are skipped.

def fetch_learnaboutwine():
    base = "https://learnaboutwine.com"
    data = json.loads(get(base + "/collections/in-person-events/products.json?limit=250"))
    events = []
    for p in data.get("products", []):
        title = p["title"]
        if re.search(r"\btrip\b|interest list|weekend", title, re.I) or "|" not in title:
            continue
        name, where_when = [x.strip() for x in title.split("|", 1)]
        venue, _, when = where_when.partition(":")
        date = guess_date(when)
        if not date:
            continue
        variants = p.get("variants") or []
        events.append({
            "source": "learnaboutwine",
            "title": name,
            "description": html_to_text(p.get("body_html") or "")[:8000],  # lineups come late in long bodies
            "venue": venue.strip(),
            "when": when.strip(),
            "date": date,
            "price": variants[0]["price"] if variants else None,
            "availability": "InStock" if any(v.get("available") for v in variants) else "SoldOut",
            "tickets": [{"label": "Tickets", "url": f"{base}/products/{p['handle']}"}],
            "page": base + "/collections/in-person-events",
        })
    return events


FETCHERS = {"wallys": fetch_wallys, "winehouse": fetch_winehouse, "stanleys": fetch_stanleys, "learnaboutwine": fetch_learnaboutwine}


def main():
    out_dir = sys.argv[1]
    all_events, report = [], [f"# Fetch report {TODAY.isoformat()}", ""]
    for name, fn in FETCHERS.items():
        try:
            evs = fn()
            upcoming = [e for e in evs if not e["date"] or e["date"] >= TODAY.isoformat()]
            all_events += upcoming
            report.append(f"- {name}: ok, {len(upcoming)} upcoming ({len(evs) - len(upcoming)} past dropped)")
        except Exception as e:  # one broken site must not sink the run
            report.append(f"- {name}: FAILED ({type(e).__name__}: {e})")
    report.append("- kl: not fetched here (Cloudflare); read via web search")
    with open(f"{out_dir}/events.json", "w") as f:
        json.dump(all_events, f, indent=1, ensure_ascii=False)
    with open(f"{out_dir}/fetch-report.md", "w") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
