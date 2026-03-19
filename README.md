# Self-Evolved Research (SER) — Dev Branch

> Development fork of the [Self-Evolved Research Framework](https://github.com/Shiien/Self-Evolved-Research-Framework) v5.0.

A behavior-driven research collaboration framework for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). You talk naturally — SER detects intent and routes to the right micro-skill. The framework improves its own skills through use via natural language TD learning.

**Key capabilities**: 50 micro-skills, hierarchical checklist engine, TD-NL self-evolution, and dual review (cross-model verification via external LLM).

## Architecture

SER uses a 3-layer behavioral protocol:

| Layer | Scope | File |
|-------|-------|------|
| **Layer 0** | Global defaults (git, GPU policy, tools) | `~/.claude/CLAUDE.md` |
| **Layer 1** | SER dev framework (intent router, skills, data contracts) | `CLAUDE.md` |
| **Layer 2** | Project-specific config and memory | `config.yaml` + `memory/` |

## Installation

```bash
git clone git@github.com:Liyunlun/Self-Evolved-Research-Framework.git
cd Self-Evolved-Research-Framework
bash scripts/setup.sh
```

The setup script creates `config.yaml`, initializes the memory system, and sets up all required directories. It includes a MetaScheduler mode option for automated agent workflows. Safe to run multiple times.

## Micro-Skills (50 skills across 16 spec files)

| Category | Spec File | Skills |
|----------|-----------|--------|
| **Session** | `session.md` | `session.open`, `.close` |
| **Paper** | `paper.md` | `paper.read`, `.compare`, `.index`, `lit.search` |
| **Theory** | `theory.md` | `theory.formalize`, `.decompose`, `.search`, `.counterexample`, `.generalize` |
| **Proof** | `proof.md` | `proof.critique`, `.fix`, `.formalize`, `.verify` |
| **Writing** | `writing.md` | `writing.outline`, `.draft`, `.review`, `.polish` |
| **Planning** | `planning.md` | `plan.suggest`, `.milestone`, `progress.capture`, `status.report`, `decision.analyze`, `experiment.analyze` |
| **Experiment** | `experiment.*.md` | `experiment.run`, `.monitor` (base + local + MetaScheduler modes) |
| **Memory** | `memory.md` | `memory.write`, `.retrieve`, `.consolidate`, `.forget` |
| **Meta** | `meta.md` | `evolve.suggest`, `.apply` |
| **Idea** | `idea.md` | `idea.discover`, `.verify` |
| **Research** | `research.md` | `research.explore`, `design.converge` |
| **Checklist** | `checklist.md` | `checklist.generate`, `.verify`, `.update`, `.create`, `.status` |
| **Visual** | `visual.md` | Visual artifact generation |
| **Integrate** | `integrate.md` | Cross-skill integration |

## Skill Evolution (TD-NL)

The framework optimizes its own micro-skill specs through natural language TD learning:

1. **G2** (inline): After every skill fires, append outcome assessment to feedback log
2. **G1** (session.close): Aggregate G2 feedback, update per-skill value estimates, propose spec edits
3. **Apply** (user-triggered): Edit skill specs with version archive and rollback safety

## Project Structure

```
├── CLAUDE.md              # Behavioral protocol (intent router + data contracts)
├── Checklist.md           # Project progress root
├── config.template.yaml   # Copy to config.yaml and customize
├── skills/
│   ├── micro/             # 16 micro-skill spec files (optimization target)
│   └── td-nl/             # TD-NL skill evolution infrastructure
├── scripts/               # Utility scripts (setup, citation, notify, analyzer)
├── memory/                # Persistent three-tier memory (episodes/topics/procedures)
├── checklists/            # Hierarchical task tracking (L1/L2)
├── experiments/           # Experiment code + results
├── outputs/               # Research deliverables
├── resources/             # Reference materials (papers/ + repos/)
├── logs/digest/           # Session logs
└── docs/                  # Plans, reports
```

## Upstream

This is a development fork. Upstream: [Shiien/Self-Evolved-Research-Framework](https://github.com/Shiien/Self-Evolved-Research-Framework)

## License

MIT — See [LICENSE](LICENSE)
