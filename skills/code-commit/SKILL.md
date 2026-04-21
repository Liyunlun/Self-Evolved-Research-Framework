---
name: code-commit
description: Commit reviewed code. Runs a pre-commit verification pass (full test suite + each Done Criterion + `git diff --stat` + user confirmation), writes a prefixed message per `skills/_shared/git-conventions.md`, explicit-stages named files, and — when the task was driven by a checklist Implementation checkbox — calls `checklist-update` to mark `[x]` and annotate the checkbox with the commit SHA. Triggers after `code-review` returns PASS, or on "commit these changes", "finalize this work".
---

# code-commit

**Trigger**: Code is reviewed and PASSED. Ready to persist.

**Shared context**: Before acting, Read `skills/_shared/git-conventions.md` for commit prefix list, staging rules, never-commit list, and post-commit verification. Do not restate those rules here.

## Process

### Step 1 — Pre-commit verification

This absorbs v6's "pre-commit final verification" from the (retired) synthesize skill. Single-round; no loop.

1. **Run the full test command** from the roadmap's Context § Test command (or the project's default test command for small tasks). Must pass with zero failures.
2. **Run each Done Criterion** from the roadmap (full mode). Record evidence for each.
3. **Summarize the change**: `git diff --stat` — present the change list to the user.
4. **Confirm with user**:
   ```
   Ready to commit:
     Files changed: {N}
     Lines +{added} / -{removed}
     Tests: PASS
     Done Criteria: {k}/{K} PASS
   Proceed? (y/n)
   ```
   Wait for user response. Do NOT commit on "ambiguous".

Skip steps 1–2 for small tasks without a roadmap (no Done Criteria to run); keep the diff summary and confirmation.

### Step 2 — Select commit prefix

Per `skills/_shared/git-conventions.md § Commit Prefixes`. Choose by dominant intent:

| Prefix | When |
|--------|------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `exp:` | Experiment code / sweep / ablation |
| `refactor:` | Restructure without behavior change |
| `docs:` | Documentation only |
| `chore:` | Tooling / deps / maintenance |

### Step 3 — Stage explicitly

Per `skills/_shared/git-conventions.md § Staging Rules`:
- Name each file:
  ```
  git add path/to/file.py path/to/test_file.py
  ```
- Never `-A` or `-.`.
- Run `git status` to verify nothing unintended is present; check against the Never-Commit list.

### Step 4 — Write the commit

```
git commit -m "{prefix}: {imperative short summary}

{optional body — explain WHY, not WHAT}"
```

Keep the subject line under 72 characters. Imperative mood.

### Step 5 — Post-commit verification

1. `git status` — working tree should be clean.
2. `git log --oneline -1` — confirm the commit landed with the right message.
3. Capture the SHA: `git rev-parse HEAD`.

### Step 6 — Checklist integration (SER-specific)

If the task was driven by a checklist `[ ] Implementation` checkbox:

1. Invoke `checklist-update` to:
   - Mark the checkbox `[x]`.
   - Append the commit SHA to the artifact field, e.g.:
     ```
     - [x] Implementation — `docs/implement_roadmap/2026-04-21-config-parser.md` · commit `{sha-short}`
     ```
2. If the checkbox is part of a BRANCH (L2 sub-checklist), `checklist-update` recomputes parent counts automatically.
3. Verification by `checklist-verify` (evidence check → `[v]`) is a separate later step, not chained here.

For tasks not driven by a checklist, skip Step 6.

---

## Output

```
[code-commit] Committed
  Prefix: {feat/fix/...}
  Message: {subject line}
  SHA: {abbreviated}
  Files: {N}
  Tree: clean
  Checklist: {[x] at path | n/a}
  Pushed: no  (run `git push` separately per git-conventions § When to Push)
```

**Inputs**: Reviewed working tree + (optional) roadmap + (optional) driving checkbox
**Outputs**: One git commit; optional checklist checkbox update
**Token**: ~2-5K
**Composition**:
- Task was research-facing → proceed to next research skill (`experiment-run`, `paper-illustrate`, etc.) as the checklist suggests
- Task was framework-facing → done; next user task
