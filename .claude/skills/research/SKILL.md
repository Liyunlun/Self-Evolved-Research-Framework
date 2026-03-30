# /research — Research Exploration & Design Convergence

When to use this skill:
- User asks open-ended questions about research directions or possibilities
- User wants to narrow down from multiple options to a concrete plan
- "What are the possible directions?", "How should we implement X?"
- Early-stage ideation through to decision-making

## research.explore

**Trigger**: Open-ended research exploration — "what are the possible directions?", "what approaches exist for X?", brainstorming phase, or when the project needs new ideas.

### Process
1. Gather context:
   - Read `config.yaml` for project scope, methodology, and constraints
   - Execute `memory.retrieve` for relevant prior work and decisions
   - Check `papers/` and any literature notes for related references
2. Generate 3-5 candidate directions, each containing:
   - **Core idea**: 1-2 sentence description
   - **Pros**: key advantages
   - **Cons**: key risks or limitations
   - **References**: relevant papers, methods, or prior work
   - **Effort estimate**: rough scope (days/weeks, complexity)
3. Rank directions by three criteria:
   - **Novelty**: how original is this relative to existing work?
   - **Feasibility**: can we execute this with current resources and timeline?
   - **Alignment**: does this serve the project's stated goals and methodology?
4. Present ranked list with clear reasoning for the ranking

### Suggested Next
- User selects a direction: `design.converge`
- Always: `memory.write` (capture the exploration and options considered)

## design.converge

**Trigger**: User picks a direction from exploration — "let's go with option 2", "how should we implement X?", or when narrowing from multiple options to a concrete decision.

### Process
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

### Suggested Next
- Recommendation accepted: `progress.capture`
- Recommendation rejected or user wants to reconsider: `research.explore`
- Always: `memory.write` (capture the decision and rationale)
