---
name: evolve-apply
description: Apply approved skill-spec edits from evolve-suggest — archive the current SKILL.md to skills/td-nl/history/{skill}-v{N}.md, edit the skill body, update skill-values metadata, and log the change. Triggers on "apply those improvements", "evolve the skills", or user approval of a pending proposal.
---

# evolve-apply

**Trigger**: User approves a proposal from `evolve-suggest`, or explicitly asks to improve the framework ("apply those improvements", "evolve the skills").

**Shared context**: Before running this skill, Read `skills/_shared/evolve-cycle.md` for the safety rules (one edit per session, archive before edit) and rollback mechanism.

**Process**:

## Phase 1: Read Proposals
1. Read pending proposals from `skills/td-nl/feedback-log.md § Pending Proposals`
2. If called with a specific proposal, use that; otherwise present all pending
3. For each proposal, show: skill, problem, proposed edit, evidence, risk

## Phase 2: User Approval
4. Present proposals and get explicit approval per proposal
5. User can: approve, reject, or modify each proposal

## Phase 3: Apply Edits (for each approved proposal)
6. Archive current spec: copy `skills/{skill-name}/SKILL.md` → `skills/td-nl/history/{skill-name}-v{N}.md`
7. Apply the edit to `skills/{skill-name}/SKILL.md`
8. Update the `skill-values/{skill-name}.md`:
   - Set `last_spec_edit` to today's date
   - Set `edit_reason` to the proposal summary
9. Log to feedback-log.md:
   ```
   - [YYYY-MM-DD] APPLIED: {skill-name} v{N-1}→v{N}: "{edit summary}"
   ```

## Phase 4: Rollback Check (next session)
10. At the next `evolve-suggest`, compare pre-edit and post-edit performance:
    - If output_usefulness dropped >= 2 points → auto-propose rollback
    - Rollback: restore from `skills/td-nl/history/{skill-name}-v{N-1}.md`
    - Log: `[YYYY-MM-DD] ROLLBACK: {skill-name} v{N}→v{N-1}: "{reason}"`

## Phase 5: Evolution Report
11. Generate report:
    ```yaml
    date: "YYYY-MM-DD"
    skills_modified: ["{skill-name}"]
    proposals_approved: N
    proposals_rejected: N
    details:
      - skill: "{name}"
        change: "{description}"
        evidence_sessions: N
        pre_edit_score: X
    ```
12. Append to `config.yaml` `evolution_history`
13. Update CLAUDE.md if behavioral routing changed (rare)

**Outputs**: Modified skill specs + version archive + evolution log
**Token**: ~2-5K
**Composition**: Terminal for the evolution cycle
