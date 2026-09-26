---
name: weekly-digest
description: Build the weekly Pour Decisions digest of upcoming wine tastings end to end (scan, score, compose, render, send, remember). Use for the scheduled weekly run or when asked for this week's digest.
---

# Weekly digest

`<run_dir>` = `agents/pour-decisions/workspace/runs/<today YYYY-MM-DD>/`.

1. **Read context:** `knowledge/preferences.md`, `knowledge/sources.md`, `memory/events-seen.md`, and the latest file in `memory/digests/` (all under `agents/pour-decisions/`), plus `shared/knowledge/household.md`.
2. **Scan:** follow the `scan-tastings` skill to produce `<run_dir>/scored.json`.
   **Scout:** then follow `scout-tastings`, which adds a few outside finds to the same file and logs new venue candidates.
3. **Mark what's new:** an event whose `id` isn't in `memory/events-seen.md` gets the badge `New`, except in the very first digest (when `events-seen.md` has no rows yet), where everything would be new and the badge means nothing. For an event already listed before, mention what changed if anything did (lineup published, price change, sold out).
4. **Compose** `<run_dir>/digest.json` (schema at the top of `bin/render_digest.py`). The renderer does the layout (This week by day, then Sneak peeks, with labels from scores), so you only supply content:
   - `subject`: `Pour Decisions · <Mon D of the Monday that starts "This week"> — <this week's headline>`, e.g. `Pour Decisions · Sep 28 — Failla's four sites`.
   - `run_date`: today (ISO). The digest goes out Sunday night; the renderer makes "This week" the coming Monday–Sunday on a Sunday (the current week on any other day) and hides days already past.
   - `intro`: 2–3 sentences, conversational, with the one or two event names in `**bold**`. Lead with the best thing happening this week, then the one or two later events to book now. It's fine to be a little funny. No hype words.
   - `events`: every scored event from `scored.json` (keep `source`, `lineup` with scores, `highlights`, `badges`, `links`).
   - `classes`: from `scored.json`, only if there are any.
   - `footnotes`: source problems from `fetch-report.md` or `scored.json`'s `source_notes` in plain words, plus one line on what was left out and why. The renderer adds the critic-abbreviation legend itself.
5. **Render:**
   ```bash
   python3 agents/pour-decisions/bin/render_digest.py <run_dir>
   ```
   This writes `digest.html` (preview), `digest.email.html`, `digest.txt`, and `inline.json` (the logos the email attaches inline).
6. **Send:** if `agents/pour-decisions/bin/send_email.py` exists and `RESEND_API_KEY` is set, run it on `<run_dir>`. Otherwise skip sending and say where the digest is (`<run_dir>/digest.html`).
7. **Remember** (only after the digest was actually sent, or when told to record a test run; otherwise test runs would take the `New` badge off events before the first real email):
   - Add every event in the digest that isn't already in `memory/events-seen.md` to it (one row each).
   - Copy `<run_dir>/digest.txt` to `memory/digests/<today>.md`.
   - Update `memory/source-health.md` with this run's status for each source.
8. **Report** in 3–5 lines: how many events per source, the top picks, and anything that failed.
