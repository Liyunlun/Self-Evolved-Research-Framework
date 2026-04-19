---
name: code
description: Git workflow, code review, test-driven development, debugging, and commit discipline
---

# /code — Git, Review, Testing & Debugging

> Deterministic skill group — no Bayesian weight updates.
> Applies the same standard to ALL code: experiment scripts, framework, utilities.
> Fuses SER conventions, ECC superpowers discipline, and Codex cross-model review.

Route the user's intent to the appropriate sub-skill:

- **Implement new code or modify existing code** (user needs to write code, add a feature, or change behavior) → read `references/implement.md` and follow its instructions
- **Debug a bug or test failure** (any bug, unexpected behavior, or test failure) → read `references/debug.md` and follow its instructions
- **Review code changes** (code is ready for review before commit, dirty flag detected) → read `references/review.md` and follow its instructions
- **Commit reviewed code** (code reviewed and verified, ready to persist) → read `references/commit.md` and follow its instructions
- **Create a branch or isolate work** (starting work that needs isolation, or large changes) → read `references/branch.md` and follow its instructions

### Internal chain steps (not directly user-routed)

These sub-skills are invoked by the medium/large task workflow chain, not by direct user intent routing. They are reached via `code.implement` → plan → execute → review → synthesize.

- `references/plan.md` — Claude writes a detailed implementation plan (entered from `code.implement` for medium/large tasks)
- `references/execute.md` — Codex implements the plan via `/codex:rescue` with Superpowers
- `references/synthesize.md` — Claude synthesizes dual review results and manages fix cycles

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

**Small task**: `code.implement` → `code.review` → `code.commit`
**Medium/Large task**: `code.implement` → `code.plan` → `code.execute` → `code.review` → `code.synthesize` → `code.commit`
**Debugging**: `code.debug` → `code.implement` → `code.review` → `code.commit`
**With experiment**: `experiment.plan` → `code.implement` → `code.review` → `code.commit` → `experiment.run`

### Medium/Large task loop
`code.synthesize` may loop back to `code.execute` (with updated plan) up to 2 additional times, for a maximum of 3 total execution rounds. After round 3, ask the user before continuing.

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
