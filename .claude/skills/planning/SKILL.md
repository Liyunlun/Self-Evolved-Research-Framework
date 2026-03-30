# /planning — Project Planning and Progress Tracking

When to use this skill:
- User is unsure what to do next or needs task prioritization
- User wants to check deadlines, milestones, or project status
- User reports completing a task or making a decision
- User wants to analyze experiment results for next steps
- User says "what next?", "status?", "should I do X or Y?", "what do these results mean?"

## plan.suggest

**Trigger**: User asks "what to do next?", seems unsure about next steps, or needs task prioritization.

### Process
1. Read `Checklist.md` (L0 master checklist) for overall project structure.
2. Read L1 checklists for each incomplete item to get granular task status.
3. Read `config.yaml` milestones for deadlines and deliverables.
4. Prioritize tasks by:
   - Deadline proximity (urgent items first)
   - Dependency chains (unblock downstream tasks)
   - Blocking status (remove bottlenecks)
   - Cross-term priority (align with long-term goals)
5. Generate 3-5 prioritized tasks, each with:
   - Priority tag: `[HIGH]`, `[MED]`, or `[LOW]`
   - Task description
   - Checklist reference (which L0/L1 item it addresses)
   - Estimated effort
6. Auto-strategy selection:
   - Near milestone → surface milestone-critical tasks first
   - Long gap between milestones → suggest review/consolidation first
   - Blocked on external → suggest parallel tasks to maintain momentum

### Suggested Next
- User picks a task → route to the appropriate skill for execution.

## plan.milestone

**Trigger**: User asks "when is the deadline?", "are we on track?", or wants milestone status.

### Process
1. Read `config.yaml` milestones section for all defined milestones.
2. Calculate for each milestone:
   - Days remaining until deadline
   - Percentage of associated tasks completed (from checklists)
   - Token budget remaining (if applicable)
3. Output milestone status report:
   - Timeline visualization (milestones on a timeline)
   - Per-milestone: deadline, completion %, risk level (On Track / At Risk / Behind)
   - Risk assessment with specific concerns for at-risk milestones

### Suggested Next
- If behind schedule → `plan.suggest` with urgency flag to focus on critical path.

## progress.capture

**Trigger**: User reports completing something, makes a decision, or changes project direction.

### Process
1. Extract from conversation:
   - Accomplishments (what was completed)
   - Decisions made (and rationale)
   - Direction changes (pivots, scope adjustments)
2. Format as structured YAML entry:
   ```yaml
   date: YYYY-MM-DD
   type: accomplishment|decision|direction_change
   summary: ...
   details: ...
   related_checklist_items: [...]
   ```
3. Save to `logs/progress/YYYY-MM-DD_NNN.yaml` (NNN = sequential counter for the day).

### Suggested Next
- If the accomplishment changes project goals → `plan.suggest` to re-prioritize.

## status.report

**Trigger**: User asks "project status?", "where are we?", "summarize progress", or wants a comprehensive overview.

### Process
1. Read `Checklist.md` (L0) and all L1 checklists.
2. Compute completion statistics:
   - Per-term completion (e.g., Term 1: 80%, Term 2: 45%)
   - Per-category completion (theory, experiments, writing, etc.)
3. Read `config.yaml` milestones for deadline context.
4. Read `SUMMARY.md` for recent activity log.
5. Generate comprehensive status report:
   - **Progress overview**: completion stats with visual indicators
   - **Blocking items**: tasks that are stuck or waiting on dependencies
   - **Recent activity**: last 5-7 notable events from progress logs
   - **Outputs produced**: papers, figures, proofs, code artifacts
   - **Milestone status**: upcoming deadlines and readiness

### Suggested Next
- After status review → `plan.suggest` to determine next steps.

## decision.analyze

**Trigger**: User is weighing options, asks "should I do X or Y?", or faces a research/engineering decision.

### Process
1. Identify the decision and enumerate all options (from user input or inferred).
2. Analyze each option across dimensions:
   - **Pros**: benefits, strengths, opportunities
   - **Cons**: drawbacks, risks, limitations
   - **Effort**: time and resource requirements
   - **Risk**: probability and impact of failure
   - **Alignment**: fit with project goals and milestones
   - **Reversibility**: how easy to undo if wrong
3. Present comparison table (options as columns, dimensions as rows).
4. Give a recommendation with reasoning, clearly stating assumptions.

### Suggested Next
- Decision made → `progress.capture` to record the decision and rationale.

## experiment.analyze

**Trigger**: User shares experiment results, asks "what do these results mean?", or wants to interpret data.

### Process
1. Parse results from provided data (tables, logs, metrics files).
2. Generate statistical summary table:
   - Our method vs. each baseline
   - Delta (%) for each metric
   - Best result highlighted per metric
3. Baseline comparison:
   - Where we improve, where we don't, and by how much
   - Performance profile across different conditions/datasets
4. Statistical significance testing:
   - t-test for normally distributed metrics
   - Wilcoxon signed-rank for non-normal distributions
   - Bootstrap confidence intervals where appropriate
   - Report p-values and confidence intervals
5. Hypothesis implications:
   - Which hypotheses are supported/refuted by the results
   - Unexpected findings and possible explanations
6. Suggest next steps based on outcomes.

### Suggested Next
- Good results → `writing.draft` for results section + `paper.figure` for visualizations.
- Bad or inconclusive results → `decision.analyze` to decide on next experimental direction.
