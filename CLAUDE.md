# SER v6 — Self-Evolving Research Framework

> Behavior-driven research collaboration framework with Bayesian self-optimization.
> Skills trigger automatically via model intent detection. No explicit commands needed.

## Session Rule

**ABSOLUTE**: At conversation start, execute `session.open` (see `.claude/skills/meta/SKILL.md`)
BEFORE any other processing. The session-guard hook enforces this.

## Skill Execution Loop

**MANDATORY**: Every user request MUST be routed through this table.
Identify the matching skill first, then execute through the skill process.

### Step 1: Route — match user intent to skill

| User Intent | Skill | Required Output | → Next |
|-------------|-------|----------------|--------|
| Read/understand paper or code | paper.read | `papers/{ID}.md` (full) or key findings (quick) | paper.compare |
| Compare methods/systems | paper.compare | comparison table (inline) | decision.analyze |
| Search literature | lit.search | search results | paper.read |
| Explore research directions | research.explore | ranked directions (inline) | design.converge |
| New idea to develop | idea.discover | idea card (inline) | idea.verify |
| Decision between options | decision.analyze | criteria matrix + recommendation | progress.capture |
| Plan next steps | plan.suggest | prioritized task list | → route |
| Define theory/formalize | theory.formalize | formalized statement | proof.critique |
| Design experiment | experiment.plan | `experiments/{name}/plan.md` | experiment.run |
| Analyze results | experiment.analyze | result summary + figures | decision.analyze |
| Implement code | code.implement | tests + code | code.review |
| Debug a problem | code.debug | root cause + fix | code.review |
| Review code | code.review | issue list with severity | code.commit |
| Commit code | code.commit | clean commit | — |
| Write paper section | writing.draft | draft section in `paper/` | writing.review |
| Review draft | writing.review | revision notes | writing.polish |
| No match | general.research | context-aware response | — |

Pick the most specific match. If ambiguous, ask user.

### Step 2: Execute

Follow the skill's process. Full spec: `.claude/skills/{group}/SKILL.md` (read for complex cases).

### Step 3: Record

After each skill, append to `logs/observations/YYYY-MM-DD.jsonl`:
````jsonl
{"type":"skill","skill":"{name}","chain":"{active_chain|null}","outcome":"{better|as_expected|worse}","ts":"{ISO8601}"}
````

### Step 4: Chain

Follow → Next column. If active chain (from `~/.claude/ser/chains.yaml`), follow chain steps in order.
Stop when user's request is fully answered.

At session.close: execute `evolve.suggest` (G1 aggregation) + run `update_weights.py`.

## Reference Docs

| Need to know | Read |
|-------------|------|
| session.open/close steps | `.claude/skills/meta/SKILL.md` |
| Skill full process specs | `.claude/skills/{group}/SKILL.md` |
| Chain templates and triggers | `~/.claude/ser/chains.yaml` |
| Skill evolution | `.claude/skills/meta/SKILL.md` § evolve |

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

### Observation Format: `logs/observations/YYYY-MM-DD.jsonl`

````jsonl
{"type":"tool","phase":"pre","tool":"Read","ts":"..."}
{"type":"skill","skill":"paper.read","chain":"literature_survey","outcome":"as_expected","ts":"..."}
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

## Git Discipline

All code is held to the same standard. No distinction between experiment and framework code.

### Commit Protocol
- **Review before commit**: Run `code.review` (dual-layer) → fix issues → `code.commit`
- **Prefix convention**: `feat:` `fix:` `exp:` `refactor:` `docs:` `chore:`
- **Never commit**: `.claude/`, `logs/`, `memory/episodes/`, secrets (.env, credentials)
- **Stage explicitly**: Name files, never `git add -A`

### State Backup
- `ser-state` orphan branch: daily cron backup of Checklist.md, checklists/, memory/MEMORY.md, memory/topics/, memory/procedures/
- Uses `git worktree` — main working directory unaffected
- Script: `scripts/ser-state-backup.sh`

## Code Discipline (from ECC Philosophy)

