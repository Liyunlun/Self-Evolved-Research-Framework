# Git Conventions — Shared Infrastructure

> Shared reference for `code-branch` and `code-commit`. Defines branch naming,
> worktree pattern, commit prefixes, staging rules, never-commit list, and push
> timing.
>
> Not a skill itself (no `SKILL.md`). `code-branch/SKILL.md` and
> `code-commit/SKILL.md` direct Claude to read this file before acting.
>
> This file is the **single authoritative source** for git behavior inside SER.
> Do not duplicate rules into individual SKILL.md files. Do not read
> `config.yaml` for git settings — it does not carry any.

---

## Branch Strategy

```
main                     ← stable, verified code only
  ├── exp/<name>         ← experiment branches (sweeps, ablations, probes)
  ├── feat/<name>        ← new features / modules
  └── fix/<name>         ← bug fixes
```

### Rules
- `main` is protected. Only merge tested, validated code.
- Work on a named branch, not on `main` directly.
- Branch name format: `{type}/{slug}` where `{slug}` is kebab-case and
  describes the work (e.g., `exp/lr-ablation`, `feat/config-parser`,
  `fix/grad-nan`).
- Choose the prefix that matches the dominant intent of the change.

---

## Worktree Pattern (for Large Changes)

For multi-day work or when current working tree must stay undisturbed:

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>
```

- Work inside the worktree; main repo directory is unaffected.
- Merge back to `main` when tests pass and review is complete.
- Remove worktree after merge: `git worktree remove .worktrees/<branch-name>`.

For small changes (single-file, < 30 lines, < 1 hour), work on the current
branch directly without a worktree.

---

## Commit Prefixes

Every commit message starts with one of:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `exp:` | Experiment code, sweeps, ablations (research artifacts) |
| `refactor:` | Restructuring without behavior change |
| `docs:` | Documentation only |
| `chore:` | Maintenance, dependency bumps, tooling |

Message format: `{prefix}: {imperative short summary}` on the subject line,
blank line, then optional body explaining *why* (not *what* — the diff shows
that).

---

## Staging Rules

- **Explicit staging only.** Name files:
  ```
  git add path/to/file.py path/to/other.py
  ```
- **Never** run `git add -A` or `git add .` — they risk pulling in secrets,
  cache, or unrelated work.
- Run `git status` before staging to see what is present.
- Run `git diff --cached` after staging to confirm exactly what will be
  committed.

---

## Never-Commit List

These paths must never enter a commit:

- Secrets: `.env`, `*.key`, `*credentials*`, API tokens in source
- Framework state: `.claude/`, `skills/_shared/*/state/`, local hook outputs
- Volatile artifacts: `logs/`, `memory/episodes/` (ephemeral episodic memory),
  `.worktrees/`, `__pycache__/`, `.pytest_cache/`
- Heavy binaries: model checkpoints, `wandb/` runs, datasets (use git-lfs or
  external storage)

If any of these paths appear in `git status`, stop and investigate before
proceeding.

---

## Commit Procedure

1. Review staged diff: `git diff --cached`.
2. Write commit with prefix: `git commit -m "{prefix}: {summary}"`.
3. Verify: `git status` after commit — working tree should be clean.
4. If pre-commit hook fails, do NOT `--amend` the previous commit. Fix the
   issue, re-stage, and create a NEW commit.

---

## When to Push

- After merging a branch to `main`.
- Before ending a work session (push current branch as a backup).
- After significant progress on an experiment branch.

Do not force-push to `main`. Force-push to feature branches only if the
branch is not shared with others.
