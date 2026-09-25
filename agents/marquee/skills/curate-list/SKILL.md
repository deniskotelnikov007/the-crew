---
name: curate-list
description: Build a curated movie, series, or documentary list for the couple from their preferences and watch history. Use when asked what to watch or for a themed list.
---

# Curate a list

1. **Read context:** `agents/marquee/knowledge/preferences.md`, `agents/marquee/memory/watched.md`, `agents/marquee/memory/recommended.md`, `shared/knowledge/household.md`, `shared/knowledge/travel.md`.
2. **Pin the request:** occasion (see "Occasions"), mood, format (film / series / doc), runtime, number of picks (default 3 per category). If none given, use "Typical movie night": short on weeknights, longer on Friday/weekend.
3. **Find candidates:** start from what both rated 8–10, the "Shared sweet spots", and the "Exploration goals" canons, and from shared interests. Look for connections: same director, writer, era, tone.
4. **Filter out:** anything we've both watched (a title only one of us has seen is fine; say who has seen it), suggested in the last 90 days, or hitting either person's dealbreakers. Check each pick against Denis's dislikes (he vetoes most) and Masha's gore/violence tolerance of 3 (stylized is OK; skip graphic gore).
5. **Check availability:** if "Where we watch" is filled in, use web search to confirm where each pick streams in the US, and find a trailer link.
6. **Balance the list:** about 75% safe bets and 25% wildcards across the request, labeled. Don't let one person's taste dominate.
7. **Present** each pick as:
   `**Title** (Year) · Safe bet | Wildcard · runtime · where to watch · [trailer](url)`
   One paragraph, no spoilers: why it fits both of us, tied to our tastes (e.g. "same director as X, which you both gave 8+"), and any content warnings.
8. **Log** every pick in `agents/marquee/memory/recommended.md` with outcome `suggested`.
