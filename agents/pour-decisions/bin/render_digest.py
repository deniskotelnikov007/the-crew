#!/usr/bin/env python3
"""Render digest.json into email-safe HTML and plain text.

Usage: render_digest.py <run_dir>
Reads <run_dir>/digest.json and writes:
  digest.html        preview; logos embedded as data URIs
  digest.email.html  the version to send; logos are inline attachments (cid:logo-<source>)
  digest.txt         plain-text alternative
  inline.json        cid -> file for every inline image the email uses (the logos); the sender attaches them

digest.json (written by the agent, see skills/weekly-digest/SKILL.md):
{
  "subject": "...", "intro": "...",
  "run_date": "YYYY-MM-DD",           # "This week" = Mon-Sun containing run_date; on a Sunday, the coming week
  "events": [Event],                  # any order; the renderer sorts and groups
  "classes": [Event],                 # optional, WSET etc.
  "footnotes": ["..."]
}
Event: {"title", "source" (a LOGOS key picks the logo; "scout" or anything else = no logo), "date" (ISO), "time",
        "venue", "location" (branch or off-site place shown next to the logo; derived from venue if absent), "price", "score" (1-10), "format", "verdict", "value",
        "lineup": [str | {"wine", "price", "scores": ["WA 97", "V 95"]}],
        "highlights": [str],                # 2-3 standout wines for the sneak-peek card
        "grape": str, "region": str,        # only when every wine shares it
        "badges": [str], "links": [{"label", "url"}]}
Only "title" is required. In "verdict" and "value", **double asterisks** mark key words to bold.

Layout: "This week" (Mon-Sun) lists every remaining event by day (full card at score >= 6, one line below).
"Sneak peeks" lists later events scoring >= 6 as short cards; later ones below 6 get one line.
"""
import base64
import datetime as dt
import html
import json
import os
import re
import struct
import sys

WINE = "#6d1a36"
WINE_SOFT = "#c9a3ae"
INK = "#2b2024"
MUTED = "#6b5c62"
PAPER = "#faf6f1"
CARD = "#ffffff"
LINE = "#eadfd6"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT = SANS  # body text: the device's system font reads best on phones
DISPLAY = "Georgia, 'Times New Roman', serif"  # masthead only

LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logos")
LOGOS = {"wallys": "wallys.png", "winehouse": "winehouse.png", "kl": "kl.png",
         "stanleys": "stanleys.png", "learnaboutwine": "learnaboutwine.png"}
BRANDS = {"wallys": "Wally's", "winehouse": "The Wine House", "kl": "K&L",
          "stanleys": "Stanley's Wet Goods", "learnaboutwine": "Learn About Wine"}  # stripped from venue next to a logo

# (label, min score, pill background, pill text, card accent)
TIERS = [("Must", 8, WINE, "#fff", WINE), ("Worth a look", 6, "#f3e7ea", WINE, WINE_SOFT), ("Also on", 0, "#efebe8", MUTED, LINE)]

CRITICS = {"WA": "Wine Advocate", "V": "Vinous", "AG": "Antonio Galloni", "JS": "James Suckling",
           "WS": "Wine Spectator", "WE": "Wine Enthusiast", "JD": "Jeb Dunnuck", "D": "Decanter",
           "BH": "Burghound", "WH": "Wine & Spirits", "JR": "Jancis Robinson", "OB": "Owen Bargreen"}


def e(s):
    return html.escape(str(s or ""))


def rich(s):
    """Escape, then turn **key words** into bold."""
    return re.sub(r"\*\*(.+?)\*\*", rf'<b style="font-weight:700;color:{INK}">\1</b>', e(s))


def plain(s):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", str(s or ""))


def tier(ev):
    s = ev.get("score")
    s = 0 if s is None else s
    return next(t for t in TIERS if s >= t[1])


def day(iso):
    try:
        return dt.date.fromisoformat(iso)
    except (TypeError, ValueError):
        return None


def nice_date(iso, long=False):
    d = day(iso)
    if not d:
        return iso or ""
    return d.strftime("%A, %B %-d" if long else "%a %b %-d")


