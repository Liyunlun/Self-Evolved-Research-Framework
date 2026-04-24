---
stage: correctness
paper_id: toy_paper
model_notes: "Symbolically checked 1 equation via numpy; no proofs or algorithms in paper"
severity_counts:
  critical: 1
  major: 0
  minor: 0
---

## Findings

- [critical] Equation in §3 has a dimension mismatch: y = W x + b with W ∈ R^{2×4}, x ∈ R^4, b ∈ R^3, y ∈ R^3 (evidence: §3 first Method section)
  Detail: W x yields a vector in R^2. Adding b ∈ R^3 to a vector in R^2 is undefined. Either W should be R^{3×4}, or y and b should be R^2. The architecture description is internally inconsistent.

## Evidence citations

- §3 (method equation)

## Open questions

- What are the intended dimensions of the linear layer? This determines whether the later claims are meaningful.
