# Skills — Standard Claude Code Skills + TD-NL Evolution

This directory holds the SER framework's skills in **standard Claude Code format**:
one directory per skill, each with a `SKILL.md` that has YAML frontmatter
(`name`, `description`) and a markdown body. Claude Code auto-loads the body
when a skill's description matches the current conversation intent.

## How skills are organized

```
skills/
  {skill-name}/SKILL.md      # 42 SER skills
  _shared/*.md               # Cross-cutting reference docs (not skills themselves)
  external/{name}/SKILL.md   # External skills (git submodules)
  td-nl/                     # Skill evolution infrastructure
```

`_shared/` holds large cross-cutting documents that multiple skills depend on:
`checklist-engine.md`, `memory-tiers.md`, `evolve-cycle.md`. The skills that
need them instruct Claude to Read them on demand. `_shared/` has no `SKILL.md`
so it's ignored by `scripts/install-skills.sh`.

## Skill index (48 SER + 1 external)

### Session lifecycle
- `session-open`, `session-close`

### Paper reading
- `paper-read`, `paper-compare`, `paper-index`
- `external/fey-r` — deep Feynman-method paper reading

### Theory & proofs
- `theory-formalize`, `theory-decompose`, `theory-search`, `theory-counterexample`, `theory-generalize`
- `proof-critique`, `proof-fix`, `proof-formalize`, `proof-verify`

### Writing
- `writing-outline`, `writing-draft`, `writing-review`, `writing-polish`

### Planning & progress
- `plan-suggest`, `plan-milestone`, `progress-capture`, `status-report`, `decision-analyze`, `experiment-analyze`

### Experiments
- `experiment-run`, `experiment-monitor`

### Ideas
- `idea-discover`, `idea-verify`

### Checklist engine
- `checklist-create`, `checklist-verify`, `checklist-update`, `checklist-status`
- Shared vocabulary: `_shared/checklist-engine.md`

### Memory
- `memory-write`, `memory-retrieve`, `memory-consolidate`, `memory-forget`
- Shared vocabulary: `_shared/memory-tiers.md`

### Research exploration
- `research-explore`, `design-converge`

### Code family
- `code-branch`, `code-roadmap`, `code-implement`, `code-review`, `code-debug`, `code-commit`
- Shared vocabulary: `_shared/git-conventions.md` (all tracks) and `_shared/codex-contract.md` (codex track only)
- Two install tracks via `scripts/install-skills.sh --code-track claude|codex`; `code-implement` and `code-review` each ship `SKILL.claude.md` + `SKILL.codex.md` variants materialized at install time

### Meta (TD-NL skill evolution)
- `evolve-suggest`, `evolve-apply`, `general-research`
- Shared vocabulary: `_shared/evolve-cycle.md`

### Integration (one-off)
- `project-integrate` — merge an unpacked SER distribution into an existing project

## Install into `.claude/skills/`

Run `bash scripts/install-skills.sh --list` to list everything discovered,
`bash scripts/install-skills.sh` to copy into `./.claude/skills/`, or
`bash scripts/install-skills.sh --link --force` for a developer-friendly
symlinked install.

## TD-NL evolution infrastructure

```
td-nl/
  feedback-log.md       # G2 entries (per-firing) + processed cycles
  value-function.md     # V^L: global skill system assessment
  skill-values/         # Q^L per skill (created on first firing)
    _template.md        # Template for new skill value files
  history/              # Spec version archive (pre-edit snapshots for rollback)
```

See `_shared/evolve-cycle.md` for the full G2 → G1 → `evolve-suggest` → `evolve-apply` process.

## External skills (git submodules)

| Directory | Skill | Purpose |
|-----------|-------|---------|
| `external/fey-r/` | `fey-r` | Feynman-method paper reading (deep understanding via derivation) |

Run `git submodule update --init --recursive` or `bash scripts/setup.sh` to initialize.
