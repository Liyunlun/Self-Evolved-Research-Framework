---
name: research-explore
description: Open-ended exploration of 3-5 research directions with pros/cons, key references, and effort estimates, ranked by novelty × feasibility × alignment. Triggers on "what are the possible directions?", "let's think about approaches to X", "brainstorm research angles".
---

# research-explore

**Trigger**: User asks to explore research directions, brainstorm approaches, or says "what are the possible directions?", "let's think about approaches to X", or engages in open-ended research exploration without a specific method in mind.

**Process**:
1. Gather context:
   - Read `config.yaml` (project goals, current phase)
   - Execute `memory-retrieve` for relevant memories (past decisions, paper insights)
   - Read recent `resources/papers/*.md` Quick Reference sections for related work
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
- User selects a direction → chain to `design-converge`
- User wants more options → iterate with refined criteria
- Always → chain to `memory-write` (log explored directions)
