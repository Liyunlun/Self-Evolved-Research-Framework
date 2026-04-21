## compare

**Trigger**: User wants to compare two or more papers, methods, or approaches side-by-side.

### Process
1. Read the paper files from `resources/papers/` for each paper being compared
2. Generate a structured comparison table covering:
   - Method / Architecture
   - Training data and preprocessing
   - Evaluation metrics and benchmarks
   - Main quantitative results
   - Theoretical guarantees (if any)
   - Computational cost / scalability
   - Limitations and failure modes
3. Below the table, provide:
   - Key differentiators (what each paper does that others don't)
   - Complementary strengths (what could be combined)
   - Implications for user's research direction
4. If comparing >3 papers, organize by sub-groups sharing similar approaches

### Suggested Next
- If comparison reveals a design decision to make -> `decision.analyze`
