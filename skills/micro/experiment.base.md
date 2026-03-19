# Experiment Micro-Skills — Shared Base

> Skills shared by both Local and MetaScheduler installation modes.
> This file is merged with either experiment.local.md or experiment.ms.md during setup.

## experiment.plan

**Trigger**: User asks to "plan an experiment", "design the experiment", or after `idea.refine` / `design.converge` produces a concrete approach

**Process**:
1. **Read context**:
   - Research hypothesis from `methodology/approach.md` or conversation
   - Available baselines from `resources/papers/`
   - Existing experiment configs from `experiments/`
2. **Design experiment**:
   - **Claims to test**: List specific, falsifiable claims
   - **Independent variables**: What we vary
   - **Dependent variables**: What we measure
   - **Controls/baselines**: What we compare against
   - **Ablations**: Which components to test independently
3. **Generate experiment plan**:
   ```markdown
   ## Experiment Plan: {title}

   ### Claims
   | # | Claim | Test | Success Criterion |
   |---|-------|------|-------------------|

   ### Configurations
   | Config | Params | Purpose |
   |--------|--------|---------|

   ### Ablation Schedule
   | Ablation | Removes | Tests |
   |----------|---------|-------|

   ### Resource Estimate
   GPUs: {N} × {type} | Duration: ~{hours}h | Seeds: {N}
   ```
4. **Save** to `experiments/{exp_name}/plan.md`

**Inputs**: Research hypothesis + available resources
**Outputs**: Experiment plan in `experiments/{exp_name}/plan.md`
**Token**: ~3-6K
**Composition**: Plan approved → `checklist.create(category=experiment)` to track execution

---

## experiment.analyze

**Trigger**: User shares experiment results, training logs, metrics, or asks "what do these results mean?"

**Process**:
1. **Parse the results** (tables, metrics, logs, CSV, JSON, wandb exports)
2. **Generate statistical summary table**:
   ```
   | Metric | Ours | Baseline A | Baseline B | Δ (vs best) |
   |--------|------|-----------|-----------|-------------|
   | {metric} | {val ± std} | {val ± std} | {val ± std} | {+/-X.X%} |
   ```
3. **Baseline comparison analysis**:
   - Identify which baselines are beaten, by how much
   - Identify metrics where our method underperforms
   - Compute relative improvement percentages
4. **Statistical significance assessment**:
   - If multiple seeds/runs available: compute mean, std, confidence intervals
   - If applicable: suggest paired t-test, Wilcoxon signed-rank, or bootstrap
   - Report: `Significant (p < 0.05)` / `Marginal (p < 0.10)` / `Not significant`
5. **Hypothesis implications**:
   - Are results as expected? Better/worse?
   - What do the results imply for the research hypothesis?
   - Any surprising findings?
6. **Suggest next steps**: next experiments, ablations, or adjustments
7. If results are significant, suggest `progress.capture`

**Inputs**: Experiment results (any format)
**Outputs**: Analysis report with statistical tables (inline)
**Token**: ~3-8K
**Composition**: Good results → suggest `writing.draft` + `paper.figure`. Bad results → suggest `decision.analyze`

---

## math.dse

**Trigger**: User says "设计空间探索", "DSE", "parameter sweep", "tune parameters", "grid search", "explore hyperparameters"

**Process**:
1. **Define search space**:
   - Parameters to explore (with ranges and step sizes)
   - Objective function (metric to optimize)
   - Constraints (max time, max configs, GPU budget)
2. **Select exploration strategy**:
   - Grid search: exhaustive (small spaces)
   - Random search: sample N configs (medium spaces)
   - Bayesian-inspired: prioritize promising regions based on intermediate results
3. **Generate configuration list**:
   ```yaml
   dse:
     name: "{exploration name}"
     objective: "{metric to maximize/minimize}"
     parameters:
       - name: "{param}"
         range: [min, max]
         step: {step}
     configs:
       - id: "config-001"
         params: {key: value, ...}
       - ...
   ```
4. **Execute iteratively** (or generate batch script):
   - Run initial configurations
   - Analyze intermediate results
   - Select next configurations based on results
   - Repeat until convergence or budget exhaustion
5. **Output exploration report**:
   ```
   ### DSE Report: {name}
   Configs tested: {N} | Best: config-{id}
   | Config | {param1} | {param2} | {objective} |
   |--------|----------|----------|-------------|

   Optimal: {param1}={val}, {param2}={val} → {objective}={val}
   Sensitivity: {which params matter most}
   ```
6. **Save** to `experiments/dse/{name}/report.md`

**Inputs**: Parameter ranges + objective function + program/script
**Outputs**: Optimal configuration + exploration report
**Token**: ~5-15K
**Composition**: Optimal config found → `memory.write` + `checklist.update` + suggest `experiment.plan` for full validation

---

## Experiment Log Format: `logs/experiments/{exp_id}.yaml`

```yaml
exp_id: "exp-20260316-001"
command: "python -m option_exp.entry.run_gymnax +alg=pqn_craftax"
machine: "remote-3"
ip: "172.16.51.3"
gpu: "0"
pid: 12345
working_dir: "~/codeforshare/purejaxql"
log_file: "/tmp/exp-20260316-001.log"
python_path: "/home/hsshi/anaconda3/envs/torch/bin/python"
config_snapshot:
  alg: "pqn_craftax"
  num_seeds: 3
started: "2026-03-16 14:30:00"
ended: null
status: "launched"
last_checked: null
latest_metrics: {}
final_metrics: {}
error_summary: null
```

## Autonomy Integration

When `config.yaml § autonomy.auto_proceed` is true:
- Experiments launch without confirmation (after pre-flight passes)
- Monitoring auto-polls at intervals
- On completion → auto-chains to `experiment.analyze`
- On failure → notifies and pauses for human review (unless `autonomy.auto_retry: true`)
