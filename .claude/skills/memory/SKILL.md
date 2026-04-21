---
name: memory
description: Persistent knowledge management — write, retrieve, consolidate, and forget across a three-tier memory system
---

# /memory — Persistent Knowledge Management

## Tier Structure

| Tier | Purpose | Max Files | Retention |
|------|---------|-----------|-----------|
| `episodes/` | Recent observations | 20 | 7 days |
| `topics/` | Consolidated knowledge | 50 | 90 days |
| `procedures/` | Stable processes | 100 | permanent |

Episode files use `YYYY-MM-DD-NNN` numbering (e.g., `2026-03-30-001.md`).
`MEMORY.md` line budget: ~200 lines. Flag when exceeding 180 lines.

Route the user's request to the matching sub-skill below:

- **Write a new memory entry** — saving an insight, decision, or observation after skill execution; "remember this", "save this": read `references/write.md` and follow its instructions.
- **Retrieve prior knowledge** — querying memory before knowledge-dependent skills, recalling past decisions, "what did we decide about X?": read `references/retrieve.md` and follow its instructions.
- **Consolidate episodes into topics** — clustering related episodes, synthesizing topic summaries, managing MEMORY.md line budget: read `references/consolidate.md` and follow its instructions.
- **Forget low-value entries** — capacity cleanup, removing expired or unretrieved entries while protecting critical knowledge: read `references/forget.md` and follow its instructions.

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
