---
name: decision-analyze
description: Structured analysis of a decision — for each option list pros/cons, effort, risk, milestone alignment, and reversibility, then produce a recommendation (user still decides). Triggers on "should I do X or Y?", "which approach is better?", "weigh these options for me".
---

# decision-analyze

**Trigger**: User weighs options, asks "should I do X or Y?", or considers pivoting research direction.

**Process**:
1. Identify the decision and options
2. For each option, analyze:
   - Pros / Cons
   - Effort estimate
   - Risk level
   - Alignment with current milestones
   - Reversibility
3. Present comparison table
4. Give recommendation with reasoning
5. Note: this is analysis only — the user decides

**Inputs**: Decision context + options
**Outputs**: Decision analysis (inline)
**Token**: ~2-5K
**Composition**: Decision made → may trigger `progress-capture` to log the decision
