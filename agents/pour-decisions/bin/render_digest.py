#!/usr/bin/env python3
"""Render digest.json into email-safe HTML and plain text.

Usage: render_digest.py <run_dir>
Reads <run_dir>/digest.json, writes <run_dir>/digest.html and <run_dir>/digest.txt.

digest.json shape (written by the agent, see skills/weekly-digest/SKILL.md):
{
  "subject": "...", "week_of": "YYYY-MM-DD", "intro": "...",
  "sections": [{"title": "...", "blurb": "...", "style": "full" | "compact", "events": [Event]}],
  "footnotes": ["..."]
}
Event: {"title", "date" (ISO), "time", "venue", "price", "score" (1-10), "format",
        "verdict", "lineup": [str], "value", "badges": [str], "links": [{"label", "url"}]}
Only "title" is required; everything else is optional.
"""
import datetime as dt
import html
import json
import sys

WINE = "#6d1a36"
INK = "#2b2024"
MUTED = "#7a6a70"
PAPER = "#faf6f1"
CARD = "#ffffff"
LINE = "#eadfd6"
FONT = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def e(s):
    return html.escape(str(s or ""))


def nice_date(iso):
    if not iso:
        return ""
    try:
        return dt.date.fromisoformat(iso).strftime("%a, %b %-d")
    except ValueError:
        return iso


def when_line(ev):
    return " · ".join(x for x in [nice_date(ev.get("date")), ev.get("time"), ev.get("venue"), ev.get("price")] if x)


def score_pill(score):
    if score is None:
        return ""
    return (f'<span style="display:inline-block;background:{WINE};color:#fff;font:600 12px {SANS};'
            f'padding:3px 8px;border-radius:10px;white-space:nowrap">{e(score)}/10</span>')


def badges(ev):
    out = [f'<span style="display:inline-block;border:1px solid {WINE};color:{WINE};font:600 11px {SANS};'
           f'padding:2px 7px;border-radius:9px;margin:0 4px 4px 0">{e(b)}</span>' for b in ev.get("badges") or []]
    if ev.get("format"):
        out.insert(0, f'<span style="display:inline-block;background:#f3e7ea;color:{WINE};font:600 11px {SANS};'
                      f'padding:3px 8px;border-radius:9px;margin:0 4px 4px 0">{e(ev["format"])}</span>')
    return "".join(out)


def links(ev):
    return " &nbsp;·&nbsp; ".join(
        f'<a href="{e(l.get("url"))}" style="color:{WINE};font:600 13px {SANS}">{e(l.get("label") or "Link")} →</a>'
        for l in ev.get("links") or [] if l.get("url"))


def full_card(ev):
    lineup = ""
    if ev.get("lineup"):
        items = "".join(f'<li style="margin:0 0 3px">{e(w)}</li>' for w in ev["lineup"])
        lineup = (f'<div style="font:600 11px {SANS};letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin:14px 0 4px">In the glass</div>'
                  f'<ul style="margin:0;padding-left:18px;font:14px/1.45 {FONT};color:{INK}">{items}</ul>')
    value = (f'<p style="margin:10px 0 0;font:13px/1.5 {SANS};color:{MUTED}"><b style="color:{INK}">Value:</b> {e(ev["value"])}</p>'
             if ev.get("value") else "")
    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border:1px solid {LINE};border-radius:10px;margin:0 0 14px">
<tr><td style="padding:18px 20px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="font:600 19px/1.3 {FONT};color:{INK};padding-right:10px">{e(ev.get("title"))}</td>
    <td align="right" valign="top" width="60">{score_pill(ev.get("score"))}</td>
  </tr></table>
  <div style="font:13px/1.5 {SANS};color:{MUTED};margin:4px 0 10px">{e(when_line(ev))}</div>
  <div>{badges(ev)}</div>
  <p style="margin:8px 0 0;font:15px/1.55 {FONT};color:{INK}">{e(ev.get("verdict"))}</p>
  {lineup}
  {value}
  <div style="margin-top:14px">{links(ev)}</div>
