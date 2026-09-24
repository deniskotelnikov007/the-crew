#!/usr/bin/env bash
# Regenerate .claude/agents and .claude/skills as symlinks into agents/ and shared/.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p .claude/agents .claude/skills
find .claude/agents .claude/skills -maxdepth 1 -type l -delete

for dir in agents/*/; do
  name=$(basename "$dir")
  [[ "$name" == _* ]] && continue
  ln -s "../../agents/$name/AGENT.md" ".claude/agents/$name.md"
done

link_skill() {
  local src=$1 name
  name=$(basename "$src")
  if [[ -e ".claude/skills/$name" ]]; then
    echo "error: duplicate skill name '$name' ($src)" >&2
    exit 1
  fi
  ln -s "../../$src" ".claude/skills/$name"
}

for s in shared/skills/*/; do [[ -d "$s" ]] && link_skill "${s%/}"; done
for s in agents/[!_]*/skills/*/; do [[ -d "$s" ]] && link_skill "${s%/}"; done

echo "Agents:"; ls .claude/agents
echo "Skills:"; ls .claude/skills
