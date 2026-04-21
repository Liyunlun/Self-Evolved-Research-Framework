# plan.suggest

**Trigger**: User asks "what to do next?", seems unsure about next steps, or needs task prioritization.

## Process

1. Read `Checklist.md` (L0 master checklist) for overall project structure.
2. Read L1 checklists for each incomplete item to get granular task status.
3. Read `config.yaml` milestones for deadlines and deliverables.
4. Prioritize tasks by:
   - Deadline proximity (urgent items first)
   - Dependency chains (unblock downstream tasks)
   - Blocking status (remove bottlenecks)
   - Cross-term priority (align with long-term goals)
5. Generate 3-5 prioritized tasks, each with:
   - Priority tag: `[HIGH]`, `[MED]`, or `[LOW]`
   - Task description
   - Checklist reference (which L0/L1 item it addresses)
   - Estimated effort
6. Auto-strategy selection:
   - Near milestone -> surface milestone-critical tasks first
   - Long gap between milestones -> suggest review/consolidation first
   - Blocked on external -> suggest parallel tasks to maintain momentum

## Suggested Next

- User picks a task -> route to the appropriate skill for execution.
