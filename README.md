# SER — Self-Evolved Research

> A behavior-driven research framework for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).
> Skills trigger automatically. The framework improves its own skills through use.

<p align="center">
  <img src="ser_architecture_overview.svg" alt="SER Architecture Overview" width="700"/>
</p>

## What It Does

You talk naturally. SER detects your intent and routes to the right micro-skill:

| You say | SER triggers |
|---------|-------------|
| "I'm reading this paper..." | `paper-read` — structured notes |
| "Is this proof correct?" | `proof-critique` — step-by-step check |
| "What should I do next?" | `plan-suggest` — prioritized tasks |
| "Run the experiment" | `experiment-run` — launch + monitoring |
| "Any novel ideas for X?" | `idea-discover` → `idea-verify` |
| "Write the introduction" | `writing-draft` — section draft |
| (end conversation) | `session-close` — auto-saves summary |

Every skill execution generates feedback. Over sessions, SER proposes improvements
to its own skill specs via natural language TD learning — the skills you use today
become better tomorrow.

## Getting Started

### 1. Clone

```bash
git clone --recurse-submodules https://github.com/Shiien/Self-Evolved-Research-Framework.git
cd Self-Evolved-Research-Framework
```

> **Already cloned without `--recurse-submodules`?** Run:
> ```bash
> git submodule update --init --recursive
> ```

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
1. Read your config and memory (`session-open`)
2. Show a status banner
3. Wait for your research request — no commands needed

### 5. Install the skills into `.claude/skills/`

```bash
bash scripts/install-skills.sh            # copy into ./.claude/skills
bash scripts/install-skills.sh --link     # symlink (dev workflow)
bash scripts/install-skills.sh --user     # install into ~/.claude/skills
bash scripts/install-skills.sh --list     # list discovered skills
```

Each SER skill lives in its own directory under `skills/` with a standard
`SKILL.md` (YAML frontmatter + body), so Claude Code auto-discovers and
auto-triggers them once installed.

## Skills (42 SER + 1 external)

Each skill lives in `skills/{skill-name}/SKILL.md` with standard YAML frontmatter.

| Category | Skills | Purpose |
|----------|--------|---------|
| **Session** | `session-open`, `session-close` | Lifecycle: status banner, auto-save |
| **Paper** | `paper-read` (standard + deep/Fey-R), `paper-compare`, `paper-index` | Reading & analysis |
| **Theory** | `theory-formalize`, `theory-decompose`, `theory-search`, `theory-counterexample`, `theory-generalize` | Formalization & proof strategy |
| **Proof** | `proof-critique`, `proof-fix`, `proof-formalize`, `proof-verify` | Verification & correction |
| **Writing** | `writing-outline`, `writing-draft`, `writing-review`, `writing-polish` | Paper authoring |
| **Planning** | `plan-suggest`, `plan-milestone`, `progress-capture`, `status-report`, `decision-analyze`, `experiment-analyze` | Project management |
| **Experiment** | `experiment-run`, `experiment-monitor` | Experiment dispatch |
| **Idea** | `idea-discover`, `idea-verify` | Gap analysis + novelty check |
| **Checklist** | `checklist-create`, `checklist-verify`, `checklist-update`, `checklist-status` | Paper audit & claim tracking |
| **Research** | `research-explore`, `design-converge` | Open-ended exploration |
| **Memory** | `memory-write`, `memory-retrieve`, `memory-consolidate`, `memory-forget` | Persistent cross-session memory |
| **Meta** | `evolve-suggest`, `evolve-apply`, `general-research` | TD-NL skill self-improvement + fallback |
| **Integration** | `project-integrate` | Merge SER into an existing project |

## External Skills

| Skill | Source | Purpose |
|-------|--------|---------|
| [Fey-R](https://github.com/xvirobotics/fey-r) | `skills/external/fey-r/` | Interactive Feynman-method paper reading — deeply understand papers by recreating the author's derivation |

External skills are installed as git submodules and initialized automatically by `scripts/setup.sh`.
To add your own, use `git submodule add <url> skills/external/<name>/`.

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs through natural language TD learning:

```
skill fires → G2 assessment (was it useful?) → accumulate over sessions
                                                        ↓
session.close → G1 aggregation → per-skill value update → spec edit proposal
                                                        ↓
                                    user approves → evolve.apply → rollback if quality drops
```

The optimization target is the skill specs themselves (`skills/{skill-name}/SKILL.md`).
Version history in `skills/td-nl/history/` enables safe rollback.

## Project Structure

```
├── CLAUDE.md              # Behavioral protocol (intent router + data contracts)
├── config.template.yaml   # Copy to config.yaml and customize
├── README.md / LICENSE
├── skills/
│   ├── {skill-name}/      # 42 SER skills, each with SKILL.md + YAML frontmatter
│   ├── _shared/           # Shared infra read by related skills
│   │   ├── checklist-engine.md
│   │   ├── memory-tiers.md
│   │   └── evolve-cycle.md
│   ├── external/          # External skills (git submodules)
│   │   └── fey-r/         # Feynman-method paper reading
│   └── td-nl/             # Skill evolution infrastructure
│       ├── feedback-log.md
│       ├── value-function.md
│       ├── skill-values/   # Per-skill Q^L estimates
│       └── history/        # Spec version archive for rollback
├── scripts/               # Utility scripts (citation, notify, analyzer, install-skills)
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

- **Intent router**: 25 patterns that map your messages to SER skills
- **Session lifecycle**: auto-open/close with memory persistence
- **Data contracts**: standardized formats for logs, paper notes, memory files
- **Evolution loop**: G2/G1 feedback cycle for skill improvement

Each subdirectory has its own `CLAUDE.md` with scoped context for that area.
The root `CLAUDE.md` is the bootloader; subdirectory files are namespace guides.

## Typical Workflows

### Daily Research

```
(open claude)
→ session-open shows status banner

"I want to continue reading the LAPA paper"
→ paper-read generates structured notes

"Is this derivation step correct? [paste]"
→ proof-critique checks it

"That's it for today"
→ session-close saves summary + evolve-suggest updates skill values
```

### Idea Exploration

```
"What are the open problems in agent memory?"
→ idea-discover generates candidates

"Is the second idea novel?"
→ idea-verify checks against existing literature

"Let's go with that direction"
→ decision-analyze records the choice
```

### Paper Writing

```
"Time to start writing"
→ writing-outline generates structure

"Write the introduction"
→ writing-draft produces a draft

"Review this version"
→ writing-review simulates peer review
```

## License

MIT — See [LICENSE](LICENSE)
