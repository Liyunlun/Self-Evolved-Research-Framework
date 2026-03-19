# Skills — Micro-Skill Specifications + TD-NL Evolution

`micro/` contains the behavioral specs for all SER micro-skills.
These are NOT code — they are structured natural language specifications
that define trigger conditions, processes, inputs/outputs, and composition rules.

`td-nl/` contains the skill evolution infrastructure. The micro-skill specs
in `micro/` are the **optimization target** — TD-NL improves them over time
based on accumulated usage feedback.

## Skill Index

| File | Skills | Purpose |
|------|--------|---------|
| `micro/session.md` | session.open, session.close | Conversation lifecycle |
| `micro/paper.md` | paper.read, paper.compare, paper.index, **lit.search** | Paper reading, analysis & literature search |
| `micro/theory.md` | theory.formalize, .decompose, .search, .counterexample, .generalize | Theory development |
| `micro/proof.md` | proof.critique, .fix, .formalize, .verify, **proof.write** | Proof management & writing |
| `micro/writing.md` | writing.outline†, .draft†, .review, .polish, **paper.figure**, **paper.compile** | Paper writing, figures & compilation |
| `micro/planning.md` | plan.suggest, .milestone, progress.capture, status.report, decision.analyze, experiment.analyze† | Project planning |
| `micro/experiment.md`* | experiment.plan, experiment.analyze†, **math.dse**, [experiment.run, experiment.monitor]‡ | Experiment lifecycle |
| `micro/idea.md` | idea.discover†, idea.verify†, **idea.refine** | Idea generation, refinement & novelty check |
| `micro/visual.md` | **pixel.create**, **paper.illustrate** | Visual creation (pixel art, diagrams) |
| `micro/checklist.md` | checklist.create†, .verify†, .update, .status† | Hierarchical checklist engine (core) |
| `micro/meta.md` | evolve.suggest, evolve.apply, general.research | TD-NL skill evolution |
| `micro/research.md` | research.explore, design.converge | Open-ended research |
| `micro/memory.md` | memory.write†, .retrieve†, .consolidate†, .forget† | Memory operations (config.yaml parameterized) |
| `micro/integrate.md` | project.integrate | Framework onboarding |

**Bold** = SER dev new skill | † = SER dev enhanced | * = assembled from base+local/ms at setup

‡ `experiment.run` and `experiment.monitor` only available in Local mode.
  MetaScheduler mode replaces them with MetaScheduler interaction protocol.

**Note**: Checklist is the core engine — all skills chain to `checklist.update` after completion.

## How Skills Work

1. User message arrives → CLAUDE.md intent router matches a pattern
2. Before executing, the agent MUST `Read` the relevant `micro/*.md` file
3. The spec defines the exact process, not just a summary
4. After execution, a G2 assessment is appended to `td-nl/feedback-log.md`
5. At session.close, `evolve.suggest` aggregates feedback and updates skill values
6. On sufficient signal, spec edit proposals are generated for user approval

## TD-NL Evolution Infrastructure

```
td-nl/
  feedback-log.md       # G2 entries (per-firing) + processed cycles
  value-function.md     # V^L: global skill system assessment
  skill-values/         # Q^L per skill (created on first firing)
    _template.md        # Template for new skill value files
  history/              # Spec version archive (pre-edit snapshots for rollback)
```

See `micro/meta.md` for the full G2 → G1 → evolve.suggest → evolve.apply process.
