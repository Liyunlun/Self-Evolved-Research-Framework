---
stage: evaluations
paper_id: toy_paper
model_notes: "Ran 1 sanity check (accuracy range); no embedded code snippets found"
severity_counts:
  critical: 1
  major: 2
  minor: 0
---

## Findings

- [critical] Reported accuracy 1.30 is outside the valid range [0, 1] — result is impossible as stated (evidence: §4 table, FlawNet row)
  Detail: Either the metric is mis-named (accuracy must be in [0,1]) or the cell value is wrong. A simple sanity check fails: `assert 0 <= 1.30 <= 1` raises.
- [major] Only one baseline (generic "Baseline") — no standard methods for flawed-input classification compared (evidence: §4 table)
  Detail: The related work section names three prior methods; none of them appear as baselines.
- [major] No seeds, no error bars, no variance reported (evidence: §4 table)
  Detail: A single number per method with no uncertainty.

## Evidence citations

- §4 (experiments, table)

## Open questions

- Is "1.30" a typo for "0.93"? If so, is the paper still SOTA after correcting the baseline?
- How many random seeds were used?
