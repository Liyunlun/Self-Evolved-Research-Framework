---
name: experiment-monitor
description: Poll active experiments from logs/experiments/*.yaml — check PID liveness, tail logs, parse loss/metrics, detect OOM/NaN/tracebacks, and update status launched→running→completed/failed. Triggers on "how's the experiment?", "check training", "monitor runs", and auto-runs after experiment-run.
---

# experiment-monitor

**Trigger**: Auto-triggered after `experiment-run`, user asks "how's the experiment?", "check training", or during autonomous overnight mode.

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
- Experiment completed → chain to `experiment-analyze`
- Experiment failed → surface error, suggest fix or re-run
- All experiments idle + autonomy mode → sleep and re-check (via composition with session)

## TD-NL Integration

Tracked via `skills/td-nl/skill-values/experiment-monitor.md`.
Key metrics for TD assessment: were status checks accurate? were errors caught early? was result collection complete?
