# Code — Git, Review, Testing & Debugging

> Deterministic skill group — no Bayesian weight updates.
> Applies the same standard to ALL code: experiment scripts, framework, utilities.
> Fuses SER conventions, ECC superpowers discipline, and Codex cross-model review.

## Skills

### code.implement

**Trigger**: Writing new code or modifying existing code for any purpose.

**Process** (from `superpowers:test-driven-development` — RIGID, no exceptions):

1. **RED**: Write a failing test first that defines the expected behavior.
2. **GREEN**: Write the minimal code to make the test pass.
3. **REFACTOR**: Clean up while keeping tests green.

Rules:
- Test file lives next to source (or in `tests/` mirror).
- Run tests after every change — never assume they pass.
- If tests exist, run them first to establish baseline.
- No "I'll test after" — tests written after prove nothing.

**Suggested Next**: `code.review`

---

### code.debug

**Trigger**: Any bug, test failure, or unexpected behavior.

**Process** (from `superpowers:systematic-debugging` — RIGID):

**Phase 1 — Reproduce**
- Get the exact error: command, output, traceback.
- Run it yourself — don't trust descriptions.

**Phase 2 — Isolate**
- Binary search: narrow to the smallest failing unit.
- Check recent changes: `git diff`, `git log --oneline -10`.
- Add targeted logging/assertions (not print-spray).

**Phase 3 — Root Cause**
- Identify the ACTUAL cause, not symptoms.
- If 3+ fix attempts fail → stop. Question the architecture.
- Consider: is the design wrong, not just the implementation?

**Phase 4 — Verify Fix**
- Fix must address root cause, not patch symptoms.
- Run the original failing test.
- Run the full test suite — regression check.
- Remove temporary debug code.

Additional tools:
- `superpowers:find-polluter` — when a test passes alone but fails in suite.
- `superpowers:using-git-worktrees` — isolate debugging from main work.

**Suggested Next**: `code.implement` (if fix requires new code) or `code.review`

---

### code.review

**Trigger**: Code changes ready for review (before commit). `observe.sh` reminds via dirty flag.

**Process** — Dual-layer review:

**Layer 1: Codex cross-model review (GPT)**
```
/codex:review
```
- Reviews working tree diff via `mcp__codex__codex`.
- Provides external perspective (different model, different biases).
- Focus: logic errors, edge cases, security, API misuse.

**Layer 2: ECC code-reviewer (Claude subagent)**
- Invoke `superpowers:requesting-code-review`.
- Dispatches a code-reviewer subagent in isolated worktree.
- Focus: spec compliance, test coverage, code quality.

**Synthesis**:
- If both agree: proceed to commit.
- If they diverge: analyze the disagreement, fix genuine issues.
- If review finds issues: fix → re-review (max 3 rounds per `config.yaml` `workflows.review_loop.max_rounds`).

**Suggested Next**: `code.commit`

---

### code.verify

**Trigger**: About to claim work is complete, fixed, or passing.

**Process** (from `superpowers:verification-before-completion` — RIGID):

1. **IDENTIFY** — What claims are you about to make?
2. **RUN** — Execute the verification command (test, build, lint).
3. **READ** — Read the actual output. Every line.
4. **VERIFY** — Does output confirm the claim? Be honest.
5. **CLAIM** — Only now may you state completion.

Rules:
- "Should work" is not verification. Run the command.
- "Tests pass" requires seeing `PASS` / `OK` in output.
- Partial success is not success.

**Suggested Next**: `code.commit` (if verified) or `code.debug` (if failed)

---

### code.commit

**Trigger**: Code reviewed and verified, ready to persist.

**Process**:

1. **Stage explicitly** — name files, never `git add -A` or `git add .`.
2. **Prefix message** — use convention from `config.yaml git.commit_prefixes`:
   - `feat:` new feature
   - `fix:` bug fix
   - `exp:` experiment code
   - `refactor:` restructuring
   - `docs:` documentation
   - `chore:` maintenance
3. **Never commit**: secrets (.env, credentials), `.claude/`, `logs/`, `memory/episodes/`.
4. **Verify**: run `git status` after commit to confirm clean state.
5. **Clear dirty flag**: `observe.sh` auto-clears `.claude/.ser-dirty` on commit detection.

**Suggested Next**: `experiment.run` (if experiment code) or next task

---

### code.branch

**Trigger**: Starting work that needs isolation, or large changes.

**Process** (from `superpowers:using-git-worktrees`):

**Branch naming**:
- `exp/<name>` — experiment branches
- `feat/<name>` — new features
- `fix/<name>` — bug fixes

**For large changes**: Use git worktree for isolation.
```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
```
- Work in worktree, main directory unaffected.
- When done: invoke `superpowers:finishing-a-development-branch`.
- Merge to main when tests pass and review complete.

**For small changes**: Work on current branch directly.

**Suggested Next**: `code.implement`

---

## Cross-Cutting Rules

### 1% Rule
If there is even a 1% chance a code skill applies, invoke it. Do not rationalize.

### Process Before Domain
When code skills and research skills both apply:
1. Process skills first (`code.debug`, `code.implement`) — determine HOW
2. Domain skills second (`experiment.*`, `paper.*`) — determine WHAT

### Red Flags — STOP when you think these

| Thought | Reality |
|---------|---------|
| "This is just simple code" | Simple things become complex. Use TDD. |
| "I'll test after" | Tests written after pass immediately, prove nothing. |
| "Should work now" | Not verification. Run the command, read output. |
| "Too simple for review" | All code gets reviewed. No exceptions. |
| "Let me explore first" | Skills tell you HOW to explore. Invoke first. |
| "3+ fixes failed, let me try once more" | Architecture problem. Stop and discuss. |

## Workflow Chains

**Standard**: `code.implement` → `code.review` → `code.commit`
**With experiment**: `experiment.plan` → `code.implement` → `code.review` → `code.commit` → `experiment.run`
**Debugging**: `code.debug` → `code.implement` → `code.review` → `code.commit`
