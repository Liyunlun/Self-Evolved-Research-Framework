# Experiment Micro-Skills

> Triggered by experiment execution or monitoring intent. Automates the deploy→monitor→collect pipeline.
> Leverages GPU cluster config from user CLAUDE.md (server16, remote-3, remote-5, remote-13).

## experiment.run

**Trigger**: User asks to "run an experiment", "launch training", "test this on GPU", or provides a training script to execute

**Process**:
1. **Pre-flight checks**:
   - Run `bash ~/.claude/skills/monitor-gpu-utilization/scripts/gpu_status.sh` to get GPU availability
   - Identify best GPU: prefer remote machines, >20 GB free, <10% utilization
   - Verify conda environment exists on target machine
   - Verify the experiment script/command is valid (basic syntax check)
2. **Generate experiment metadata**:
   ```yaml
   exp_id: "exp-{YYYYMMDD}-{NNN}"    # sequential within day
   command: "{full command}"
   machine: "{hostname}"
   gpu: "{CUDA_VISIBLE_DEVICES value}"
   started: "YYYY-MM-DD HH:MM:SS"
   status: "launched"
   working_dir: "{path}"
   log_file: "/tmp/{exp_id}.log"
   config_snapshot: "{key hyperparams or config overrides}"
   ```
3. **Deploy and launch**:
   - For remote: `ssh hsshi@{IP} "cd {working_dir} && CUDA_VISIBLE_DEVICES={gpu} nohup {python} {command} > /tmp/{exp_id}.log 2>&1 &"`
   - For local: `CUDA_VISIBLE_DEVICES={gpu} nohup {command} > /tmp/{exp_id}.log 2>&1 &`
   - Capture PID from launch
4. **Save experiment log**: Write metadata to `logs/experiments/{exp_id}.yaml`
5. **Confirm launch**: Output 3-line status
   ```
   [EXP] {exp_id} launched on {machine} GPU:{gpu}
   Command: {abbreviated command}
   Monitor: experiment.monitor will auto-check, or run manually
   ```
6. **Notify** (if autonomy.auto_proceed enabled): Call `scripts/notify.py` with launch info

**Inputs**: Experiment command/script + optional config overrides
**Outputs**: `logs/experiments/{exp_id}.yaml` + running process on GPU
**Token**: ~2-4K
**Composition**: Launch complete → suggest or auto-trigger `experiment.monitor` after delay

---

## experiment.monitor

**Trigger**: Auto-triggered after `experiment.run`, user asks "how's the experiment?", "check training", or during autonomous overnight mode

**Process**:
1. **Load active experiments**: Read `logs/experiments/*.yaml` where `status: "launched"` or `status: "running"`
2. **For each active experiment**:
   a. Check if process is still running:
      - Remote: `ssh hsshi@{IP} "ps -p {pid} -o pid= 2>/dev/null"`
      - Local: `ps -p {pid} -o pid= 2>/dev/null`
   b. Tail last 20 lines of log file:
      - Remote: `ssh hsshi@{IP} "tail -20 /tmp/{exp_id}.log"`
      - Local: `tail -20 /tmp/{exp_id}.log`
   c. Parse log for key metrics (loss, accuracy, epoch, step)
   d. Check for errors (OOM, NaN, traceback)
3. **Update experiment status**:
   - Still running with progress → `status: "running"`, update `last_checked`, `latest_metrics`
   - Completed successfully → `status: "completed"`, set `ended`, `final_metrics`
   - Crashed/errored → `status: "failed"`, set `ended`, `error_summary`
4. **Output status table**:
   ```
   | Exp ID | Machine | Status | Duration | Latest Metrics |
   |--------|---------|--------|----------|----------------|
   ```
5. **Collect results** (if completed):
   - Copy relevant output files from remote to local if needed
   - Extract final metrics into the experiment log
6. **Notify** (if autonomy.auto_proceed enabled): Send status via `scripts/notify.py`
7. **Update** `logs/experiments/{exp_id}.yaml` with current state

**Inputs**: Active experiment IDs (from logs/experiments/)
**Outputs**: Updated `logs/experiments/{exp_id}.yaml` + status report (inline)
**Token**: ~2-4K
**Composition**:
- Experiment completed → chain to `experiment.analyze` (in `skills/micro/planning.md`)
- Experiment failed → surface error, suggest fix or re-run
- All experiments idle + autonomy mode → sleep and re-check (via composition with session)

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
ended: null                          # set on completion/failure
status: "launched"                   # launched | running | completed | failed
last_checked: null
latest_metrics: {}
final_metrics: {}
error_summary: null
```

## Autonomy Integration

When `config.yaml § autonomy.auto_proceed` is true:
- `experiment.run` launches without confirmation (after pre-flight passes)
- `experiment.monitor` auto-polls at intervals (composition chain handles scheduling)
- On completion → auto-chains to `experiment.analyze`
- On failure → notifies and pauses for human review (unless `autonomy.auto_retry: true`)

## TD-NL Integration

Both options track performance via:
- `memory/td-nl/option-values/experiment-run.md`
- `memory/td-nl/option-values/experiment-monitor.md`

Key metrics for TD assessment:
- `experiment.run`: Did pre-flight catch issues? Did launch succeed? Was GPU selection optimal?
- `experiment.monitor`: Were status checks accurate? Were errors caught early? Was result collection complete?
