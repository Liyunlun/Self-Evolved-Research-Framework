# SER — Self-Evolved Research

> A behavior-driven research framework for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).
> Skills trigger automatically. The framework improves its own skills through use.

## What It Does

You talk naturally. SER detects your intent and routes to the right micro-skill:

| You say | SER triggers |
|---------|-------------|
| "I'm reading this paper..." | `paper.read` — structured notes |
| "Is this proof correct?" | `proof.critique` — step-by-step check |
| "What should I do next?" | `plan.suggest` — prioritized tasks |
| "Run the experiment" | `experiment.run` — launch + monitoring |
| "Any novel ideas for X?" | `idea.discover` → `idea.verify` |
| "Write the introduction" | `writing.draft` — section draft |
| (end conversation) | `session.close` — auto-saves summary |

Every skill execution generates feedback. Over sessions, SER proposes improvements
to its own skill specs via natural language TD learning — the skills you use today
become better tomorrow.

## Getting Started

### 1. Clone

```bash
git clone https://github.com/Shiien/Self-Evolved-Research-Framework.git
cd Self-Evolved-Research-Framework
```

### 2. Run Setup

```bash
bash scripts/setup.sh
```

This creates `config.yaml`, initializes the memory system, and sets up all required directories. Safe to run multiple times.

### 3. Configure Your Project

Edit `config.yaml` with your project details:

```yaml
project:
  name: "Your Research Project"
  status: "phase-0-exploration"
  created_at: "2026-03-19"

research:
  domain: "Your Domain"
  sub_domain: "Your Sub-Domain"
  keywords: [...]
```

### 4. Start Working

```bash
claude
```

SER will automatically:
1. Read your config and memory (`session.open`)
2. Show a status banner
3. Wait for your research request — no commands needed

## Micro-Skills (24)

| Category | Skills | Purpose |
|----------|--------|---------|
| **Session** | `session.open`, `.close` | Lifecycle: status banner, auto-save |
| **Paper** | `paper.read`, `.compare`, `.index` | Reading & analysis |
| **Theory** | `theory.formalize`, `.decompose`, `.search`, `.counterexample`, `.generalize` | Formalization & proof strategy |
| **Proof** | `proof.critique`, `.fix`, `.formalize`, `.verify` | Verification & correction |
| **Writing** | `writing.outline`, `.draft`, `.review`, `.polish` | Paper authoring |
| **Planning** | `plan.suggest`, `.milestone`, `progress.capture`, `status.report`, `decision.analyze`, `experiment.analyze` | Project management |
| **Experiment** | `experiment.run`, `.monitor` | Experiment dispatch |
| **Idea** | `idea.discover`, `.verify` | Gap analysis + novelty check |
| **Checklist** | `checklist.generate`, `.verify`, `.update` | Paper audit & claim tracking |
| **Research** | `research.explore`, `design.converge` | Open-ended exploration |
| **Memory** | `memory.write`, `.retrieve`, `.consolidate`, `.forget` | Persistent cross-session memory |
| **Meta** | `evolve.suggest`, `.apply` | TD-NL skill self-improvement |

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs through natural language TD learning:

```
skill fires → G2 assessment (was it useful?) → accumulate over sessions
                                                        ↓
session.close → G1 aggregation → per-skill value update → spec edit proposal
                                                        ↓
                                    user approves → evolve.apply → rollback if quality drops
```

The optimization target is the skill specs themselves (`skills/micro/*.md`).
Version history in `skills/td-nl/history/` enables safe rollback.

## Project Structure

```
├── CLAUDE.md              # Behavioral protocol (intent router + data contracts)
├── config.template.yaml   # Copy to config.yaml and customize
├── README.md / LICENSE
├── skills/
│   ├── micro/             # 12 micro-skill spec files (optimization target)
│   └── td-nl/             # Skill evolution infrastructure
│       ├── feedback-log.md
│       ├── value-function.md
│       ├── skill-values/   # Per-skill Q^L estimates
│       └── history/        # Spec version archive for rollback
├── scripts/               # Utility scripts (citation, notify, analyzer)
├── memory/                # Persistent three-tier memory
│   ├── episodes/          # Recent observations (7-day retention)
│   ├── topics/            # Consolidated knowledge (90-day)
│   └── procedures/        # Permanent processes
├── background/            # Research background materials
├── methodology/           # Research methods + ideas
├── experiments/           # Experiment code + results
├── outputs/               # Deliverables (short/mid/long-term + paper/)
├── resources/             # Reference materials (papers/ + repos/)
├── logs/digest/           # Session logs
└── docs/                  # Plans, reports
```

## How CLAUDE.md Works

SER is driven by `CLAUDE.md` — a behavioral protocol that Claude Code reads automatically.
It defines:

- **Intent router**: 24 patterns that map your messages to micro-skills
- **Session lifecycle**: auto-open/close with memory persistence
- **Data contracts**: standardized formats for logs, paper notes, memory files
- **Evolution loop**: G2/G1 feedback cycle for skill improvement

Each subdirectory has its own `CLAUDE.md` with scoped context for that area.
The root `CLAUDE.md` is the bootloader; subdirectory files are namespace guides.

## Typical Workflows

### Daily Research

```
(open claude)
→ session.open shows status banner

"I want to continue reading the LAPA paper"
→ paper.read generates structured notes

"Is this derivation step correct? [paste]"
→ proof.critique checks it

"That's it for today"
→ session.close saves summary + evolve.suggest updates skill values
```

### Idea Exploration

```
"What are the open problems in agent memory?"
→ idea.discover generates candidates

"Is the second idea novel?"
→ idea.verify checks against existing literature

"Let's go with that direction"
→ decision.analyze records the choice
```

### Paper Writing

```
"Time to start writing"
→ writing.outline generates structure

"Write the introduction"
→ writing.draft produces a draft

"Review this version"
→ writing.review simulates peer review
```

## License

MIT — See [LICENSE](LICENSE)
