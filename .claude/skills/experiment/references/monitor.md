# experiment.monitor

**Trigger**: User asks to check experiment status, "how's the experiment going?", or wants progress updates.

## Process

**MetaScheduler mode**:
1. Query status: `mb task manager <chatId> "check status of experiment {exp_name}"`.
2. Report: running/completed/failed, current metrics if available, estimated time remaining.

**Local mode**:
1. Check result files in `experiments/{exp_name}/results/` and logs in `logs/experiments/`.
2. Parse metrics from training logs (loss curves, validation metrics).
3. Report current status: epoch/step progress, current metrics, anomalies detected.

## Suggested Next
- Experiment completed → `experiment.analyze` to interpret results.
