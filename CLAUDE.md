# SER v5.0 — Behavioral Protocol

> Self-Evolved Research: A behavior-driven research collaboration framework.
> All skills trigger automatically via intent detection — no explicit commands needed.

> **Self-Evolving Principle**: The framework improves its own micro-skills through use.
> Every skill execution generates feedback (G2). At session-close, feedback is aggregated (G1)
> and used to propose spec edits via natural language TD learning. The skills you use today
> become better tomorrow.

## Enforcement Priority

**ABSOLUTE RULE — SESSION-OPEN FIRST**: At conversation start, `session-open` MUST
execute BEFORE any other processing, skill evaluation, or response — including
clarifying questions, brainstorming checks, or external skill hooks. No exceptions.

SER micro-skills take precedence over external skill systems for research tasks.
External skills (brainstorming, claudeception) remain active for their domains
but do NOT override SER intent routing.

## Session Protocol

### Conversation Start → `session-open`

At the start of each conversation, **silently execute** the following steps, then output a status banner:

1. Read: `config.yaml` + the most recent `logs/digest/*.yaml` + `logs/digest/SUMMARY.md`
2. Read: `memory/MEMORY.md` (always-loaded memory index)
3. Execute `memory-retrieve`: load active context and relevant memories
4. Read: `Checklist.md` (project progress root)
5. Output:
   ```
   [SER] {project_name} | Phase {X} | [{done}/{total} items] | V^L={overall}/10
   Last session ({date}): {1-line summary}
   Next milestone: {goal} ({days}d)
   ```
6. If milestone ≤3 days away: append `** MILESTONE APPROACHING **`
7. Proceed directly to the user's request without asking questions

### During Session → G2 Inline Assessment

After EVERY micro-skill execution, silently append a G2 feedback entry to
`skills/td-nl/feedback-log.md`. See `skills/_shared/evolve-cycle.md § G2` for format.
This is automatic and costs ~100-200 tokens per skill firing.

### Conversation End → `session-close`

When the conversation is about to end:
1. Generate a summary (1-3 key points + decisions + file changes). **Record all user text input.**
2. Execute `memory-write` → `memory-consolidate`
3. Execute `evolve-suggest` (G1 aggregation + optional spec edit proposal)
4. Update `memory/MEMORY.md`
5. Ask: "Save session log? [Y/edit]"
6. Write to `logs/digest/YYYY-MM-DD.yaml`, update `SUMMARY.md`

---

## Intent Router

Priority matches from top to bottom. Each SER skill lives in its own directory
under `skills/{skill-name}/` with a standard `SKILL.md`, so Claude Code auto-loads
the body when the skill fires; the router below describes *why* and *when* a skill
should be chosen.

| # | Detection Pattern | Skill |
|---|-------------------|-------|
| 1 | Conversation start | `session-open` |
| 2 | Conversation end | `session-close` |
| 3 | User discusses/shares a paper | `paper-read` |
| 3b | User wants to deeply study a paper ("understand", "study", "Fey-R") | `paper-read` (Deep/Fey-R mode) → `fey-r` |
| 4 | Comparing multiple papers | `paper-compare` |
| 5 | User proposes a theorem/conjecture | `theory-formalize` |
| 6 | User presents a proof draft | `proof-critique` |
| 7 | User requests writing a paper section | `writing-draft` |
| 8 | User asks "what to do next" | `plan-suggest` (reads the checklist tree) |
| 9 | User asks "project status" | `status-report` / `checklist-status` |
| 10 | User reports completing something | `progress-capture` |
| 11 | Complex proof decomposition needed | `theory-decompose` |
| 12 | Stuck on a proof / seeking methods | `theory-search` |
| 13 | Weighing options / making a decision | `decision-analyze` |
| 14 | Sharing experiment results | `experiment-analyze` |
| 15 | User asks to run / launch experiment | `experiment-run` |
| 16 | User asks to check experiment status | `experiment-monitor` |
| 17 | User asks to brainstorm ideas | `idea-discover` |
| 18 | User asks "is this idea novel?" | `idea-verify` |
| 19 | User asks to create a paper checklist | `checklist-create` (uses paper audit template) |
| 20 | User asks to verify paper claims | `checklist-verify` |
| 21 | Paper changed, checklist needs sync | `checklist-update` |
| 22 | Open-ended research exploration | `research-explore` |
| 23 | Architecture/design decision | `design-converge` |
| 24 | Other research-related (fallback) | `general-research` |
| 25 | User wants to add/track a task | `checklist-create` |
| 26 | User asks to start a branch / isolate work / create a worktree | `code-branch` |
| 27 | Medium/large coding task needing a plan before writing code | `code-roadmap` |
| 28 | User asks to implement / add feature / change code behavior | `code-implement` |
| 29 | Test fails / bug reported / unexpected behavior | `code-debug` |
| 30 | Review code changes after implementation | `code-review` |
| 31 | Commit reviewed code changes | `code-commit` |
| 32 | User asks for architecture/pipeline/flow diagram for a paper | `paper-illustrate` |
| 33 | User asks for pixel art / project mascot / README hero / decorative SVG | `paper-art` |
| 34 | User asks to compile the paper / build PDF / "编译论文" | `paper-compile` |
| 35 | User asks to generate a data plot / bar chart / heatmap / table — or chained after `experiment-analyze` | `paper-figure` |

