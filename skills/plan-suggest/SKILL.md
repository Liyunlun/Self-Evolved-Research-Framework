---
name: plan-suggest
description: Read the checklist tree + milestones and produce a prioritized list of 3-5 next tasks with HIGH/MED/LOW rank and checklist references. Triggers on "what should I do next?", "what's the priority?", "give me a task list", or when the user seems unsure about next steps.
---

# plan-suggest

**Trigger**: User asks "what should I do next?", "what's the priority?", or seems unsure about next steps.

**Process**:
1. Read: `Checklist.md` (L0 project root) for overall progress
2. Read: relevant L1 checklists (`checklists/short-term.md`, `checklists/mid-term.md`) for `[ ]` (incomplete) items
3. Read: `config.yaml` (milestones, timeline) for deadline context
4. Prioritize incomplete items by:
   - Deadline proximity (nearest milestone first)
   - Dependency chains (unblock other items first)
   - Blocking status (items others depend on)
   - Cross-term priority: Short-term items rank above mid-term items of equal priority. Milestone proximity overrides term ordering — if a mid-term milestone is within 7 days, its items rank first.
5. Generate 3-5 prioritized task suggestions with checklist references:
   ```
   1. [HIGH] {task} — {reason, milestone impact} (→ checklists/{path})
   2. [MED]  {task} — {reason} (→ checklists/{path})
   3. [LOW]  {task} — {nice-to-have}
   ```
6. No multi-question wizard — direct output

**Auto-strategy selection**:
- Near milestone → emphasize milestone-critical tasks from checklist
- Long gap since last session → suggest review/catch-up first
- Blocked on external → suggest parallel tasks from checklist

**Inputs**: Checklist.md, L1 checklists, config.yaml
**Outputs**: Prioritized task list with checklist references (inline)
**Token**: ~2-3K
**Composition**: User picks a theory task → triggers appropriate theory/proof skill
