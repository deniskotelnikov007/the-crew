# The Crew

A crew of Claude Code subagents. Each agent has its own space; shared resources live in `shared/`.

## Agents
- `marquee` — curates movie lists for the two of us based on our tastes and what we've already watched.

## Layout
- `agents/<name>/AGENT.md` — the subagent definition (frontmatter + system prompt). Source of truth.
- `agents/<name>/skills/` — skills private to that agent.
- `agents/<name>/knowledge/` — reference data only that agent reads.
- `agents/<name>/memory/` — records the agent keeps between runs (committed).
- `agents/<name>/workspace/` — scratch output (gitignored).
- `shared/skills/` — skills any agent can use.
- `shared/knowledge/` — facts useful to every agent (e.g. who we are).
- `.claude/agents/` and `.claude/skills/` — **generated symlinks**. Never edit directly; run `scripts/sync.sh`.

## Rules
1. An agent writes only inside its own `agents/<name>/` folder. `shared/` is read-only for agents.
2. A skill starts private. Move it to `shared/skills/` once a second agent needs it.
3. Skill folder names must be unique across `shared/` and all agents.
4. After adding or renaming an agent or skill, run `scripts/sync.sh`.
