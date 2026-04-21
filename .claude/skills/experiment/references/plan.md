# experiment.plan

**Trigger**: User says "plan experiment", or is ready to design experiments after idea refinement or design convergence.

## Process
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

## Suggested Next
- Plan approved → create experiment checklist items to track execution.
