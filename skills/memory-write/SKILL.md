---
name: memory-write
description: Persist an insight, decision, or finding to memory/episodes/YYYY-MM-DD-NNN.md (skipping importance < 5 or duplicates), then update memory/MEMORY.md Recent Episodes. Triggers when a skill produces a novel insight, the user says "remember this", or at session-close for unrecorded insights.
---

# memory-write

**Trigger**: After insight-producing micro-skills, or when user says "remember this."

**Initiation** (chain from other skills):
- After `paper-read`, `decision-analyze`, `progress-capture`, `theory-formalize`
- After `proof-critique`, `experiment-analyze`, `idea-discover`, `idea-verify`
- Agent self-detects novel insight during any skill execution

**Shared context**: Before running this skill, Read `skills/_shared/memory-tiers.md` for the tier structure, episode format, and MEMORY.md index rules.

**Process**:
1. Read `memory/MEMORY.md` (should be in context from session-open)
2. Assess importance (1-10):
   - Novelty to project
   - Decision significance
   - Error/failure severity
   - Cross-topic relevance
3. If importance < 5 → skip (not worth persisting)
4. Check for duplicates: scan MEMORY.md index for similar content
5. If duplicate → update existing memory instead of creating new
6. Write episode file to `memory/episodes/YYYY-MM-DD-NNN.md` using the episode format in `skills/_shared/memory-tiers.md`
7. Update `memory/MEMORY.md` Recent Episodes table (prepend; keep last 10)
8. If MEMORY.md > 180 lines → flag for consolidation

**Artifact**: `memory/episodes/YYYY-MM-DD-NNN.md` + updated MEMORY.md
**Token**: ~1-2K
**Composition**: If episode count exceeds threshold → chain to `memory-consolidate`
