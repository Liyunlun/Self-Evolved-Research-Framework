# /experiment — Experiment Design and Execution

When to use this skill:
- User wants to plan, run, or monitor experiments
- User needs to explore hyperparameter spaces or do parameter sweeps
- User says "plan experiment", "run experiment", "check status", "grid search", "DSE"
- User uses Chinese equivalents: "设计实验", "跑实验"

## experiment.plan

**Trigger**: User says "plan experiment", "设计实验", or is ready to design experiments after idea refinement or design convergence.

### Process
1. Read context for experiment design:
   - Hypothesis or research question to test
   - Available baselines and prior results
   - Existing experiment configs in `experiments/`
2. Design experiment with:
   - **Claims to test**: map each experiment to a specific paper claim
   - **Independent variables**: what we manipulate (methods, hyperparameters, data)
   - **Dependent variables**: what we measure (metrics, with definitions)
   - **Controls and baselines**: what we compare against, ensuring fair comparison
   - **Ablations**: which components to remove/replace to test their contribution
3. Generate structured plan:
   - Claims table: claim → experiment → expected outcome
   - Configurations table: config name → hyperparameters → purpose
   - Ablation schedule: what to ablate, in what order, expected impact
   - Resource estimate: GPU hours, storage, estimated wall-clock time
4. Save plan to `experiments/{exp_name}/plan.md`.

### Suggested Next
- Plan approved → create experiment checklist items to track execution.

## experiment.run

**Trigger**: User asks to run, launch, or start an experiment.

### Process

**MetaScheduler mode** (GPU experiments on cluster):
1. Prepare submission:
   - Run code.review → code.commit workflow (ensure reproducibility with reviewed code)
   - Verify experiment config is complete and saved
   - Check data paths and dependencies are accessible
2. Query available resources: `mb task manager <chatId> "describe need: model, GPU count, duration, purpose"`.
3. Wait for MetaScheduler to assign resources and provide endpoint.
4. Submit experiment to assigned resources.
5. MetaScheduler handles allocation, launch, and monitoring.

**Local mode** (CPU experiments or small-scale tests):
1. Set up environment (verify dependencies, activate conda/venv).
2. Before writing new baseline code, check `resources/repos/` for existing implementations.
3. Generate `run.sh` with full experiment command (reproducible).
4. Run experiment; save raw outputs to `experiments/{exp_name}/results/`.
5. Redirect stdout/stderr to `logs/experiments/`.

### Suggested Next
- Experiment launched → `experiment.monitor` to track progress.

## experiment.monitor

**Trigger**: User asks to check experiment status, "how's the experiment going?", or wants progress updates.

### Process

**MetaScheduler mode**:
1. Query status: `mb task manager <chatId> "check status of experiment {exp_name}"`.
2. Report: running/completed/failed, current metrics if available, estimated time remaining.

**Local mode**:
1. Check result files in `experiments/{exp_name}/results/` and logs in `logs/experiments/`.
2. Parse metrics from training logs (loss curves, validation metrics).
3. Report current status: epoch/step progress, current metrics, anomalies detected.

### Suggested Next
- Experiment completed → `experiment.analyze` to interpret results.

## math.dse

**Trigger**: User says "DSE", "parameter sweep", "grid search", "explore hyperparameters", or needs systematic hyperparameter exploration.

### Process
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

### Suggested Next
- Optimal config found → `experiment.plan` for full-scale validation with the best settings.