</td></tr></table>"""


def compact_row(ev):
    link = next((l.get("url") for l in ev.get("links") or [] if l.get("url")), None)
    title = f'<a href="{e(link)}" style="color:{INK};text-decoration:none;font-weight:600">{e(ev.get("title"))}</a>' if link else f'<b>{e(ev.get("title"))}</b>'
    note = f' — {e(ev["verdict"])}' if ev.get("verdict") else ""
    return (f'<tr><td style="padding:9px 0;border-bottom:1px solid {LINE};font:14px/1.45 {FONT};color:{INK}">'
            f'{title}{note}<div style="font:12px {SANS};color:{MUTED};margin-top:2px">{e(when_line(ev))}</div></td></tr>')


def render_html(d):
    parts = []
    for s in d.get("sections") or []:
        evs = s.get("events") or []
        if not evs:
            continue
        blurb = f'<p style="margin:0 0 12px;font:14px/1.5 {SANS};color:{MUTED}">{e(s["blurb"])}</p>' if s.get("blurb") else ""
        head = f'<h2 style="margin:28px 0 6px;font:600 13px {SANS};letter-spacing:.12em;text-transform:uppercase;color:{WINE}">{e(s.get("title"))}</h2>'
        if s.get("style") == "compact":
            body = f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{"".join(compact_row(x) for x in evs)}</table>'
        else:
            body = "".join(full_card(x) for x in evs)
        parts.append(head + blurb + body)
    notes = "".join(f'<li style="margin:0 0 4px">{e(n)}</li>' for n in d.get("footnotes") or [])
    notes_html = (f'<ul style="margin:24px 0 0;padding-left:18px;font:12px/1.5 {SANS};color:{MUTED}">{notes}</ul>' if notes else "")
    week = nice_date(d.get("week_of"))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d.get("subject") or "Pour Decisions")}</title></head>
<body style="margin:0;padding:0;background:{PAPER}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPER}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px">
<tr><td style="background:{WINE};border-radius:12px 12px 0 0;padding:26px 24px 22px">
  <div style="font:600 30px/1.1 {FONT};color:#fff">Pour Decisions</div>
  <div style="font:13px {SANS};color:#f0d9e0;margin-top:6px">Tastings worth your evening{(" · week of " + e(week)) if week else ""}</div>
</td></tr>
<tr><td style="padding:22px 4px 8px">
  <p style="margin:0;font:16px/1.6 {FONT};color:{INK}">{e(d.get("intro"))}</p>
  {"".join(parts)}
  {notes_html}
  <p style="margin:28px 0 8px;font:12px {SANS};color:{MUTED};text-align:center">Sent by pour-decisions, a member of the crew. Spit responsibly.</p>
</td></tr>
</table></td></tr></table>
</body></html>
"""


def render_text(d):
    out = [d.get("subject") or "Pour Decisions", "", d.get("intro") or "", ""]
    for s in d.get("sections") or []:
        evs = s.get("events") or []
        if not evs:
            continue
        out += [s.get("title", "").upper(), "-" * 40]
        for ev in evs:
            score = f" [{ev['score']}/10]" if ev.get("score") is not None else ""
            out.append(f"* {ev.get('title')}{score}")
            out.append(f"  {when_line(ev)}")
            if ev.get("verdict"):
                out.append(f"  {ev['verdict']}")
            if s.get("style") != "compact":
                for w in ev.get("lineup") or []:
                    out.append(f"    - {w}")
                if ev.get("value"):
                    out.append(f"  Value: {ev['value']}")
            for l in ev.get("links") or []:
                out.append(f"  {l.get('label') or 'Link'}: {l.get('url')}")
            out.append("")
    for n in d.get("footnotes") or []:
        out.append(f"note: {n}")
    return "\n".join(out) + "\n"


def main():
    run_dir = sys.argv[1]
    with open(f"{run_dir}/digest.json") as f:
        d = json.load(f)
    with open(f"{run_dir}/digest.html", "w") as f:
        f.write(render_html(d))
    with open(f"{run_dir}/digest.txt", "w") as f:
        f.write(render_text(d))
    print(f"wrote {run_dir}/digest.html and digest.txt")


if __name__ == "__main__":
    main()
