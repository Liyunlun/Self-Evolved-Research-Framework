---
stage: presentation
paper_id: toy_paper
model_notes: "Scanned heading tree; inspected all captions (none present)"
severity_counts:
  critical: 0
  major: 0
  minor: 2
---

## Findings

- [minor] Two consecutive section headings both labeled "## 3. Method" (evidence: between §3 and §4)
  Detail: The paper emits `## 3. Method` twice in succession with different content. This is almost certainly a typo and will confuse readers.
- [minor] No figures or tables have captions (evidence: only table in §4)
  Detail: The results table in §4 has no caption explaining what FLAWS is or how accuracy is computed.

## Evidence citations

- §3 (duplicate heading)
- §4 (table)

## Open questions

- none
