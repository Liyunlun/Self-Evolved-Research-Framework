# SER v5.0 — Behavioral Protocol

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
4. Output:
   ```
   [SER] {project_name} | Phase {X} | Token: {used}/{total} ({pct}%)
   Last session ({date}): {1-line summary}
   Next milestone: {goal} ({days}d)
   [MEM] {N} memories | [TD-NL] V^L={overall}/10
   ```
5. If milestone ≤3 days away: append `** MILESTONE APPROACHING **`
6. Proceed directly to the user's request without asking questions

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
| 5 | User proposes a theorem/conjecture | `theory.formalize` | `skills/micro/theory.md` |
| 6 | User presents a proof draft | `proof.critique` | `skills/micro/proof.md` |
| 7 | User requests writing a paper section | `writing.draft` | `skills/micro/writing.md` |
| 8 | User asks "what to do next" | `plan.suggest` | `skills/micro/planning.md` |
| 9 | User asks "project status" | `status.report` | `skills/micro/planning.md` |
| 10 | User reports completing something | `progress.capture` | `skills/micro/planning.md` |
| 11 | Complex proof decomposition needed | `theory.decompose` | `skills/micro/theory.md` |
| 12 | Stuck on a proof/seeking methods | `theory.search` | `skills/micro/theory.md` |
| 13 | Weighing options/making a decision | `decision.analyze` | `skills/micro/planning.md` |
| 14 | Sharing experiment results | `experiment.analyze` | `skills/micro/planning.md` |
| 15 | User asks to run/launch experiment | `experiment.run` | `skills/micro/experiment.md` |
| 16 | User asks to check experiment status | `experiment.monitor` | `skills/micro/experiment.md` |
| 17 | User asks to brainstorm ideas | `idea.discover` | `skills/micro/idea.md` |
| 18 | User asks "is this idea novel?" | `idea.verify` | `skills/micro/idea.md` |
| 19 | User asks to create paper checklist | `checklist.generate` | `skills/micro/checklist.md` |
| 20 | User asks to verify paper claims | `checklist.verify` | `skills/micro/checklist.md` |
| 21 | Paper changed, checklist needs sync | `checklist.update` | `skills/micro/checklist.md` |
| 22 | Open-ended research exploration | `research.explore` | `skills/micro/research.md` |
| 23 | Architecture/design decision | `design.converge` | `skills/micro/research.md` |
| 24 | Other research-related | `general.research` | `skills/micro/meta.md` |

---

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs using natural language TD learning:

1. **G2 (inline)**: After every skill fires → append outcome assessment to feedback log
2. **G1 (session.close)**: `evolve.suggest` aggregates G2 → updates per-skill values → proposes spec edits
3. **Apply (user-triggered)**: `evolve.apply` edits skill specs with version archive + rollback safety

Infrastructure lives in `skills/td-nl/`. See `skills/micro/meta.md` for the full process.

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

### Memory System: `memory/`

Three-tier persistent memory. See `memory/CLAUDE.md` for structure and capacity limits.
See `skills/micro/memory.md` for write/retrieve/consolidate/forget specs.

---

## Project Architecture

```
├── CLAUDE.md              # Behavioral protocol (this file)
├── config.template.yaml   # Copy to config.yaml and customize
├── README.md / LICENSE
├── skills/
│   ├── CLAUDE.md          # Skill index
│   ├── micro/             # 12 micro-skill spec files (the optimization target)
│   └── td-nl/             # TD-NL skill evolution infrastructure
│       ├── feedback-log.md
│       ├── value-function.md
│       ├── skill-values/   # Per-skill Q^L estimates
│       └── history/        # Spec version archive for rollback
├── scripts/               # Utility scripts (citation, notify, analyzer)
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
| Skill evolution (evolve.suggest) | 2-4K |
| Skill evolution (evolve.apply) | 2-5K |
| Paper analysis | 3-8K |
| Theory formalization | 3-8K |
| Proof refinement | 3-10K/pass |
| Writing (draft/review/polish) | 2-15K |
| Experiment execution (run + monitor) | 2-4K each |
| Idea discovery + novelty verification | 4-8K + 3-6K |
| Planning & progress | 1-5K |
| Memory operations | 1-3K |
