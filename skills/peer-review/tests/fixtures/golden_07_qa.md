---
stage: qa
paper_id: toy_paper
model_notes: "Sampled 4/4 references; 1 unverifiable; no identity leak; no offensive language; all 6 AAAI sections present"
severity_counts:
  critical: 1
  major: 0
  minor: 0
---

## Findings

- [critical] Hallucinated citation detected in the final review: `Nonexistent, A. et al. (2025)` — this reference was carried over from the paper into a weakness bullet and should be flagged, not cited as though real (evidence: 06_final.md Weaknesses)
  Detail: Spot-check queries failed to return any matching paper; the venue "NeurIPS 2099" is chronologically impossible. The review correctly flags this as a hallucinated citation (no propagation into References), so QA confirms the flag is appropriate.

## Evidence citations

- 06_final.md Weaknesses bullet 3
- 06_final.md References (correctly excludes the fabricated entry)

## Open questions

- none
