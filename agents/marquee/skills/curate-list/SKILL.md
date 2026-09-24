---
name: curate-list
description: Build a curated movie list for the couple from their preferences and watch history. Use when asked what to watch or for a themed list.
---

# Curate a list

1. **Read context:** `agents/marquee/knowledge/preferences.md`, `agents/marquee/memory/watched.md`, `agents/marquee/memory/recommended.md`, `shared/knowledge/household.md`.
2. **Pin the request:** theme, mood, runtime, number of picks (default 5). If none given, use "Typical movie night".
3. **Find candidates:** start from what both rated 4–5 and from shared interests. Look for connections: same director, writer, era, tone.
4. **Filter out:** anything already watched, suggested in the last 90 days, or hitting either person's dealbreakers.
5. **Check availability:** if "Where we watch" is filled in, use web search to confirm where each pick streams in our region.
6. **Balance the list:** mix at least one safe bet and one wildcard. Don't let one person's taste dominate.
7. **Present** each pick as:
   `**Title** (Year) · runtime · where to watch`
   `Why: one line tied to our tastes (e.g. "same director as X, which you both gave 5").`
8. **Log** every pick in `agents/marquee/memory/recommended.md` with outcome `suggested`.
