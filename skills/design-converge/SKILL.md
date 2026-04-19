---
name: design-converge
description: Convert a set of concrete design options into a weighted criteria matrix (novelty / feasibility / alignment / risk) with a recommendation, key risk, and first concrete step. Triggers when the user picks a direction from research-explore, asks "how should we implement X?", or weighs algorithms/architectures.
---

# design-converge

**Trigger**: User picks a research direction, asks "how should we implement X?", or needs to make an architecture/design decision among concrete options.

**Process**:
1. Clarify the decision scope:
   - What is being decided (algorithm, architecture, framework, method)
   - What are the concrete options (from `research-explore` output or user input)
2. Build a criteria matrix:
   ```
   | Criterion          | Weight | Option A | Option B | Option C |
   |-------------------|--------|----------|----------|----------|
   | Novelty           | {W}    | {score}  | {score}  | {score}  |
   | Feasibility       | {W}    | {score}  | {score}  | {score}  |
   | Alignment w/ goals| {W}    | {score}  | {score}  | {score}  |
   | Risk              | {W}    | {score}  | {score}  | {score}  |
   ```
   Weights derived from project phase and timeline pressure.
3. Recommend the top option with rationale:
   ```
   **Recommendation**: Option {X}
   **Rationale**: {2-3 sentences explaining why, referencing criteria scores}
   **Key risk**: {main concern and mitigation strategy}
   **First concrete step**: {actionable next task}
   ```
4. Record the decision context (regardless of whether user accepts)

**Inputs**: Options (from research-explore or user), project context
**Outputs**: Criteria matrix + recommendation (inline)
**Token**: ~2-4K
**Composition**:
- Decision accepted → chain to `progress-capture` (log the decision)
- Decision rejected → refine criteria or return to `research-explore`
- Always → chain to `memory-write` (record decision analysis)
