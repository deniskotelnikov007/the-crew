#!/usr/bin/env bash
# Usage: scripts/new-agent.sh <name>
set -euo pipefail
cd "$(dirname "$0")/.."

name=${1:?usage: scripts/new-agent.sh <name>}
[[ -e "agents/$name" ]] && { echo "agents/$name already exists" >&2; exit 1; }

cp -R agents/_template "agents/$name"
sed -i '' "s/AGENT_NAME/$name/g" "agents/$name/AGENT.md"
scripts/sync.sh
echo "Created agents/$name. Edit agents/$name/AGENT.md next."
