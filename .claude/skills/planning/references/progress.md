# progress.capture

**Trigger**: User reports completing something, makes a decision, or changes project direction.

## Process

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

## Suggested Next

- If the accomplishment changes project goals -> `plan.suggest` to re-prioritize.
