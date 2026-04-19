# code.debug

**Trigger**: Any bug, test failure, or unexpected behavior.

## Process (from `superpowers:systematic-debugging` — RIGID)

### Phase 1 — Reproduce
- Get the exact error: command, output, traceback.
- Run it yourself — don't trust descriptions.

### Phase 2 — Isolate
- Binary search: narrow to the smallest failing unit.
- Check recent changes: `git diff`, `git log --oneline -10`.
- Add targeted logging/assertions (not print-spray).

### Phase 3 — Root Cause
- Identify the ACTUAL cause, not symptoms.
- If 3+ fix attempts fail → stop. Question the architecture.
- Consider: is the design wrong, not just the implementation?

### Phase 4 — Verify Fix
- Fix must address root cause, not patch symptoms.
- Run the original failing test.
- Run the full test suite — regression check.
- Remove temporary debug code.

### Additional tools
- `superpowers:find-polluter` — when a test passes alone but fails in suite.
- `superpowers:using-git-worktrees` — isolate debugging from main work.

## Suggested Next
- `code.implement` (if fix requires new code) or `code.review`
