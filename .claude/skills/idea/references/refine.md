# idea.refine

**Trigger**: User says "refine idea", "make this idea more concrete", "sharpen the proposal", or after `idea.verify` confirms novelty.

## Process
1. **Read target idea**: From `methodology/ideas/*.md` or user-provided description
2. **Problem anchoring**:
   - What exactly does this solve? (1-2 sentences)
   - What is the evaluation metric?
   - What would "success" look like concretely?
3. **Frontier alignment**:
   - How does this relate to SOTA? (cite specific papers from `resources/papers/`)
   - What is the key differentiation?
   - What assumptions does it make vs. existing work?
4. **Implementation orientation**:
   - What are the concrete algorithmic steps?
   - What data/compute is required?
   - What is the minimal experiment to validate the core claim?
5. **Output structured proposal** to `methodology/ideas/{slug}.md`:
   ```markdown
   ---
   title: "{title}"
   status: "refined"
   refined_from: "{source idea reference}"
   date: "YYYY-MM-DD"
   ---
   ## Problem Statement
   {precise problem definition}

   ## Proposed Approach
   {concrete algorithmic/methodological steps}

   ## Key Differentiation
   {what makes this different from existing work}

   ## Minimal Validation
   {smallest experiment that tests the core claim}

   ## Resource Requirements
   {data, compute, dependencies}
   ```

## Suggested Next
- Refined idea → `checklist.create(category=method)` to track implementation
- Refined idea → `experiment.plan` for experiment design
