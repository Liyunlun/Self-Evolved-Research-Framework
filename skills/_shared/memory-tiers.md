# Memory Tier Structure — Shared Reference

> Shared definitions for the `memory-*` skills (write, retrieve, consolidate, forget).
> Not a skill itself (no `SKILL.md`). Each `memory-*/SKILL.md` reads this file for
> tier definitions, MEMORY.md index rules, and capacity budgets.

---

## Tier Structure

| Tier | Purpose | Max Files | Retention |
|------|---------|-----------|-----------|
| `memory/episodes/` | Recent observations, raw insights | 20 | 7 days |
| `memory/topics/` | Consolidated knowledge, synthesized themes | 50 | 90 days |
| `memory/procedures/` | Stable processes, permanent decisions | 100 | permanent |

Memory types (episodic / semantic / procedural) emerge naturally from usage —
individual episodes are captured first, synthesized into topics when patterns
repeat, and crystallized into procedures when they describe stable multi-step
workflows.

---

## MEMORY.md

Always-loaded index. Read at every `session-open`. 200-line hard limit forces
consolidation. Contains four sections:

- **Active Context** (~5 lines): what the project is currently focused on
- **Topic Index** (~45 lines, 15 topics × 3 lines): pointers to `memory/topics/`
- **Recent Episodes** (~30 lines, 10 episodes × 3 lines): pointers to `memory/episodes/`
- **Procedure Index** (~30 lines, 10 procedures × 3 lines): pointers to `memory/procedures/`

Approximate line budget:
- Header + Active Context: ~5
- Topic Index: ~45
- Recent Episodes: ~30
- Procedure Index: ~30
- Overhead: ~15
- **Headroom**: ~75 for growth before consolidation pressure

---

## File Formats

### Episode (`memory/episodes/YYYY-MM-DD-NNN.md`)

```markdown
---
type: episode
date: "YYYY-MM-DD"
source_skill: "{triggering skill}"
importance: N      # 1-10
tags: ["{tag1}", "{tag2}"]
consolidated: false
---
## Context
{What was happening}

## Content
{The specific insight, decision, or finding}

## Connections
- Related: {links to related memories or papers}
```

Episode ID: `YYYY-MM-DD-NNN` where `NNN` is zero-padded sequence within the day
(001, 002, ...).

### Topic (`memory/topics/{topic-slug}.md`)

```markdown
---
type: topic
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
source_episodes: []
tags: []
---
## {Topic Name}

### Key Facts
{Consolidated knowledge — synthesized, not concatenated}

### Evolution
| Date | Change | Source |
|------|--------|--------|
```

### Procedure (`memory/procedures/{procedure-slug}.md`)

```markdown
---
type: procedure
created: "YYYY-MM-DD"
source_episodes: []
tags: []
---
## {Procedure Name}

### When to Use
{Trigger conditions}

### Steps
1. ...
```

---

## Importance Scoring (1-10)

Used by `memory-write` to gate persistence. Skip episodes with importance < 5.

Factors:
- **Novelty to project**: Is this new information, or a restatement of existing knowledge?
- **Decision significance**: Does this record a commitment that affects future work?
- **Error / failure severity**: Did something fail in a way that will inform future attempts?
- **Cross-topic relevance**: Does this connect multiple topics?

High-importance examples (7-10): architectural decisions, novel findings, reproducible bugs, key papers read.
Low-importance examples (1-4): chit-chat, routine status checks, commands that didn't work.
