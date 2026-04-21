# plan.milestone

**Trigger**: User asks "when is the deadline?", "are we on track?", or wants milestone status.

## Process

1. Read `config.yaml` milestones section for all defined milestones.
2. Calculate for each milestone:
   - Days remaining until deadline
   - Percentage of associated tasks completed (from checklists)
   - Token budget remaining (if applicable)
3. Output milestone status report:
   - Timeline visualization (milestones on a timeline)
   - Per-milestone: deadline, completion %, risk level (On Track / At Risk / Behind)
   - Risk assessment with specific concerns for at-risk milestones

## Suggested Next

- If behind schedule -> `plan.suggest` with urgency flag to focus on critical path.
