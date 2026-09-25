---
name: curate-list
description: Build a curated movie, series, or documentary list for the couple from their preferences and watch history. Use when asked what to watch or for a themed list.
---

# Curate a list

1. **Read context:** `agents/marquee/knowledge/preferences.md`, `agents/marquee/memory/watched.md`, `agents/marquee/memory/recommended.md`, `shared/knowledge/household.md`, `shared/knowledge/travel.md`.
2. **Pin the request:** occasion (see "Occasions"), mood, format (film / series / doc), runtime, number of picks (default 3 per category). If none given, use "Typical movie night": short on weeknights, longer on Friday/weekend.
3. **Find candidates:** start from what both rated 8–10, the "Shared sweet spots", and the "Exploration goals" canons, and from shared interests. Look for connections: same director, writer, era, tone.
4. **Filter out:** anything we've both watched (a title only one of us has seen is fine; say who has seen it), suggested in the last 90 days, or hitting either person's dealbreakers. Check each pick against Denis's dislikes (he vetoes most) and Masha's gore/violence tolerance of 3 (stylized is OK; skip graphic gore).
5. **Look up the facts** with web search for each pick. Never state a number, award or list from memory. If a fact can't be confirmed, leave it out.
   - Where it streams in the US, and a trailer link.
   - Rotten Tomatoes: critics score (Tomatometer) and audience score (Popcornmeter). For a series, use the series overall.
   - Oscar wins and nominations, with categories. If there are none, the most notable other honor: Cannes / Venice / Berlin top prize, Golden Globe, BAFTA. For series: Emmys and Golden Globes.
   - Notable lists: AFI 100, IMDb Top 250, Sight & Sound greatest-films poll, NYT 100 Best Movies of the 21st Century, Criterion Collection. Also flag it when a pick belongs to one of our "Exploration goals" canons.
6. **Balance the list:** about 75% safe bets and 25% wildcards across the request, labeled. Don't let one person's taste dominate.
7. **Present** each pick as a magazine-style capsule:

   ```
   ### Title (Year)
   Director · runtime · genre · Safe bet | Wildcard
   Rotten Tomatoes: 94% critics · 92% audience
   Oscars: Won Best Picture, Best Director · Nominated for Best Original Screenplay, Best Original Score
   Lists: AFI 100 (#45) · IMDb Top 250

   Synopsis: 2–3 sentences like a magazine blurb or the back of a Blu-ray. Premise, setting and tone, in vivid third person. No spoilers, no "you'll love".

   For you: one short line connecting it to our history (e.g. "Nolan again, after Inception 10/9"). Say who has already seen it, if anyone.
   Heads-up: content warnings (violence level, sensitive content). Omit if none.
   Watch: Netflix · [Trailer](url)
   ```

   Drop the Oscars and Lists lines when there's nothing notable. Don't pad them.
8. **Log** every pick in `agents/marquee/memory/recommended.md` with outcome `suggested`.