def logo_img(source, mode, box_w, box_h):
    """Logo tile scaled to fit a box. Tiles in assets/logos/ share one 128x88 shape, so every card lines up."""
    if source == "scout":  # found by the scout, not a watched shop: a neutral tile, same footprint
        return (f'<div style="width:{box_w - 2}px;height:{box_h - 2}px;border:1px solid {LINE};border-radius:6px;background:#f4eee7;'
                f'text-align:center;line-height:{box_h - 2}px;font-size:{round(box_h * 0.45)}px">🔭</div>')
    if source not in LOGOS:
        return ""
    with open(os.path.join(LOGO_DIR, LOGOS[source]), "rb") as f:
        data = f.read()
    w, h = struct.unpack(">II", data[16:24])  # PNG IHDR
    k = min(box_w / w, box_h / h)
    w, h = round(w * k), round(h * k)
    if mode == "email":  # Gmail strips data: URIs, so the sender attaches logos inline
        src = f"cid:logo-{source}"
    else:  # self-contained preview
        src = "data:image/png;base64," + base64.b64encode(data).decode()
    return (f'<img src="{e(src)}" width="{w}" height="{h}" alt="{e(BRANDS.get(source, source))}" '
            f'style="width:{w}px;height:{h}px;border:1px solid {LINE};border-radius:6px;display:block">')


def location(ev):
    """Where it is. Next to a logo, only the branch: "Wally's Beverly Hills" -> "Beverly Hills"."""
    if ev.get("location"):
        return ev["location"]
    venue = ev.get("venue") or ""
    brand = BRANDS.get(ev.get("source"))
    if brand and venue.startswith(brand):
        return venue[len(brand):].strip(" ,·-")
    return venue


def pill(text, bg, fg):
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font:600 11px {SANS};'
            f'padding:3px 8px;border-radius:9px;white-space:nowrap">{e(text)}</span>')


def label_pill(ev):
    name, _, bg, fg, _ = tier(ev)
    score = f" · {ev['score']}/10" if ev.get("score") is not None else ""
    return pill(name + score, bg, fg)


def chips(ev):
    """Tag row. Wine color is saved for what calls for a decision: the rating and "Book now".
    Format is a neutral fill (what the tasting is); other badges are gray outlines (context)."""
    base = f"display:inline-block;font:600 11px {SANS};border-radius:9px;margin:0 4px 4px 0;white-space:nowrap"
    badges = ev.get("badges") or []
    urgent = [b for b in badges if b.lower().startswith("book now")]
    quiet = [b for b in badges if b not in urgent]
    out = [f'<span style="display:inline-block;margin:0 4px 4px 0">{label_pill(ev)}</span>']
    out += [f'<span style="{base};border:1px solid {WINE};color:{WINE};padding:2px 7px">{e(b)}</span>' for b in urgent]
    title_words = set(re.findall(r"\w{4,}", (ev.get("title") or "").lower()))
    # Region/grape only when the title doesn't already name it: "Champagne Tent" needs no 📍 Champagne,
    # "Pinot Taste Off" no 🍇 Pinot Noir.
    extra = [f"{icon} {ev[k]}" for k, icon in [("region", "📍"), ("grape", "🍇")]
             if ev.get(k) and not set(re.findall(r"\w{4,}", ev[k].lower())) & title_words]
    for text in [ev.get("format"), *extra]:
        if text:
            out.append(f'<span style="{base};background:#efe9e3;color:{INK};padding:3px 8px">{e(text)}</span>')
    out += [f'<span style="{base};border:1px solid #d3cac5;color:{MUTED};padding:2px 7px">{e(b)}</span>' for b in quiet]
    return f'<div style="margin:14px 0 0">{"".join(out)}</div>'


def links(ev):
    return " &nbsp;·&nbsp; ".join(
        f'<a href="{e(l.get("url"))}" style="color:{WINE};font:600 13px {SANS}">{e(l.get("label") or "Link")} →</a>'
        for l in ev.get("links") or [] if l.get("url"))


def when_parts(ev, with_date=True, with_time=True):
    parts = [nice_date(ev.get("date")) if with_date else None, ev.get("time") if with_time else None, ev.get("price"), location(ev)]
    return [p for p in parts if p]


def when(ev, with_date=True, with_time=True):
    return " · ".join(when_parts(ev, with_date, with_time))


