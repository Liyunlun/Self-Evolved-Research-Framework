---
name: theory-decompose
description: Break a complex proof goal into sub-lemmas with a dependency graph and critical-path analysis. Triggers when the user has a hard theorem and asks "how do I prove this?", faces a multi-step argument, or needs a proof roadmap.
---

# theory-decompose

**Trigger**: User has a complex proof goal, asks "how do I prove this?", or faces a multi-step argument.

**Process**:
1. Break the main claim into sub-lemmas / intermediate results
2. For each sub-lemma:
   - State precisely
   - Classify difficulty (routine / moderate / hard / open)
   - Suggest technique
3. Draw dependency graph (text-based)
4. Identify the critical path (hardest sub-lemma)
5. Save roadmap to `outputs/{topic}/roadmaps/` if substantial

**Inputs**: Theorem/goal statement + any partial progress
**Outputs**: Proof roadmap with dependency structure
**Token**: ~3-8K
**Composition**:
- Hard sub-lemma → suggest `theory-search` for cross-domain techniques
- If user provides attempt → chain to `proof-critique`
