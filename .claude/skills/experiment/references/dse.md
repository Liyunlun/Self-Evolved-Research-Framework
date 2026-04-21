# math.dse — Design Space Exploration

**Trigger**: User says "DSE", "parameter sweep", "grid search", "explore hyperparameters", or needs systematic hyperparameter exploration.

## Process
1. Define search space:
   - Parameters with ranges (continuous, discrete, or categorical)
   - Objective function (metric to optimize, minimize or maximize)
   - Constraints (max GPU hours, memory limits, minimum performance thresholds)
2. Select search strategy:
   - **Grid search**: exhaustive, for small discrete spaces (< 50 configs)
   - **Random search**: for large spaces, sample N configs uniformly
   - **Bayesian-inspired**: sequential, use results from early configs to guide later choices
3. Generate configuration list as YAML:
   ```yaml
   configs:
     - name: config_001
       params: {lr: 0.001, hidden: 256, dropout: 0.1}
     - name: config_002
       params: {lr: 0.01, hidden: 512, dropout: 0.2}
   ```
4. Execute iteratively:
   - Run batch of configs → collect results → analyze
   - For Bayesian-inspired: select next configs based on promising regions
   - Early-stop configs that clearly underperform
5. Output exploration report:
   - All configs tested with results
   - Best configuration and its performance
   - Sensitivity analysis (which parameters matter most)
   - Visualization of search landscape where possible
6. Save report to `experiments/dse/{name}/report.md`.

## Suggested Next
- Optimal config found → `experiment.plan` for full-scale validation with the best settings.
