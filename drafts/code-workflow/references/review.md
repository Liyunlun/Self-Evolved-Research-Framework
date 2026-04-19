# code.review

**Trigger**: Code changes ready for review. `observe.sh` reminds via dirty flag.

Two independent reviews run in sequence. Neither reviewer sees the other's output.

## Determine Review Mode

| Source of changes | Review mode |
|-------------------|-------------|
| Small task (Claude direct TDD) | **Lightweight** — skip Review A, run Review B only |
| Medium/Large task (Codex via plan) | **Full** — both Review A and Review B |

---

## Review A: Claude Plan Compliance Review

**Reviewer**: Claude (main session)
**Purpose**: Verify the implementation achieves the plan's goal and acceptance criteria.

### Inputs

1. The plan file: `implementation_plans/YYYY-MM-DD-{name}.md`
2. Changes since plan started:
   - `git diff {base_commit_sha}` — modifications to tracked files
   - `git status -s` — new/untracked files created by Codex (`git diff` does not show these)
3. Test results from running the plan's test command

### Process

1. **Run the Done Criteria** from the plan. Record pass/fail for each.
2. **Check each step's Acceptance criteria** against the diff:
   - Does the diff contain the expected changes for this step?
   - Were the specified files created/modified?
   - Are there unexpected deletions or modifications?
3. **Check constraints compliance**:
   - Were any forbidden files modified? (`.claude/`, `skills/`, etc.)
   - Were any unplanned dependencies added?
   - Were files outside plan scope modified? If yes, was it justified?
4. **Check the goal**: Does the overall change, taken as a whole, achieve what the Goal line promises?

### Output Format

```markdown
## Claude Review: Plan Compliance

**Plan**: {plan file path}
**Base commit**: {SHA}
**Test suite**: {PASS / FAIL with details}

### Done Criteria
- [x] {criterion 1} — PASS
- [ ] {criterion 2} — FAIL: {what went wrong}

### Per-Step Verification
| Step | Title | Acceptance | Status | Notes |
|------|-------|------------|--------|-------|
| 1 | {title} | {criterion} | PASS | — |
| 2 | {title} | {criterion} | FAIL | {what's wrong} |

### Constraint Violations
- {none, or list violations}

### Unplanned Changes
- {files modified outside plan scope, with assessment: justified / concerning}

### Overall Assessment
{PASS — ready for commit / FAIL — issues listed above need fixing}
```

---

## Review B: Codex Code Quality Review

**Reviewer**: Codex (via `/codex:review`)
**Purpose**: Independent code quality assessment — different model, different biases.

### Process

Run:
```
/codex:review
```

This invokes Codex to review the working tree diff. Codex focuses on:
- Logic errors and edge cases
- Security issues (injection, auth, data exposure)
- API misuse or incorrect library usage
- Code clarity and maintainability
- Error handling gaps
- Performance concerns

### Output

Codex returns a structured review with findings ordered by severity. Preserve the output verbatim — do not summarize or reinterpret.

Expected output structure from `/codex:review` (for reference when parsing in `code.synthesize`):
- **Findings** ordered by severity (critical → important → minor)
- Each finding includes: file path, line number (if applicable), description, evidence
- **Assessment**: overall pass/fail recommendation
- **Residual risks** or follow-up suggestions

If Codex output format differs from above, extract findings as-is. The `code.synthesize` step will normalize both reviews into a unified table.

---

## Architectural Note

Previous versions used a two-layer serial review: Codex first, then a Claude subagent (`superpowers:requesting-code-review`) in an isolated worktree. The new design replaces this with:
- **Review A**: Claude main session reviews against the plan (goal compliance)
- **Review B**: Codex reviews independently (code quality)

This change is intentional. In the plan-based workflow, Claude's review role shifts from generic code quality (which Codex and Superpowers handle better) to **plan compliance** — checking whether the implementation actually achieves the research goal. The two reviews now have distinct purposes rather than overlapping scope.

For small tasks (no plan), the Claude subagent review via `superpowers:requesting-code-review` remains available as an option if desired.

---

## Lightweight Mode (Small Tasks)

For small tasks that did not go through the plan/execute flow:

1. **Skip Review A** (no plan to check against).
2. **Run Review B** (`/codex:review`) for code quality.
3. **Claude quick check**: Read the diff, confirm tests pass, confirm the change does what the user asked.

---

## Dependencies

This skill requires:
- `/codex:review` — Codex CLI review command (from `codex-plugin-cc`). Must be installed and authenticated. Check with `/codex:setup` if unavailable.

## Suggested Next
- `code.synthesize` (medium/large tasks with full review — **mandatory**, do not skip)
- `code.commit` (small tasks after lightweight review passes — lightweight mode does NOT proceed to `code.synthesize`)
