---
name: experiment
description: Experiment design, execution, monitoring, and hyperparameter exploration
---

# /experiment — Experiment Design and Execution

Route the user's intent to the appropriate sub-skill:

- **Plan an experiment** (user wants to design experiments, map claims to tests, create ablation schedules) → read `references/plan.md` and follow its instructions
- **Run an experiment** (user wants to launch, start, or execute an experiment on cluster or locally) → read `references/run.md` and follow its instructions
- **Monitor an experiment** (user asks about experiment status, progress, or wants updates) → read `references/monitor.md` and follow its instructions
- **Design space exploration / parameter sweep** (user says "DSE", "grid search", "parameter sweep", or needs systematic hyperparameter exploration) → read `references/dse.md` and follow its instructions

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
