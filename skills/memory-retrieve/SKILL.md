---
name: memory-retrieve
description: Surface relevant persisted memories (episodes, topics, procedures) into the current conversation by scoring MEMORY.md entries on tag overlap, keyword match, recency, and importance. Runs at session-open and before knowledge-dependent skills like plan-suggest, status-report.
---

# memory-retrieve

**Trigger**: Before knowledge-dependent micro-skills.

**Initiation**:
- `session-open` (always — load active context)
- Before `plan-suggest`, `status-report`
- Self-initiated when agent lacks context for current task

**Shared context**: Before running this skill, Read `skills/_shared/memory-tiers.md` for the tier structure and MEMORY.md index layout.

**Process**:
1. Determine query: what does the agent need to know right now?
2. Read `memory/MEMORY.md`
3. Score index entries by: tag overlap, keyword match, recency, importance
4. Select top 5 candidates from index
5. Read full files for top 3 candidates
6. Surface relevant content into conversation context

**Artifact**: Inline context (not a file)
**Token**: ~1-3K
**Composition**: Provides context for the calling skill to continue
