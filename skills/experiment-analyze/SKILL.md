---
name: experiment-analyze
description: Parse experiment results (tables, metrics, logs), assess significance vs. baselines, interpret for the hypothesis, and suggest next experiments. Triggers when the user shares training logs, metrics, or asks "what do these results mean?", "are these results good?".
---

# experiment-analyze

**Trigger**: User shares experiment results, training logs, metrics, or asks "what do these results mean?".

**Process**:
1. Parse the results (tables, metrics, logs)
2. Analyze:
   - Are results as expected? Better/worse?
   - Statistical significance (if applicable)
   - Comparison to baselines
   - What the results imply for the research hypothesis
3. Suggest next experiments or adjustments
4. If results are significant, suggest `progress-capture`

**Inputs**: Experiment results (any format)
**Outputs**: Analysis report (inline)
**Token**: ~3-8K
**Composition**: Good results → suggest `writing-draft` for results section. Bad results → suggest `decision-analyze` for next direction
