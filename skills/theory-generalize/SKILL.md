---
name: theory-generalize
description: Propose generalizations of a proven result along axes like weaker assumptions, higher dimensions, different metrics, or stochastic versions — and assess which proof steps break in each case. Triggers on "can we generalize?", "does this extend to...", or after a special case is proven.
---

# theory-generalize

**Trigger**: User asks "can we generalize?", "does this extend to...", or has proven a special case.

**Process**:
1. Identify the proven result and its specific assumptions
2. Propose generalizations along multiple axes:
   - Weaker assumptions (e.g., convex → quasi-convex)
   - Higher dimensions / larger spaces
   - Different norms / metrics
   - Stochastic / approximate versions
3. For each generalization:
   - State the generalized claim
   - Assess feasibility (likely true / unclear / likely false)
   - Identify which proof steps break
4. Recommend most promising generalization direction

**Inputs**: Proven theorem + proof sketch
**Outputs**: Generalization analysis (inline)
**Token**: ~3-8K
**Composition**: Promising generalization → chain to `theory-decompose` for the generalized proof
