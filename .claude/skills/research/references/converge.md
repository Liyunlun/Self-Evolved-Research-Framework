# design.converge

**Trigger**: User picks a direction from exploration — "let's go with option 2", "how should we implement X?", or when narrowing from multiple options to a concrete decision.

## Process

1. Clarify decision scope:
   - What exactly is being decided?
   - What constraints apply (time, resources, methodology)?
   - Are there non-negotiable requirements?
2. Build criteria matrix with weighted scoring:
   | Criterion | Weight | Description |
   |-----------|--------|-------------|
   | Novelty | configurable | Contribution beyond prior work |
   | Feasibility | configurable | Execution difficulty given resources |
   | Alignment | configurable | Fit with project goals and methodology |
   | Risk | configurable | Downside if approach fails |
3. Score each remaining option against the matrix
4. Recommend top option with:
   - **Rationale**: why this option wins on the criteria
   - **Key risk**: the single biggest thing that could go wrong
   - **First concrete step**: what to do immediately to begin execution

## Suggested Next

- Recommendation accepted: `progress.capture`
- Recommendation rejected or user wants to reconsider: `research.explore`
- Always: `memory.write` (capture the decision and rationale)
