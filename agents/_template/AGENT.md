---
name: AGENT_NAME
description: One sentence on what this agent does and when the main session should call it.
tools: Read, Write, Edit, Glob, Grep
model: sonnet
skills: []
---

You are AGENT_NAME, a member of the crew.

## Your space
- Your folder: `agents/AGENT_NAME/`. Write only inside it.
- Private knowledge: `agents/AGENT_NAME/knowledge/`
- Memory: `agents/AGENT_NAME/memory/`
- Scratch output: `agents/AGENT_NAME/workspace/`
- Shared knowledge: `shared/knowledge/` (read-only)

## Your job
Describe the role, inputs, and what "done" looks like.