---

## Checklist Engine

The hierarchical checklist is the single source of truth for project progress.

- **L0** (`Checklist.md`): Project root — read at every session-open
- **L1** (`checklists/{term}.md`): Short/mid/long-term phase checklists
- **L2** (`checklists/{term}/{category}-{slug}.md`): Specific task checklists

Items are Leaf (single checkable) or Branch (→ sub-checklist). Completion propagates upward.
Verification stages: `[ ]` → `[x]` (done) → `[v]` (verified) → `[U]` (user signed off).

All skills update the checklist after producing artifacts. The engine's shared
vocabulary (tree, markers, composition rules, paper audit template) lives in
`skills/_shared/checklist-engine.md`; the 4 operation skills are
`checklist-create`, `checklist-verify`, `checklist-update`, `checklist-status`.

---

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs using natural language TD learning:

1. **G2 (inline)**: After every skill fires → append outcome assessment to feedback log
2. **G1 (session-close)**: `evolve-suggest` aggregates G2 → updates per-skill values → proposes spec edits
3. **Apply (user-triggered)**: `evolve-apply` edits skill specs with version archive + rollback safety

Infrastructure lives in `skills/td-nl/`. See `skills/_shared/evolve-cycle.md` for the full process.

---

## Data Contracts

### Log Format: `logs/digest/YYYY-MM-DD.yaml`

```yaml
date: "YYYY-MM-DD"
type: "session"          # session | progress | review
summary: "{1-line}"
accomplishments:
  - type: "{paper_read|experiment|proof|code|decision}"
    content: "{description}"
decisions: []
files_changed: []
token_estimate: N
milestone_phase: "{phase}"
```

### Paper Notes: `resources/papers/{ID}.md`

```yaml
---
title: "{title}"
authors: ["{author}"]
year: YYYY
venue: "{venue}"
relevance: "{high|medium|low}"
tags: []
read_date: "YYYY-MM-DD"
---
```

**Structure**: Quick Reference (first) → Background, Pain Points, Method, Experiments, Conclusion, Questions, Personal Notes.

**Reading rule**: Read only Quick Reference first. Only read the full document if deeper understanding is needed.

### Checklist Items

Leaf: `- [ ] {description}`
Branch: `- [3/7] {description} → checklists/{path}.md`
With artifact: `- [x] {description} | artifact: outputs/{path}`

### Memory System: `memory/`

Three-tier persistent memory. See `memory/CLAUDE.md` for structure and capacity limits.
See `skills/_shared/memory-tiers.md` for tier definitions; the 4 operation skills
are `memory-write`, `memory-retrieve`, `memory-consolidate`, `memory-forget`.

---

## Project Architecture

```
├── CLAUDE.md              # Behavioral protocol (this file)
├── Checklist.md           # Project progress root (L0)
├── checklists/            # Hierarchical task tracking
│   ├── short-term.md      # L1 phase checklists
│   ├── mid-term.md
│   ├── long-term.md
│   └── {term}/{cat}-{slug}.md  # L2 specific tasks
├── config.template.yaml   # Copy to config.yaml and customize
├── README.md / LICENSE
├── skills/
│   ├── CLAUDE.md          # Skill index
│   ├── {skill-name}/      # 52 SER skills, each with SKILL.md + YAML frontmatter
│   │   └── SKILL.md       # Auto-loaded by Claude Code when the skill fires
│   ├── _shared/           # Cross-cutting infra read by related skills
│   │   ├── checklist-engine.md
│   │   ├── memory-tiers.md
│   │   └── evolve-cycle.md
│   ├── external/          # External skills (git submodules)
│   │   └── fey-r/         # Feynman-method paper reading
│   └── td-nl/             # TD-NL skill evolution infrastructure
│       ├── feedback-log.md
│       ├── value-function.md
│       ├── skill-values/   # Per-skill Q^L estimates
│       └── history/        # Spec version archive for rollback
├── scripts/               # Utility scripts (citation, notify, analyzer, install-skills)
├── memory/                # Persistent three-tier memory
│   ├── episodes/          # Episodic memories (recent)
│   ├── topics/            # Consolidated semantic memories
│   └── procedures/        # Permanent procedural memories
├── background/            # Research background materials
├── methodology/           # Research methods + ideas
├── experiments/           # Experiment code + results
├── logs/digest/           # Session logs
├── outputs/               # Research deliverables (short/mid/long-term + paper/)
├── resources/             # Reference materials
│   ├── papers/            # Paper reading notes
│   └── repos/             # Cloned reference repositories
└── docs/                  # Plans, reports, process docs
```

## Token Budget

| Operation | Cost |
|-----------|------|
| Session lifecycle (open + close) | ~2-4K |
| G2 inline assessment (per skill firing) | ~100-200 |
| Skill evolution (evolve-suggest) | 2-4K |
| Skill evolution (evolve-apply) | 2-5K |
| Paper analysis | 3-8K |
| Theory formalization | 3-8K |
| Proof refinement | 3-10K/pass |
| Writing (draft/review/polish) | 2-15K |
| Experiment execution (run + monitor) | 2-4K each |
| Idea discovery + novelty verification | 4-8K + 3-6K |
| Planning & progress | 1-5K |
| Memory operations | 1-3K |
