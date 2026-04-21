# experiment.run

**Trigger**: User asks to run, launch, or start an experiment.

## Process

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

## Suggested Next
- Experiment launched → `experiment.monitor` to track progress.
