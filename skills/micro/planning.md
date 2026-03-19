# Planning & Progress Micro-Skills

> Triggered by planning, status, or progress-related context.

## plan.suggest

**Trigger**: User asks "what should I do next?", "what's the priority?", or seems unsure about next steps

**Process**:
1. Read: `config.yaml` (milestones, timeline), `methodology/approach.md` (phases), last few `logs/digest/*.yaml`
2. Assess current state:
   - Where are we in the timeline?
   - What was accomplished recently?
   - What's the next milestone?
3. Generate 3-5 prioritized task suggestions:
   ```
   1. [HIGH] {task} — {reason, milestone impact}
   2. [MED]  {task} — {reason}
   3. [LOW]  {task} — {nice-to-have}
   ```
4. No multi-question wizard — direct output

**Auto-strategy selection**:
- Near milestone → emphasize milestone-critical tasks
- Long gap since last session → suggest review/catch-up first
- Blocked on external → suggest parallel tasks

**Inputs**: Project state (config, logs, methodology)
**Outputs**: Prioritized task list (inline)
**Token**: ~2-3K
**Composition**: User picks a theory task → triggers appropriate theory/proof skill

---

## plan.milestone

**Trigger**: User asks about timeline, "when is the deadline?", "are we on track?"

**Process**:
1. Read `config.yaml` milestones and `methodology/approach.md` phases
2. Calculate:
   - Days to next milestone
   - % of phase tasks completed (from logs)
   - Token budget remaining for this phase
3. Output milestone status:
   ```
   Phase {X}: {name}
   Timeline: {start} → {end} ({days_remaining}d remaining)
   Progress: ~{pct}% (based on logged accomplishments)
   Token budget: {used}/{allocated} for this phase
   Risk: {on track / at risk / behind}
   ```

**Inputs**: config.yaml, methodology/approach.md, logs
**Outputs**: Milestone status (inline)
**Token**: ~1-2K
**Composition**: If behind → auto-suggest `plan.suggest` with urgency

---

## progress.capture

**Trigger**: User reports completing something, shares results, or says "I did X today"

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
**Composition**: If goal adjustment detected → auto-suggest `plan.suggest`

---

## status.report

**Trigger**: User asks "where are we?", "project status?", or "give me an overview"

**Process**:
1. Read: config.yaml, SUMMARY.md, recent logs, methodology/approach.md
2. Generate comprehensive status:
   - Overall progress (phase, timeline, token budget)
   - Recent activity (last 3-5 sessions)
   - Key research outputs produced
   - Open questions / blockers
   - Upcoming milestones
3. Keep to ~15-20 lines

**Inputs**: All project state files
**Outputs**: Status report (inline)
**Token**: ~1-2K
**Composition**: Naturally leads to `plan.suggest` if user wants next steps

---

## decision.analyze

**Trigger**: User weighs options, asks "should I do X or Y?", or considers pivoting research direction

**Process**:
1. Identify the decision and options
2. For each option, analyze:
   - Pros / Cons
   - Effort estimate
   - Risk level
   - Alignment with current milestones
   - Reversibility
3. Present comparison table
4. Give recommendation with reasoning
5. Note: this is analysis only — the user decides

**Inputs**: Decision context + options
**Outputs**: Decision analysis (inline)
**Token**: ~2-5K
**Composition**: Decision made → may trigger `progress.capture` to log the decision

---

## experiment.analyze

**Trigger**: User shares experiment results, training logs, metrics, or asks "what do these results mean?"

**Process**:
1. Parse the results (tables, metrics, logs)
2. Analyze:
   - Are results as expected? Better/worse?
   - Statistical significance (if applicable)
   - Comparison to baselines
   - What the results imply for the research hypothesis
3. Suggest next experiments or adjustments
4. If results are significant, suggest `progress.capture`

**Inputs**: Experiment results (any format)
**Outputs**: Analysis report (inline)
**Token**: ~3-8K
**Composition**: Good results → suggest `writing.draft` for results section. Bad results → suggest `decision.analyze` for next direction
