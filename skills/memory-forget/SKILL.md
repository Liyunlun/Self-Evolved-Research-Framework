---
name: memory-forget
description: Delete or archive low-value memories (unretrieved episodes with importance < 5, consolidated episodes with importance < 7, superseded decisions) while preserving architectural decisions, key findings, and active hypotheses. Runs after memory-consolidate if still over the 200-line budget.
---

# memory-forget

**Trigger**: Capacity pressure or stale content cleanup.

**Initiation**:
- After `memory-consolidate` if still over capacity
- MEMORY.md > 200 lines

**Shared context**: Before running this skill, Read `skills/_shared/memory-tiers.md` for the tier retention rules.

**Process**:
1. Identify candidates:
   - Episodes with no retrievals and importance < 5
   - Consolidated episodes with importance < 7
   - Superseded decisions
2. **Never forget**: architectural decisions, key findings, active hypotheses
3. Delete or archive candidates
4. Update MEMORY.md: remove entries from index

**Token**: ~1K