def when_html(ev, with_date=True, with_time=True):
    """Each piece stays whole ("Culver City" never splits); a narrow phone breaks only between pieces."""
    return " · ".join(e(p).replace(" ", "&nbsp;") for p in when_parts(ev, with_date, with_time))


def wine_row(w):
    if isinstance(w, str):
        w = {"wine": w}
    scores = "".join(
        f'<span style="display:inline-block;background:#f6efe6;color:{INK};font:600 10px {SANS};padding:2px 5px;'
        f'border-radius:4px;margin:0 3px 2px 0;white-space:nowrap">{e(s)}</span>' for s in w.get("scores") or [])
    return (f'<tr><td style="padding:4px 0;border-bottom:1px solid {LINE};font:14px/1.4 {FONT};color:{INK}">{e(w.get("wine"))}'
            f'{"<div>" + scores + "</div>" if scores else ""}</td>'
            f'<td align="right" valign="middle" style="padding:4px 0 4px 10px;border-bottom:1px solid {LINE};font:13px {SANS};color:{MUTED};white-space:nowrap">{e(w.get("price"))}</td></tr>')


def card_head(ev, mode, size, with_date, box=(64, 44), with_time=True):
    """Logo | title over subtitle. The label pill lives in the chips row, so titles get the full width."""
    logo = logo_img(ev.get("source"), mode, *box)
    logo_td = f'<td valign="middle" width="{box[0]}" style="width:{box[0]}px;padding:0 12px 0 0">{logo}</td>' if logo else ""
    return f"""
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    {logo_td}
    <td valign="middle">
      <div style="font:700 {size}px/1.25 {FONT};color:{INK}">{e(ev.get("title"))}</div>
      <div style="font:13px/1.4 {SANS};color:{MUTED};margin-top:2px">{when_html(ev, with_date, with_time)}</div>
    </td>
  </tr></table>"""


def full_card(ev, mode, with_date=False):
    accent = tier(ev)[4]
    lineup = ""
    if ev.get("lineup"):
        n = len(ev["lineup"])
        # <details> collapses in Apple Mail and browsers; Gmail drops the tags and shows it open.
        lineup = (f'<details style="margin:18px 0 0"><summary style="cursor:pointer;font:600 11px {SANS};letter-spacing:.08em;'
                  f'text-transform:uppercase;color:{MUTED};padding:2px 0">In the glass · {n} wine{"s" if n != 1 else ""}</summary>'
                  f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:4px">'
                  f'{"".join(wine_row(w) for w in ev["lineup"])}</table></details>')
    value = (f'<p style="margin:14px 0 0;font:13px/1.55 {SANS};color:{MUTED}"><b style="color:{INK}">Value:</b> {rich(ev["value"])}</p>'
             if ev.get("value") else "")
    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border:1px solid {LINE};border-left:4px solid {accent};border-radius:10px;margin:0 0 18px">
<tr><td style="padding:20px 20px 22px">
  {card_head(ev, mode, 17, with_date, box=(56, 38))}
  {chips(ev)}
  <p style="margin:12px 0 0;font:16px/1.6 {FONT};color:{INK}">{rich(ev.get("verdict"))}</p>
  {lineup}
  {value}
  <div style="margin-top:18px">{links(ev)}</div>
</td></tr></table>"""


def peek_card(ev, mode):
    accent = tier(ev)[4]
    wines = [w if isinstance(w, str) else w.get("wine", "") for w in ev.get("lineup") or []]
    shown = ev.get("highlights") or wines[:3]
    glass = ""
    if shown:
        more = f" +{len(wines) - len(shown)} more" if len(wines) > len(shown) else ""
        glass = f'<div style="font:13px/1.5 {SANS};color:{MUTED};margin-top:10px"><b style="color:{INK}">In the glass:</b> {e("; ".join(shown))}{e(more)}</div>'
    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border:1px solid {LINE};border-left:4px solid {accent};border-radius:10px;margin:0 0 14px">
<tr><td style="padding:18px 18px 20px">
  {card_head(ev, mode, 17, True, box=(48, 33))}
  {chips(ev)}
  <p style="margin:10px 0 0;font:15px/1.55 {FONT};color:{INK}">{rich(ev.get("verdict"))}</p>
  {glass}
  <div style="margin-top:14px">{links(ev)}</div>
</td></tr></table>"""


