# SER dev — Behavioral Protocol

> Self-Evolved Research: A behavior-driven research collaboration framework.
> All skills trigger automatically via intent detection — no explicit commands needed.

> **Self-Evolving Principle**: The framework improves its own micro-skills through use.
> Every skill execution generates feedback (G2). At session.close, feedback is aggregated (G1)
> and used to propose spec edits via natural language TD learning. The skills you use today
> become better tomorrow.

## Enforcement Priority

**ABSOLUTE RULE — SESSION.OPEN FIRST**: At conversation start, `session.open` MUST
execute BEFORE any other processing, skill evaluation, or response — including
clarifying questions, brainstorming checks, or external skill hooks. No exceptions.

SER micro-skills take precedence over external skill systems for research tasks.
External skills (brainstorming, claudeception) remain active for their domains
but do NOT override SER intent routing.

## Session Protocol

### Conversation Start → `session.open`

At the start of each conversation, **silently execute** the following steps, then output a status banner:

1. Read: `config.yaml` + the most recent `logs/digest/*.yaml` + `logs/digest/SUMMARY.md`
2. Read: `memory/MEMORY.md` (always-loaded memory index)
3. Execute `memory.retrieve`: load active context and relevant memories
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
`skills/td-nl/feedback-log.md`. See `skills/micro/meta.md § G2` for format.
This is automatic and costs ~100-200 tokens per skill firing.

### Conversation End → `session.close`

When the conversation is about to end:
1. Generate a summary (1-3 key points + decisions + file changes). **Record all user text input.**
2. Execute `memory.write` → `memory.consolidate`
3. Execute `evolve.suggest` (G1 aggregation + optional spec edit proposal)
4. Update `memory/MEMORY.md`
5. Ask: "Save session log? [Y/edit]"
6. Write to `logs/digest/YYYY-MM-DD.yaml`, update `SUMMARY.md`

---

## Intent Router

Priority matches from top to bottom. Each micro-skill has a detailed spec in `skills/micro/`.
**You MUST Read the spec file before executing** — the table below is a summary only.

