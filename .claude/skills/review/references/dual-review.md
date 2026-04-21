# dual_review

**Trigger**: When `config.yaml` section `dual_review.enabled` is true and during `writing.review`, `idea.verify`, `proof.critique`, or `experiment.analyze` — or when the user explicitly requests cross-model review.

## Process

1. **Send to external model**: Submit the artifact (paper section, proof, idea summary, or experiment analysis) to the external model via MCP tool specified in `config.yaml` section `dual_review.tool` (default: `mcp__codex__codex`). Include sufficient context for meaningful review:
   - The artifact itself
   - Brief project context (methodology, goals)
   - Specific review criteria relevant to the artifact type
2. **Generate internal review simultaneously**: Produce an independent review using the same criteria, without referencing the external model's output
3. **Synthesize perspectives**:
   - **Consensus points**: Where both models agree — mark as high-confidence findings
   - **Divergence points**: Where models disagree — flag explicitly for user attention
4. **Report with clear attribution**:
   - Present internal review findings with label (e.g., "Claude assessment")
   - Present external model findings with label (e.g., "External model assessment")
   - Highlight consensus items as actionable with high confidence
   - Highlight divergence items with both perspectives explained
5. **Handle significant divergence**: If the models fundamentally disagree on a point (not just emphasis differences), present both views side by side and let the user decide. Do not silently merge conflicting assessments.

## Suggested Next

- Consensus on improvements: apply via the relevant skill (`writing.polish`, `proof.fix`, `experiment.refine`, etc.)
