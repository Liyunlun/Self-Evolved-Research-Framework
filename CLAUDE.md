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
| Code skills (TDD, review, commit, debug) | `.claude/skills/code/SKILL.md` |

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
