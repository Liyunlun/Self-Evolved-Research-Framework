# SER v6 — Self-Evolving Research Framework

> Behavior-driven research collaboration framework with Bayesian self-optimization.
> Skills trigger automatically via model intent detection. No explicit commands needed.

## Session Rule

**ABSOLUTE**: At conversation start, execute `session.open` (see `.claude/skills/meta/SKILL.md`)
BEFORE any other processing. The session-guard hook enforces this.

## Skill Chain Protocol

session.open loads `~/.claude/ser/chains.yaml` and `.claude/.ser-recommendations.json`.

Selecting next action:
1. If active chain → follow chain steps in order
2. If no active chain → match chains.yaml triggers to user intent
3. Multiple chains match → use recommendation scores (if ambiguous flag is set, ask user)
4. No chain matches → read SKILL.md "Suggested Next" for single-step transitions
5. No match at all → use general.research

After every skill execution:
- Record G2 observation (see meta/SKILL.md § G2)
- Update checklist if artifact produced

At session.close:
- Execute evolve.suggest (G1 aggregation)
- Run update_weights.py to persist learning

## Reference Docs

Read these when you need detailed procedures:

| Need to know | Read |
|-------------|------|
| session.open/close full steps | `.claude/skills/meta/SKILL.md` |
| Chain templates and triggers | `~/.claude/ser/chains.yaml` |
| Weight update and learning mechanics | `~/.claude/ser/td-nl/README.md` |
| G2 observation recording format | `.claude/skills/meta/SKILL.md` § G2 |
| External model review process | `.claude/skills/review/SKILL.md` |
| Skill evolution (evolve.suggest/apply) | `.claude/skills/meta/SKILL.md` § evolve |
| Checklist engine full spec | `.claude/skills/checklist/SKILL.md` |

## Checklist Engine

Hierarchical checklist is the single source of truth for project progress.

- **L0** (`Checklist.md`): Project root — read at every session.open
- **L1** (`checklists/{term}.md`): Short/mid/long-term phase checklists
- **L2** (`checklists/{term}/{category}-{slug}.md`): Specific task checklists

Items: Leaf (`- [ ] {desc}`) or Branch (`- [3/7] {desc} → path`).
Stages: `[ ]` → `[x]` (done) → `[v]` (verified) → `[U]` (blocked).
Categories: Ideas, Methods, Experiments, Paper-Audit, Review-Loop, Paper-Writing, Research-Pipeline.

All skills update the checklist after producing artifacts. See `.claude/skills/checklist/SKILL.md`.

## Data Contracts

### Log Format: `logs/digest/YYYY-MM-DD.yaml`

````yaml
date: "YYYY-MM-DD"
type: "session"
summary: "{1-line}"
accomplishments:
  - type: "{paper_read|experiment|proof|code|decision}"
    content: "{description}"
decisions: []
files_changed: []
milestone_phase: "{phase}"
````

### Observation Format: `logs/observations/{session}.jsonl`

````jsonl
{"type":"tool","tool":"Read","file":"paper/intro.md","duration_ms":120,"ts":"..."}
{"type":"skill","skill":"paper.read","chain":"literature_survey","step":2,"ts":"..."}
{"type":"transition","from":"paper.read","to":"paper.compare","suggested":true,"ts":"..."}
{"type":"checkpoint","chain":"literature_survey","at":"after_paper.read","user_interrupted":false,"ts":"..."}
````

### Paper Notes: `resources/papers/{ID}.md`

YAML frontmatter: title, authors, year, venue, relevance, tags, read_date.
Structure: Quick Reference → Background → Pain Points → Method → Experiments → Conclusion → Questions → Personal Notes.
Reading rule: Read Quick Reference first. Only read full document if deeper understanding needed.

### Checklist Items

Leaf: `- [ ] {description}`
Branch: `- [3/7] {description} → checklists/{path}.md`
With artifact: `- [x] {description} | artifact: outputs/{path}`

### Memory: `memory/`

Three-tier: episodes/ (20 max, 7d) → topics/ (50 max, 90d) → procedures/ (100 max, permanent).
MEMORY.md: always-loaded index (200-line hard limit).
See `.claude/skills/memory/SKILL.md`.

## Project Structure

```
├── CLAUDE.md                    # This file — framework protocol
├── Checklist.md                 # Project progress root (L0)
├── config.yaml                  # Project configuration
├── .claude/
│   ├── settings.json            # Hook configuration
│   └── skills/                  # Grouped skill specs (v6)
│       ├── paper/SKILL.md       # paper.read, compare, index, lit.search
│       ├── theory/SKILL.md      # theory.formalize, decompose, search, counterexample, generalize
│       ├── proof/SKILL.md       # proof.critique, write, fix, formalize, verify
│       ├── writing/SKILL.md     # writing.outline, draft, review, polish, figure, compile
│       ├── planning/SKILL.md    # plan.suggest, milestone, progress, status, decision, experiment.analyze
│       ├── experiment/SKILL.md  # experiment.plan, run, monitor, math.dse
│       ├── idea/SKILL.md        # idea.discover, verify, refine
│       ├── visual/SKILL.md      # pixel.create, paper.illustrate
│       ├── checklist/SKILL.md   # checklist.create, verify, update, status
│       ├── research/SKILL.md    # research.explore, design.converge
│       ├── memory/SKILL.md      # memory.write, retrieve, consolidate, forget
│       ├── review/SKILL.md      # dual_review (external model)
│       └── meta/SKILL.md        # session.open/close, G2, evolve, general.research
├── checklists/                  # Hierarchical task tracking (L1 + L2)
├── memory/                      # Three-tier persistent memory
│   ├── MEMORY.md                # Always-loaded index
│   ├── episodes/                # Recent (20 max, 7d)
│   ├── topics/                  # Consolidated (50 max, 90d)
│   └── procedures/              # Permanent (100 max)
├── logs/
│   ├── digest/                  # Session logs (YAML + SUMMARY.md)
│   ├── observations/            # JSONL observation data (per session)
│   ├── progress/                # Progress capture logs
│   └── experiments/             # Experiment logs
├── methodology/                 # Research direction + ideas
├── experiments/                 # Experiment code + results
├── paper/                       # Paper artifacts (proofs, theory, figures, drafts, reviews)
├── outputs/                     # Research deliverables
├── resources/                   # Reference materials (papers, repos)
├── background/                  # Background research
├── scripts/                     # Utility scripts
└── docs/                        # Supporting documentation
```

### Global Infrastructure (shared across all SER projects)

```
~/.claude/ser/
├── hooks/                       # session-guard.sh, observe.sh
├── scripts/                     # recommend.py, update_weights.py
├── chains.yaml                  # Chain templates
├── weights.yaml                 # Bayesian transition weights
├── config.yaml                  # Learning parameters
└── td-nl/README.md              # System documentation
```