### Core Rules
1. **Test-First (Rigid)**: Write tests before code. RED-GREEN-REFACTOR. No exceptions. (`superpowers:test-driven-development`)
2. **Systematic Debugging**: 4-phase root cause analysis. 3+ fix failures → question architecture. (`superpowers:systematic-debugging`)
3. **Evidence over Claims**: Verify before claiming completion. IDENTIFY→RUN→READ→VERIFY→CLAIM. (`superpowers:verification-before-completion`)
4. **Simplicity / YAGNI**: Minimize complexity. Don't design for hypothetical requirements.
5. **1% Rule**: If any code skill might be relevant, invoke it. Don't rationalize.

### Skill Priority
When code skills and research skills both apply:
1. **Process skills first** (debug, TDD) — determine HOW to approach
2. **Domain skills second** (experiment, paper) — determine WHAT to build
3. If even 1% chance a skill applies, invoke it

### Red Flags (STOP when you think these)

| Thought | Reality |
|---------|---------|
| "This is just simple code" | Simple things become complex. Use TDD. |
| "I'll test after" | Tests written after pass immediately, prove nothing. |
| "Should work now" | Not verification. Run the command, read output. |
| "Too simple for review" | All code gets reviewed. No exceptions. |
| "Let me explore first" | Skills tell you HOW to explore. Invoke first. |
| "3+ fixes failed, let me try once more" | Architecture problem. Stop and discuss. |

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
│       ├── code/SKILL.md         # code.implement, debug, review, verify, commit, branch
│       ├── review/SKILL.md      # dual_review (external model)
│       └── meta/SKILL.md        # session.open/close, G2, evolve, general.research
├── src/                         # Project source code (unified location)
├── experiments/                 # Per-experiment directories (→ see experiment/SKILL.md)
│   └── {name}/plan.md          # Claims, configs, ablations, resources, commit ID
│   └── {name}/run.sh           # Experiment launch script
│   └── {name}/results/         # Raw output files
├── resources/                   # External references — read-only (→ resources/README.md)
│   ├── papers/                  # Paper notes (YAML frontmatter; Quick Ref first)
│   ├── repos/                   # Cloned reference repos (--depth 1)
│   └── docs/                    # Plans, reports, process documents
├── paper/                       # Paper writing artifacts
│   ├── figures/ + scripts/      # Figures and generation scripts
│   ├── papers/                  # Draft versions (.tex)
│   ├── proofs/                  # Mathematical proofs
│   ├── reviews/                 # Reviewer feedback
│   └── theory/                  # Theoretical analysis
├── outputs/                     # Verified deliverables (→ outputs/README.md)
│   ├── short_term/              # Notes, summaries, preliminary analyses
│   ├── mid_term/                # Draft sections, experiment reports
│   ├── long_term/               # Complete papers, dissertations
│   ├── paper/                   # Compiled paper PDF
│   └── visuals/                 # Visualizations
├── background/                  # Survey and landscape analysis (→ background/README.md)
├── methodology/                 # Research direction + ideas (→ methodology/README.md)
│   ├── approach.md              # Current methodology
│   └── ideas/                   # Idea discovery artifacts (YYYY-MM-DD-discovery.md)
├── checklists/                  # Hierarchical task tracking L1+L2 (→ checklists/README.md)
├── memory/                      # Three-tier persistent memory (→ memory/README.md)
│   ├── MEMORY.md                # Always-loaded index (200-line limit)
│   ├── episodes/                # Recent (20 max, 7d)
│   ├── topics/                  # Consolidated (50 max, 90d)
│   └── procedures/              # Permanent (100 max)
├── logs/                        # Session infrastructure (→ logs/README.md)
│   ├── digest/                  # Session YAML + SUMMARY.md
│   ├── observations/            # Hook JSONL (observe.sh)
│   ├── progress/                # Progress snapshots
│   └── experiments/             # Experiment runtime logs (stdout/stderr)
├── scripts/                     # Utility scripts (→ scripts/README.md)
└── refine-logs/                 # Proposal iteration history (dual_review)
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