def line_row(ev, mode, with_date=False):
    """Logo | one-line title over one-line details. table-layout:fixed lets long lines end in "…"."""
    link = next((l.get("url") for l in ev.get("links") or [] if l.get("url")), None)
    title = (f'<a href="{e(link)}" style="color:{INK};text-decoration:none">{e(ev.get("title"))}</a>'
             if link else e(ev.get("title")))
    meta = e(when(ev, with_date)) + (f' — {e(plain(ev["verdict"]))}' if ev.get("verdict") else "")
    clip = "white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;margin:0 0 12px"><tr>
  <td width="56" valign="middle" style="width:56px;padding:0 12px 0 0">{logo_img(ev.get("source"), mode, 55, 38)}</td>
  <td valign="middle">
    <div style="font:600 15px/1.3 {FONT};color:{INK};{clip}">{title}</div>
    <div style="font:12px/1.4 {SANS};color:{MUTED};margin-top:2px;{clip}">{meta}</div>
  </td>
</tr></table>"""


def h2(text, sub=None, note=None):
    sub_html = f'<span style="font-weight:400;color:{MUTED};letter-spacing:.02em;text-transform:none"> &nbsp;|&nbsp; {e(sub)}</span>' if sub else ""
    note_html = f'<div style="font:13px {SANS};color:{MUTED};margin:2px 0 0">{e(note)}</div>' if note else ""
    return (f'<h2 style="margin:30px 0 12px;font:700 13px {SANS};letter-spacing:.12em;text-transform:uppercase;color:{WINE}">'
            f'{e(text)}{sub_html}{note_html}</h2>')


def split(d):
    run = day(d.get("run_date")) or dt.date.today()
    # The digest goes out Sunday night, so a Sunday run covers the coming week. Any other day
    # (manual runs, or Monday in UTC on GitHub) covers the current week: same result either way.
    start = run - dt.timedelta(days=run.weekday()) + dt.timedelta(days=7 if run.weekday() == 6 else 0)
    end = start + dt.timedelta(days=6)
    evs = sorted(d.get("events") or [], key=lambda x: (x.get("date") or "9999", -(x.get("score") or 0)))
    evs = [x for x in evs if not day(x.get("date")) or day(x["date"]) >= run]  # earlier days are over
    this_week = [x for x in evs if day(x.get("date")) and day(x["date"]) <= end]
    later = [x for x in evs if x not in this_week]
    return start, end, this_week, later


def critic_legend(d):
    used = set()
    for ev in d.get("events") or []:
        for w in ev.get("lineup") or []:
            for s in (w.get("scores") if isinstance(w, dict) else None) or []:
                used.add(s.split()[0])
    known = [f"{k} {CRITICS[k]}" for k in sorted(used) if k in CRITICS]
    return "Critic scores as listed by the shop: " + " · ".join(known) + "." if known else None


def render_html(d, mode):
    start, end, this_week, later = split(d)
    body = []

    body.append(h2("This week", f"{start.strftime('%a, %b %-d')} – {end.strftime('%a, %b %-d')}"))
    if not this_week:
        body.append(f'<p style="font:15px/1.5 {FONT};color:{MUTED}">Nothing worth the drive this week. See the sneak peeks.</p>')
    current = None
    for ev in this_week:
        if ev["date"] != current:
            current = ev["date"]
            body.append(f'<div style="font:600 15px {FONT};color:{INK};margin:18px 0 8px;padding-bottom:4px;border-bottom:1px solid {LINE}">{e(nice_date(current, long=True))}</div>')
        body.append(full_card(ev, mode) if (ev.get("score") or 0) >= 6 else line_row(ev, mode))

    peeks = [x for x in later if (x.get("score") or 0) >= 6]
    minor = [x for x in later if (x.get("score") or 0) < 6]
    if peeks or minor:
        body.append(h2("Sneak peeks", f"from {(end + dt.timedelta(days=1)).strftime('%a, %b %-d')}"))
        body += [peek_card(x, mode) for x in peeks]
        body += [line_row(x, mode, with_date=True) for x in minor]

    if d.get("classes"):
        body.append(h2("Classes"))
        body += [line_row(x, mode, with_date=True) for x in d["classes"]]

    notes = list(d.get("footnotes") or [])
    legend = critic_legend(d)
    if legend:
        notes.append(legend)
    if notes:
        body.append(f'<ul style="margin:26px 0 0;padding-left:18px;font:12px/1.5 {SANS};color:{MUTED}">'
                    + "".join(f'<li style="margin:0 0 4px">{e(n)}</li>' for n in notes) + "</ul>")

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d.get("subject") or "Pour Decisions")}</title></head>
<body style="margin:0;padding:0;background:{PAPER}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPER}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px">
<tr><td style="background:{WINE};border-radius:12px 12px 0 0;padding:26px 24px 22px">
  <div style="font:600 30px/1.1 {DISPLAY};color:#fff">Pour Decisions</div>
  <div style="font:13px {SANS};color:#f0d9e0;margin-top:6px">Tastings worth your evening · week of {e(start.strftime('%b %-d'))}</div>
</td></tr>
<tr><td style="padding:22px 4px 8px">
  <p style="margin:0;font:16px/1.6 {FONT};color:{INK}">{rich(d.get("intro"))}</p>
  {"".join(body)}
  <p style="margin:28px 0 8px;font:12px {SANS};color:{MUTED};text-align:center">Sent by pour-decisions, a member of the crew. Spit responsibly.</p>
</td></tr>
</table></td></tr></table>
</body></html>
"""


