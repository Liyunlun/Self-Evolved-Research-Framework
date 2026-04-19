---
name: plan-milestone
description: Report phase progress, days to next milestone, token budget, and on-track/at-risk/behind status by reading config.yaml and methodology/approach.md. Triggers on "when is the deadline?", "are we on track?", "milestone status", "how much time left?".
---

# plan-milestone

**Trigger**: User asks about timeline, "when is the deadline?", "are we on track?".

**Process**:
1. Read `config.yaml` milestones and `methodology/approach.md` phases
2. Calculate:
   - Days to next milestone
   - % of phase tasks completed (from logs)
   - Token budget remaining for this phase
3. Output milestone status:
   ```
   Phase {X}: {name}
   Timeline: {start} → {end} ({days_remaining}d remaining)
   Progress: ~{pct}% (based on logged accomplishments)
   Token budget: {used}/{allocated} for this phase
   Risk: {on track / at risk / behind}
   ```

**Inputs**: config.yaml, methodology/approach.md, logs
**Outputs**: Milestone status (inline)
**Token**: ~1-2K
**Composition**: If behind → auto-suggest `plan-suggest` with urgency
