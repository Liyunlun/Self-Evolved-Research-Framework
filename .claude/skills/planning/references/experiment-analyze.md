# experiment.analyze

**Trigger**: User shares experiment results, asks "what do these results mean?", or wants to interpret data.

## Process

1. Parse results from provided data (tables, logs, metrics files).
2. Generate statistical summary table:
   - Our method vs. each baseline
   - Delta (%) for each metric
   - Best result highlighted per metric
3. Baseline comparison:
   - Where we improve, where we don't, and by how much
   - Performance profile across different conditions/datasets
4. Statistical significance testing:
   - t-test for normally distributed metrics
   - Wilcoxon signed-rank for non-normal distributions
   - Bootstrap confidence intervals where appropriate
   - Report p-values and confidence intervals
5. Hypothesis implications:
   - Which hypotheses are supported/refuted by the results
   - Unexpected findings and possible explanations
6. Suggest next steps based on outcomes.

## Suggested Next

- Good results -> `writing.draft` for results section + `paper.figure` for visualizations.
- Bad or inconclusive results -> `decision.analyze` to decide on next experimental direction.