def text_event(ev, with_lineup):
    name = tier(ev)[0].upper()
    score = f" {ev['score']}/10" if ev.get("score") is not None else ""
    out = [f"* [{name}{score}] {ev.get('title')}", f"  {' · '.join(p for p in [when(ev), ev.get('venue')] if p)}"]
    if ev.get("verdict"):
        out.append(f"  {plain(ev['verdict'])}")
    if with_lineup:
        for w in ev.get("lineup") or []:
            if isinstance(w, dict):
                extra = " ".join(x for x in [", ".join(w.get("scores") or []), w.get("price")] if x)
                out.append(f"    - {w.get('wine')}" + (f" ({extra})" if extra else ""))
            else:
                out.append(f"    - {w}")
        if ev.get("value"):
            out.append(f"  Value: {plain(ev['value'])}")
    out += [f"  {l.get('label') or 'Link'}: {l.get('url')}" for l in ev.get("links") or []]
    return out + [""]


def render_text(d):
    start, end, this_week, later = split(d)
    out = [d.get("subject") or "Pour Decisions", "", plain(d.get("intro")), "",
           f"THIS WEEK ({start:%b %-d} – {end:%b %-d})", "-" * 40]
    for ev in this_week:
        out += text_event(ev, (ev.get("score") or 0) >= 6)
    if later:
        out += ["SNEAK PEEKS", "-" * 40]
        for ev in later:
            out += text_event(ev, False)
    if d.get("classes"):
        out += ["CLASSES", "-" * 40]
        for ev in d["classes"]:
            out += text_event(ev, False)
    notes = list(d.get("footnotes") or [])
    if critic_legend(d):
        notes.append(critic_legend(d))
    out += [f"note: {n}" for n in notes]
    return "\n".join(out) + "\n"


def main():
    run_dir = sys.argv[1]
    with open(f"{run_dir}/digest.json") as f:
        d = json.load(f)
    for name, mode in [("digest.html", "preview"), ("digest.email.html", "email")]:
        with open(f"{run_dir}/{name}", "w") as f:
            f.write(render_html(d, mode))
    with open(f"{run_dir}/digest.txt", "w") as f:
        f.write(render_text(d))
    email = open(f"{run_dir}/digest.email.html").read()
    inline = {f"logo-{k}": os.path.normpath(os.path.join(LOGO_DIR, v)) for k, v in LOGOS.items() if f"cid:logo-{k}" in email}
    with open(f"{run_dir}/inline.json", "w") as f:
        json.dump(inline, f, indent=1)
    print(f"wrote digest.html, digest.email.html, digest.txt in {run_dir}")


if __name__ == "__main__":
    main()
