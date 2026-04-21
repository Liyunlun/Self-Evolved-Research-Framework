## evolve.apply

**Trigger**: User approves a proposal from `evolve.suggest`.

### Process
**Phase 1 — Read pending proposals**:
Load all unapplied proposals from the most recent evolution cycle.

**Phase 2 — User approval**:
Present each proposal individually with:
- What will change
- Why (evidence from observations)
- Expected impact
User can approve, reject, or modify each proposal.

**Phase 3 — Apply edits**:
For each approved proposal:
1. Archive current spec: copy `.claude/skills/{group}/SKILL.md` to `.claude/skills/{group}/SKILL.md.bak.{timestamp}`
2. Apply the edit to the SKILL.md file
3. Update evolution records with the change

**Phase 4 — Rollback check**:
At the next session after applying edits:
- Monitor the modified skill's `output_usefulness` score
- If it drops >= 2 points compared to pre-edit baseline, auto-propose a rollback to the archived version

**Phase 5 — Evolution report**:
Summarize all applied changes, their rationale, and the rollback monitoring plan.

### Suggested Next
Terminal for the evolution cycle
