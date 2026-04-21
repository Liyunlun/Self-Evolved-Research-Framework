---
name: code-branch
description: Create a git branch or worktree before starting non-trivial coding work — picks `exp/`, `feat/`, or `fix/` prefix by intent, uses `.worktrees/{name}` for isolated large changes, leaves current branch intact for small edits. Triggers on "start a branch for X", "isolate this work", "create a worktree", or at the beginning of any checklist Implementation task that is medium/large in scope.
---

# code-branch

**Trigger**: User starts non-trivial coding work that warrants isolation, OR a checklist Implementation checkbox is about to be expanded into a roadmap.

**Shared context**: Before acting, Read `skills/_shared/git-conventions.md` for the canonical branch naming, worktree pattern, and rules. Do not restate those rules here.

## Process

### Step 1 — Decide branch vs direct

| Signal | → Path |
|--------|--------|
| Small edit (< 30 lines, single file, < 1 hour) | **Work on current branch** — skip to Step 4 (no branch created) |
| New feature / module / multi-file change | **Named branch** — Step 2 |
| Long-running work (days+), or must not disturb current tree | **Worktree** — Step 3 |
| Experiment sweep / ablation / probe | **Named branch** (`exp/*`) — Step 2 |

### Step 2 — Named branch

1. Pick prefix per `skills/_shared/git-conventions.md § Branch Strategy`:
   - `exp/` — experiment (sweep, ablation, probe)
   - `feat/` — new feature / module
   - `fix/` — bug fix
2. Pick kebab-case slug describing the work (e.g., `feat/config-parser`).
3. Create and switch:
   ```bash
   git checkout -b {type}/{slug}
   ```
4. Report the branch name to the user and to downstream skills (`code-roadmap`, `code-implement`).

### Step 3 — Worktree (for large / isolated work)

1. Pick prefix + slug as in Step 2.
2. Create worktree:
   ```bash
   git worktree add .worktrees/{type}-{slug} -b {type}/{slug}
   ```
3. Switch directory:
   ```bash
   cd .worktrees/{type}-{slug}
   ```
4. Report the worktree path to the user. Downstream skills run in this directory until work is merged.

### Step 4 — Small edit on current branch

No branch action taken. Report: "Working directly on `{current_branch}` — change is small enough to skip isolation."

## Output

```
[code-branch] {created|using}: {branch_name}
  Path: {repo root | .worktrees/{name}}
  Ready for: code-roadmap (medium/large) or code-implement (small)
```

**Inputs**: User intent + task scope signals
**Outputs**: New branch / worktree path / unchanged tree
**Token**: ~1-2K
**Composition**:
- Non-trivial task → suggest `code-roadmap` next to write the implementation roadmap
- Small edit → suggest `code-implement` next to go straight to TDD
