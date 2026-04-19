# code.implement

**Trigger**: Writing new code or modifying existing code for any purpose.

## Step 0: Size Assessment

Before writing any code, estimate the implementation scope:

| Signal | → Path |
|--------|--------|
| Localized change, single file, < ~30 lines of new logic | **Small** → Step 1 below |
| New module, multiple files, significant new logic (30-200+ lines) | **Medium/Large** → `references/plan.md` |
| User explicitly requests plan, design review, or Codex implementation | **Medium/Large** → `references/plan.md` |
| Change involves SER framework files (`.claude/`, `skills/`, hooks) | **Small** → Step 1 below (Claude must handle directly) |
| Codex unavailable or unauthenticated | **Small** → Step 1 below |

**Default to Small.** Only route to plan when the task clearly benefits from structured planning and Codex execution.

When uncertain, ask the user: "This looks like it could be a [small/medium] task. Should I implement it directly or create a plan for Codex?"

## Step 1: Small Task — Claude Direct TDD

Process (from `superpowers:test-driven-development` — RIGID, no exceptions):

1. **RED**: Write a failing test first that defines the expected behavior.
2. **GREEN**: Write the minimal code to make the test pass.
3. **REFACTOR**: Clean up while keeping tests green.

### Rules
- Test file lives next to source (or in `tests/` mirror).
- Run tests after every change — never assume they pass.
- If tests exist, run them first to establish baseline.
- No "I'll test after" — tests written after prove nothing.

## Suggested Next
- `code.review`
