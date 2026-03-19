# Research Micro-Skills — Exploration & Design Convergence

> Triggered by open-ended research exploration or architecture/design decisions.

## research.explore

**Trigger**: User asks to explore research directions, brainstorm approaches, or says
"what are the possible directions?", "let's think about approaches to X", or engages
in open-ended research exploration without a specific method in mind.

**Process**:
1. Gather context:
   - Read `config.yaml` (project goals, current phase)
   - Execute `memory.retrieve` for relevant memories (past decisions, paper insights)
   - Read recent `papers/*.md` Quick Reference sections for related work
2. Generate 3-5 research directions, each with:
   ```
   ### Direction {N}: {title}
   - **Core idea**: {1-2 sentence description}
   - **Pros**: {strengths, novelty, feasibility}
   - **Cons**: {risks, difficulty, resource requirements}
   - **Key references**: {relevant papers from reading history}
   - **Estimated effort**: {low / medium / high}
   ```
3. Rank directions by: novelty, feasibility, alignment with project goals
4. Suggest next step: "Pick a direction to explore further, or refine the criteria."

**Inputs**: Project context (config, memory, papers)
**Outputs**: Ranked research directions with trade-off analysis (inline)
**Token**: ~3-5K
**Composition**:
- User selects a direction → chain to `design.converge`
- User wants more options → iterate with refined criteria
- Always → chain to `memory.write` (log explored directions)

---

## design.converge

**Trigger**: User picks a research direction, asks "how should we implement X?",
or needs to make an architecture/design decision among concrete options.

**Process**:
1. Clarify the decision scope:
   - What is being decided (algorithm, architecture, framework, method)
   - What are the concrete options (from `research.explore` output or user input)
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

**Inputs**: Options (from research.explore or user), project context
**Outputs**: Criteria matrix + recommendation (inline)
**Token**: ~2-4K
**Composition**:
- Decision accepted → chain to `progress.capture` (log the decision)
- Decision rejected → refine criteria or return to `research.explore`
- Always → chain to `memory.write` (record decision analysis)