| # | Detection Pattern | Micro-Skill | Spec File |
|---|-------------------|-------------|-----------|
| 1 | Conversation start | `session.open` | `skills/micro/session.md` |
| 2 | Conversation end | `session.close` | `skills/micro/session.md` |
| 3 | User discusses/shares a paper | `paper.read` | `skills/micro/paper.md` |
| 4 | Comparing multiple papers | `paper.compare` | `skills/micro/paper.md` |
| 5 | "索引论文", "paper index", organize papers | `paper.index` | `skills/micro/paper.md` |
| 6 | User proposes a theorem/conjecture | `theory.formalize` | `skills/micro/theory.md` |
| 7 | Complex proof decomposition needed | `theory.decompose` | `skills/micro/theory.md` |
| 8 | Stuck on a proof/seeking methods | `theory.search` | `skills/micro/theory.md` |
| 9 | "is this true?", verify a claim, find counterexample | `theory.counterexample` | `skills/micro/theory.md` |
| 10 | "can we generalize?", extend a proven result | `theory.generalize` | `skills/micro/theory.md` |
| 11 | User presents a proof draft, "is this proof correct?" | `proof.critique` | `skills/micro/proof.md` |
| 12 | "写证明", "prove this", prove a theorem | `proof.write` | `skills/micro/proof.md` |
| 13 | Fix proof issues identified by critique | `proof.fix` | `skills/micro/proof.md` |
| 14 | "make this publication-ready", formal LaTeX proof | `proof.formalize` | `skills/micro/proof.md` |
| 15 | Verify a formula, check algebraic step | `proof.verify` | `skills/micro/proof.md` |
| 16 | User requests writing a specific paper section (e.g., "写 introduction") | `writing.draft` | `skills/micro/writing.md` |
| 17 | "写大纲", "paper outline", plan the paper structure | `writing.outline` | `skills/micro/writing.md` |
| 18 | "review paper", "审阅论文", review a draft | `writing.review` | `skills/micro/writing.md` |
| 19 | "polish", "润色", improve writing quality | `writing.polish` | `skills/micro/writing.md` |
| 20 | "画图", "generate figures", paper figures from data | `paper.figure` | `skills/micro/writing.md` |
| 21 | "编译论文", "compile paper", build PDF | `paper.compile` | `skills/micro/writing.md` |
| 22 | User asks "what to do next" | `plan.suggest` | `skills/micro/planning.md` |
| 23 | "when is the deadline?", "are we on track?" | `plan.milestone` | `skills/micro/planning.md` |
| 24 | User asks "project status" | `status.report` | `skills/micro/planning.md` |
| 25 | User reports completing something | `progress.capture` | `skills/micro/planning.md` |
| 26 | Weighing options/making a decision | `decision.analyze` | `skills/micro/planning.md` |
| 27 | Sharing experiment results, "what do these results mean?" | `experiment.analyze` | `skills/micro/planning.md` |
| 28 | "plan experiment", "设计实验", experiment design | `experiment.plan` | `skills/micro/experiment.md` |
| 29 | User asks to run/launch experiment | `experiment.run` | `skills/micro/experiment.md` |
| 30 | User asks to check experiment status | `experiment.monitor` | `skills/micro/experiment.md` |
| 31 | "design space exploration", "DSE", parameter sweep | `math.dse` | `skills/micro/experiment.md` |
| 32 | User asks to brainstorm ideas | `idea.discover` | `skills/micro/idea.md` |
| 33 | User asks "is this idea novel?" | `idea.verify` | `skills/micro/idea.md` |
| 34 | "精炼想法", "refine idea", make idea more concrete | `idea.refine` | `skills/micro/idea.md` |
| 35 | "画像素图", "pixel art", "SVG illustration" | `pixel.create` | `skills/micro/visual.md` |
| 36 | "论文插图", "architecture diagram", "draw the pipeline" | `paper.illustrate` | `skills/micro/visual.md` |
| 37 | User asks to create paper checklist | `checklist.create(category=paper-audit)` | `skills/micro/checklist.md` |
| 38 | User asks to verify paper claims | `checklist.verify` | `skills/micro/checklist.md` |
| 39 | Paper changed, checklist needs sync | `checklist.update` | `skills/micro/checklist.md` |
| 40 | User asks for checklist completion stats | `checklist.status` | `skills/micro/checklist.md` |
| 41 | Open-ended research exploration | `research.explore` | `skills/micro/research.md` |
| 42 | Architecture/design decision | `design.converge` | `skills/micro/research.md` |
| 43 | "找论文", "文献检索", "related work", "search arxiv" | `lit.search` | `skills/micro/paper.md` |
| 44 | "写论文", "开始写", "paper writing" (full paper, not single section) | `checklist.create(category=paper-writing)` | `skills/micro/checklist.md` |
| 45 | "完整流程", "end-to-end", "从头开始研究" | `checklist.create(category=research-pipeline)` | `skills/micro/checklist.md` |
| 46 | User wants to add/track a task | `checklist.create` | `skills/micro/checklist.md` |
| 47 | Other research-related | `general.research` | `skills/micro/meta.md` |

---

## Checklist Engine

The hierarchical checklist is the single source of truth for project progress.

- **L0** (`Checklist.md`): Project root — read at every session.open
- **L1** (`checklists/{term}.md`): Short/mid/long-term phase checklists
- **L2** (`checklists/{term}/{category}-{slug}.md`): Specific task checklists

Items are Leaf (single checkable) or Branch (→ sub-checklist). Completion propagates upward.
Verification stages: `[ ]` → `[x]` (done) → `[v]` (verified) → `[U]` (user signed off).

All skills update the checklist after producing artifacts. See `skills/micro/checklist.md`.

---

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs using natural language TD learning:

1. **G2 (inline)**: After every skill fires → append outcome assessment to feedback log
2. **G1 (session.close)**: `evolve.suggest` aggregates G2 → updates per-skill values → proposes spec edits
3. **Apply (user-triggered)**: `evolve.apply` edits skill specs with version archive + rollback safety

Infrastructure lives in `skills/td-nl/`. See `skills/micro/meta.md` for the full process.

---

## Dual Review

