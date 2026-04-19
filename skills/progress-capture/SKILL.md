---
name: progress-capture
description: Extract accomplishments, decisions, and direction changes from the user's report and persist them to logs/progress/YYYY-MM-DD_NNN.yaml. Triggers when the user says "I did X today", "just finished Y", "we decided Z", or shares a results/progress update.
---

# progress-capture

**Trigger**: User reports completing something, shares results, or says "I did X today".

**Process**:
1. Extract from conversation:
   - What was accomplished
   - Key decisions made
   - Any direction changes
2. Format as structured entry:
   ```yaml
   date: "YYYY-MM-DD"
   type: "progress"
   accomplishments:
     - type: "{paper_read|experiment|proof|code|decision}"
       content: "{description}"
   decisions: []
   next_steps: []
   ```
3. Append to `logs/progress/YYYY-MM-DD_NNN.yaml`
4. One-line confirmation: "Logged: {summary}"

**Inputs**: User's progress report (from conversation)
**Outputs**: `logs/progress/YYYY-MM-DD_NNN.yaml`
**Token**: ~1-2K
**Composition**: If goal adjustment detected → auto-suggest `plan-suggest`
