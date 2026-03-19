
# Experiment Micro-Skills — Local Mode

> Direct experiment execution on local/remote GPUs without MetaScheduler.
> This file is merged with experiment.base.md during setup to produce experiment.md.

## experiment.run

**Trigger**: User asks to "run an experiment", "launch training", "test this on GPU", or provides a training script to execute

**Process**:
1. **Pre-flight checks**:
   - Query GPU availability (local `nvidia-smi` or remote SSH)
   - Identify best GPU: prefer remote machines, >20 GB free, <10% utilization
   - Verify conda environment exists on target machine
   - Verify the experiment script/command is valid (basic syntax check)
2. **Generate experiment metadata**:
   ```yaml
   exp_id: "exp-{YYYYMMDD}-{NNN}"
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
   - For remote: `ssh {user}@{IP} "cd {working_dir} && CUDA_VISIBLE_DEVICES={gpu} nohup {python} {command} > /tmp/{exp_id}.log 2>&1 &"`
   - For local: `CUDA_VISIBLE_DEVICES={gpu} nohup {command} > /tmp/{exp_id}.log 2>&1 &`
   - Capture PID from launch
4. **Save experiment log**: Write metadata to `logs/experiments/{exp_id}.yaml`
5. **Confirm launch**:
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
      - Remote: `ssh {user}@{IP} "ps -p {pid} -o pid= 2>/dev/null"`
      - Local: `ps -p {pid} -o pid= 2>/dev/null`
   b. Tail last 20 lines of log file:
      - Remote: `ssh {user}@{IP} "tail -20 /tmp/{exp_id}.log"`
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
- Experiment completed → chain to `experiment.analyze`
- Experiment failed → surface error, suggest fix or re-run
- All experiments idle + autonomy mode → sleep and re-check
