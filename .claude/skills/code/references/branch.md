# code.branch

**Trigger**: Starting work that needs isolation, or large changes.

## Process (from `superpowers:using-git-worktrees`)

### Branch naming
- `exp/<name>` — experiment branches
- `feat/<name>` — new features
- `fix/<name>` — bug fixes

### For large changes
Use git worktree for isolation:
```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
```
- Work in worktree, main directory unaffected.
- When done: invoke `superpowers:finishing-a-development-branch`.
- Merge to main when tests pass and review complete.

### For small changes
Work on current branch directly.

## Suggested Next
- `code.implement`
