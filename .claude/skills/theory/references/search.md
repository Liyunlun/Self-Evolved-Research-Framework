## search

**Trigger**: User is stuck on a proof step and needs techniques from other mathematical domains, or wants to find existing tools that apply.

### Process
1. Identify the mathematical structure of the problem:
   - What objects are involved (matrices, functions, graphs, measures, etc.)
   - What properties are needed (bounds, convergence, existence, uniqueness)
   - What makes the problem hard (non-convexity, infinite dimension, dependencies)
2. Search across mathematical domains for applicable techniques:
   - Spectral graph theory (eigenvalue methods, Cheeger inequality, expanders)
   - Functional analysis (operator theory, Banach space methods, fixed-point theorems)
   - Optimization (convex relaxation, duality, gradient methods, proximal operators)
   - Information geometry (Fisher information, natural gradient, divergence measures)
   - Statistical learning theory (VC dimension, Rademacher complexity, PAC-Bayes)
   - Topology and geometry (covering numbers, metric entropy, manifold structure)
   - Algebra (group actions, representation theory, polynomial methods)
3. For each candidate technique, assess applicability:
   - **Direct**: theorem applies as-is with minor verification of conditions
   - **Needs adaptation**: core idea applies but assumptions differ; specify what changes
   - **Inspirational**: proof strategy may transfer but substantial new work needed
4. Rank candidates by relevance and provide for each:
   - The specific theorem/technique name and reference
   - How it connects to the current problem
   - What assumptions need to be verified
   - Estimated effort to apply

### Suggested Next
- If a directly applicable theorem is found that needs formalization -> `theory.formalize`