When `config.yaml § dual_review.enabled` is true and the current skill is in the `when` list,
use the MCP tool specified in `config.yaml § dual_review.tool` (default: `mcp__codex__codex`)
to obtain an independent review from an external model (GPT-5.4).

**Process**:
1. Send the artifact (idea, draft, proof, results) to the external model via MCP tool
2. Generate own internal review simultaneously
3. Synthesize: mark consensus (high-confidence feedback) and divergence (flag for user)
4. Report both perspectives with clear attribution

**Applicable skills** (configured in `config.yaml § dual_review.when`):
- `writing.review` — cross-model paper review
- `idea.verify` — external novelty assessment
- `proof.critique` — independent proof checking
- `experiment.analyze` — external interpretation of results

This is a framework **capability**, not a separate skill. Each skill decides internally
whether to invoke the external model based on config and context.

---

## Memory Parameters

All numerical thresholds in `memory.md` operations reference `config.yaml § memory`.
TD-NL can optimize these parameters over time based on accumulated feedback:
- `memory.write.importance_threshold` — minimum importance to persist (default 5)
- `memory.retrieve.weights` — scoring weights for tag/keyword/recency/importance
- `memory.consolidate.episode_threshold` — episodes before consolidation triggers
- `memory.forget.stale_episode_days` — days before stale episode cleanup

See `skills/micro/memory.md` for the full parameterized process.

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
See `skills/micro/memory.md` for write/retrieve/consolidate/forget specs.

---

## Project Architecture

```
├── CLAUDE.md              # Behavioral protocol (this file)
├── Checklist.md           # Project progress root (L0)
├── checklists/            # Hierarchical task tracking
│   ├── short-term.md      # L1 phase checklists (7 category headers)
│   ├── mid-term.md
│   ├── long-term.md
│   └── {term}/{cat}-{slug}.md  # L2 specific tasks
├── config.template.yaml   # Copy to config.yaml and customize
├── README.md / LICENSE
├── skills/
│   ├── CLAUDE.md          # Skill index
│   ├── micro/             # 14 micro-skill spec files (the optimization target)
│   └── td-nl/             # TD-NL skill evolution infrastructure
│       ├── feedback-log.md
│       ├── value-function.md
│       ├── skill-values/   # Per-skill Q^L estimates
│       │   └── _template.md
│       └── history/        # Spec version archive for rollback
├── scripts/               # Utility scripts (citation, notify, analyzer)
├── memory/                # Persistent three-tier memory
│   ├── episodes/          # Episodic memories (recent)
│   ├── topics/            # Consolidated semantic memories
│   └── procedures/        # Permanent procedural memories
├── background/            # Research background materials
├── methodology/           # Research methods + ideas
│   ├── approach.md        # Current research direction (stub created by setup)
│   └── ideas/             # Idea discovery artifacts
├── experiments/           # Experiment code + results
├── paper/                 # Paper artifacts
│   ├── proofs/            # Proof files (proof.write output)
│   ├── theory/            # Theorem statements
│   ├── figures/           # Figures and scripts
│   │   └── scripts/       # Figure generation scripts
│   ├── papers/            # Draft papers
│   └── reviews/           # Review artifacts
├── logs/
│   ├── digest/            # Session logs (YAML + SUMMARY.md)
│   ├── progress/          # Progress capture logs
│   └── experiments/       # Experiment logs
├── outputs/               # Research deliverables
│   ├── visuals/           # SVG/pixel art (pixel.create output)
│   └── paper/             # Paper output artifacts
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
| Skill evolution (evolve.suggest) | 2-4K |
| Skill evolution (evolve.apply) | 2-5K |
| Paper analysis | 3-8K |
| Theory formalization | 3-8K |
| Proof refinement | 3-10K/pass |
| Writing (draft/review/polish) | 2-15K |
| Experiment execution (run + monitor) | 2-4K each |
| Idea discovery + novelty verification | 4-8K + 3-6K |
| Planning & progress | 1-5K |
| Checklist operations | 1-3K |
| Visual creation (pixel/illustrate) | 2-8K |
| Literature search | 2-5K |
| Memory operations | 1-3K |
