---
name: memory-consolidate
description: Synthesize unconsolidated episodes into topics (shared tags, 3+ episodes) and procedures (repeated multi-step processes), then shrink MEMORY.md below its 200-line hard limit. Runs at session-close and when episode / line thresholds are crossed.
---

# memory-consolidate

**Trigger**: Capacity management and knowledge synthesis.

**Initiation**:
- `session-close` (always check conditions)
- MEMORY.md > 180 lines
- 15+ unconsolidated episodes
- 3+ episodes sharing the same primary tag

**Shared context**: Before running this skill, Read `skills/_shared/memory-tiers.md` for the tier definitions and file formats.

**Process**:
1. Read all unconsolidated episodes (`consolidated: false`)
2. Cluster by: tag overlap → source skill → temporal proximity
3. For each cluster of 3+ episodes:
   a. **Topic emergence**: Synthesize into `memory/topics/{topic-slug}.md` using the topic format from `skills/_shared/memory-tiers.md`.
   b. **Procedure emergence**: If 2+ episodes describe the same multi-step process, synthesize into `memory/procedures/{procedure-slug}.md` using the procedure format.
4. Mark source episodes as `consolidated: true`
5. Update MEMORY.md index (add topics/procedures, remove consolidated episodes)
6. If MEMORY.md still > 200 lines → chain to `memory-forget`

**Artifact**: `memory/topics/*.md` and/or `memory/procedures/*.md`
**Token**: ~2-4K
