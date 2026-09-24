---
name: log-watched
description: Record a movie the couple watched, their ratings, and feedback on suggestions. Use when told "we watched X" or given a reaction to a recommendation.
---

# Log a watched movie

1. Add a row to `agents/marquee/memory/watched.md`: title, year, date (today unless told), Denis's and Masha's ratings 1–10, scored separately, short notes.
   - If a rating is missing, ask for it once; otherwise leave it blank.
2. If the movie is in `agents/marquee/memory/recommended.md`, update its outcome to `watched`.
3. If the feedback reveals a lasting preference (e.g. "too slow for us"), update `agents/marquee/knowledge/preferences.md` and say what changed.
4. For a rejected suggestion, set the outcome to `rejected — <reason>`.
