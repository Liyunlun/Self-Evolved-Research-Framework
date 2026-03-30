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

> Defined in `skills/micro/planning.md`. See Intent Router #27.

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

# Experiment Execution — MetaScheduler Mode

> This project uses MetaScheduler for all experiment execution and monitoring.
> The skills `experiment.run` and `experiment.monitor` are NOT available in this mode.
> Instead, experiments are submitted to and monitored by the MetaScheduler bot.

## Submitting Experiments

When experiment execution is needed (after `experiment.plan` approval or user request):

1. **Prepare submission**:
   - Ensure code is committed and pushed (`git push`)
   - Verify experiment config is in `experiments/{exp_name}/`
   - Note the conda environment name and entry command
2. **Query available resources first**:
   ```
   mb task manager <chatId> "查看当前可用 GPU 资源"
   ```
   `<chatId>`: your current chat ID from the system prompt (look for: `You are running as bot "xxx" in chat "oc_xxx..."`)
3. **Based on availability, submit experiment**:
   ```
   mb task manager <chatId> "项目 {project_name}，
     需要 {gpu_count}x {gpu_type}，conda {env}，
     运行 {command}，工作目录 {working_dir}"
   ```
   - GPU type/count chosen based on Step 2 results and experiment requirements
   - Do NOT hardcode defaults — let experiment needs and resource availability guide the choice
4. **MetaScheduler handles**:
   - Resource allocation (`/allocate-gpu`)
   - Experiment launch and monitoring (`/run-experiment`, `/monitor-experiment`)
5. **Receive results**:
   - MetaScheduler notifies on completion/failure
   - Results are available in the experiment directory on the compute node
   - Use `mb task manager <chatId> "check status of task {task_id}"` for progress

## Checking Experiment Status

```
mb task manager <chatId> "check status of task {task_id}"
```

Or check all active experiments:
```
mb task manager <chatId> "list active experiments for {project_name}"
```

## After Experiment Completes

When MetaScheduler notifies completion:
1. Results are in `experiments/{exp_name}/results/` (synced back if remote)
2. Chain to `experiment.analyze` for result interpretation
3. Chain to `checklist.update` to mark experiment items `[x]`

## Configuration

MetaScheduler settings are in `config.yaml § metascheduler`:
```yaml
metascheduler:
  bot_name: "manager"
  default_conda_env: "research"
```
