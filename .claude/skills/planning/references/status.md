# status.report

**Trigger**: User asks "project status?", "where are we?", "summarize progress", or wants a comprehensive overview.

## Process

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

## Suggested Next

- After status review -> `plan.suggest` to determine next steps.
