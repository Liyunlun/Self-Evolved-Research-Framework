---
name: code-debug
description: Systematic four-phase debugging — Reproduce, Isolate, Root Cause, Verify. Use when any test fails, a bug is reported, or behavior is unexpected. Enforces the rule that three failed fix attempts in a row means the architecture is wrong, not the implementation. Triggers on "debug this", "test fails", "unexpected behavior", "why does {X} happen", or after any `code-implement` step reports blocked.
---

# code-debug

**Trigger**: Any bug, test failure, or unexpected behavior. Independent of size assessment — small or large, failures go through the same four phases.

**Shared context**: None.

## Process (RIGID — do not skip phases)

### Phase 1 — Reproduce

- Get the exact error: command, stdout, stderr, traceback.
- Run it yourself. Do NOT trust second-hand descriptions.
- Capture the failing input: config file, data sample, CLI args. Save to a scratch file if the failure is environmental.
- If reproduction is flaky, establish the failure rate before continuing (e.g., "fails 3/10 runs"). Intermittent bugs require different tactics than deterministic ones.

### Phase 2 — Isolate

- **Binary search**: narrow to the smallest failing unit. Comment out half the suspect code, re-run, determine which half owns the failure, repeat.
- **Check recent changes**: `git diff` and `git log --oneline -10`. Did this work before? If yes, bisect: `git bisect start`.
- **Add targeted logging or assertions** at suspected boundaries. Do NOT print-spray — each log line should answer a specific question.
- Remove logging / assertions after the bug is understood.

### Phase 3 — Root Cause

- Identify the ACTUAL cause, not the symptom. "Test fails because assertion X returns False" is a symptom. "Test fails because function Y reads stale config before refresh" is a cause.
- **Hard rule**: If three fix attempts in a row fail, **stop**. The architecture may be wrong. Raise this to the user:
  ```
  [code-debug] Three fix attempts failed for {issue}.
  Candidates considered:
    1. {hypothesis} — failed because {observation}
    2. {hypothesis} — failed because {observation}
    3. {hypothesis} — failed because {observation}
  This pattern suggests the bug is architectural, not implementation-level.
  Suggest: review {module} design / data flow / state machine before attempting fix 4.
  ```
  Wait for user direction.
- Consider: is the design wrong (wrong abstraction, wrong ownership of state, wrong lifecycle), not just the implementation (typo, off-by-one)?

### Phase 4 — Verify Fix

- The fix must address the root cause, not patch the symptom.
- Run the originally failing test / command. Must pass.
- Run the full test suite — regression check. Must pass.
- Remove any temporary debug code, logging, assertions introduced in Phases 1–2.
- Commit the fix via `code-commit` with `fix:` prefix.

---

## Output

```
[code-debug] Complete
  Phase 1 reproduction: {command + evidence}
  Phase 2 isolation: {narrowed to: {file:line or module}}
  Phase 3 root cause: {one-line description}
  Phase 4 verification: {original test + full suite: PASS}
  Fix applied at: {files modified}
```

**Inputs**: Failing test output / user-reported behavior / unexpected log output
**Outputs**: Fixed code + passing tests; temporary debug code removed
**Token**: ~3-15K (highly bug-dependent)
**Composition**:
- Fix is a new piece of logic (beyond a typo) → loop through `code-implement` to write the fix with TDD, then return here for Phase 4
- Fix verified → `code-review` → `code-commit`
- Three attempts failed → halt and ask the user; do not chain further skills
