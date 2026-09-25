---
name: weekly-digest
description: Build the weekly Pour Decisions digest of upcoming wine tastings end to end (scan, score, compose, render, send, remember). Use for the scheduled weekly run or when asked for this week's digest.
---

# Weekly digest

`<run_dir>` = `agents/pour-decisions/workspace/runs/<today YYYY-MM-DD>/`.

1. **Read context:** `knowledge/preferences.md`, `knowledge/sources.md`, `memory/events-seen.md`, and the latest file in `memory/digests/` (all under `agents/pour-decisions/`), plus `shared/knowledge/household.md`.
2. **Scan:** follow the `scan-tastings` skill to produce `<run_dir>/scored.json`.
3. **Mark what's new:** an event whose `id` isn't in `memory/events-seen.md` gets the badge `New`. For an event already listed before, mention what changed if anything did (lineup published, price change, sold out).
4. **Compose** `<run_dir>/digest.json` (schema at the top of `bin/render_digest.py`):
   - `subject`: `Pour Decisions · <Mon D> — <the week's headline pick>`, e.g. `Pour Decisions · Sep 28 — Querciabella's three villages`.
   - `week_of`: the Monday of the coming week (ISO).
   - `intro`: 1–2 sentences, conversational, naming the one or two things most worth booking. It's fine to be a little funny. No hype words.
   - `sections`, in this order (drop empty ones):
     1. `🔥 Book now`: score 8–10, style `full`.
     2. `Worth a look`: score 6–7, style `full`.
     3. `Also on`: score ≤5, style `compact`, verdict of about 10 words.
     4. `Classes`: WSET etc., style `compact`, only if there are any.
   - Sort by date within each section. Badges: `New`, `Winemaker-hosted`, `Few seats left`, `Sold out`, `Drive: ~17 mi`, as they apply.
   - `footnotes`: source problems from `fetch-report.md` or `scored.json`'s `source_notes`, in plain words (e.g. "K&L lineups come from search results and may be incomplete.").
5. **Render:**
   ```bash
   python3 agents/pour-decisions/bin/render_digest.py <run_dir>
   ```
6. **Send:** if `agents/pour-decisions/bin/send_email.py` exists and `RESEND_API_KEY` is set, run it on `<run_dir>`. Otherwise skip sending and say where the digest is (`<run_dir>/digest.html`).
7. **Remember** (only after the digest was actually sent, or when told to record a test run; otherwise test runs would take the `New` badge off events before the first real email):
   - Add every event in the digest that isn't already in `memory/events-seen.md` to it (one row each).
   - Copy `<run_dir>/digest.txt` to `memory/digests/<today>.md`.
   - Update `memory/source-health.md` with this run's status for each source.
8. **Report** in 3–5 lines: how many events per source, the top picks, and anything that failed.
