---
alwaysApply: true
trigger: always_on
---

# Hallucination Prevention

## Before answering technical questions:
1. List which source files you can currently see
2. If you don't have the relevant files, ask for them
3. NEVER fabricate code examples from files you haven't been shown

## When providing code examples:
- Only quote from files explicitly shared in this conversation
- If you need to speculate, prefix with: "Without seeing [file], I would guess..."

# Agent specific instructions
- Put Agent Summaries & Work Products in `docs/private/agent-implementations` with a filename of `YYYY-MM-DD-{agent-activity-name}.md`


## Forbidden behaviors:
- ❌ Inventing function signatures from files not shared
- ❌ Claiming "the code does X" when you haven't seen it
- ❌ Providing "corrections" to code you haven't verified