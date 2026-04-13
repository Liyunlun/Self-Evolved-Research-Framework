# code.plan

**Trigger**: `code.implement` routes here for medium/large tasks.

Claude writes a function-level implementation plan. The plan tells Codex **what to build and how to verify it**, not how to write the code. Codex uses Superpowers internally for TDD, sub-planning, and step-level testing.

## Process

### 1. Understand the Goal

- Read the user's request carefully. Ask clarifying questions if the goal is ambiguous.
- Identify the feature or change to implement.
- Read existing relevant source files to understand current architecture, interfaces, and conventions.
- Note the test framework in use (pytest, jest, etc.) and how tests are typically run.

### 2. Create the Plan Directory

```bash
mkdir -p implementation_plans
```

### 3. Write the Plan File

Save to: `implementation_plans/YYYY-MM-DD-{feature-name}.md`

The plan must follow the format below **exactly**. Every section is mandatory.

---

#### Plan File Format

````markdown
# Plan: {Feature Name}

## Goal

{One clear sentence: what this plan achieves when fully completed.}

## Context

- **Project**: {project name and brief description}
- **Language / Framework**: {e.g., Python 3.11, PyTorch 2.x, pytest}
- **Test command**: {e.g., `pytest tests/ -v`}
- **Key files for context** (Codex should read these to understand the codebase):
  - `{path}` — {what this file does and why it matters}
  - `{path}` — {what this file does and why it matters}

## Constraints

- Do NOT modify: `.claude/`, `skills/`, `memory/`, `hooks/`, `config.yaml`, `CLAUDE.md`
- Do NOT run `git commit` or `git push`
- Do NOT add new dependencies unless explicitly justified in a step
- {Any project-specific constraints — e.g., "must be backward-compatible with existing config format"}

## Steps

### Step 1: {Descriptive title}

- **Purpose**: {Why this step is needed — the problem it solves or the capability it adds}
- **Files**:
  - Create: `{path}` — {what this file will contain}
  - Modify: `{path}` — {what changes and why}
  - Test: `{path}` — {test file for this step}
- **What to do**: {Concrete description of the change at function/class/module level. Describe interfaces, expected behavior, edge cases to handle. Do NOT write code — describe what the code should do.}
- **Acceptance**:
  - `{test command}` passes with all new tests green
  - {Any additional verifiable condition, e.g., "running `python -c 'from module import X'` succeeds"}

### Step 2: {Descriptive title}

- **Purpose**: ...
- **Files**: ...
- **What to do**: ...
- **Acceptance**: ...

{Continue for all steps. Typical plans have 3-8 steps.}

## Done Criteria

When the entire plan is complete, ALL of the following must be true:

1. `{full test command}` — all tests pass, zero failures
2. {Functional verification — e.g., "running `python main.py --config test.yaml` produces expected output"}
3. {Integration check — e.g., "existing tests in `tests/test_old.py` still pass (no regressions)"}

## Status

- [ ] Step 1: {title}
- [ ] Step 2: {title}
- [ ] ...
- **Round**: 1 (max 3 auto, then ask user)
- **Base commit**: {filled by code.execute before first run}
- **Last updated**: {YYYY-MM-DD}
````

---

### 4. Plan Quality Checklist

Before presenting the plan, verify:

- [ ] **Goal is testable**: The Done Criteria can be verified by running commands.
- [ ] **No placeholders**: Every step has concrete Purpose, Files, What to do, and Acceptance. No "TBD", "implement appropriate handling", or "similar to Step N".
- [ ] **Files are real paths**: Every file path in the plan exists (for Modify) or has a clear parent directory (for Create).
- [ ] **Steps are ordered**: Later steps can depend on earlier steps. No circular dependencies.
- [ ] **Constraints are complete**: All files that must NOT be touched are listed.
- [ ] **Context files are listed**: Codex will read these first — include files that define interfaces, types, or conventions that the new code must follow.
- [ ] **Acceptance is verifiable**: Every step has at least one command that produces a pass/fail result.

### 5. Present to User

Show the complete plan to the user. Wait for approval before proceeding.

If the user requests changes, update the plan file and re-present.

### Edge Cases

- **0-step plan**: If analysis reveals the task is already complete or requires no code changes, inform the user and exit the plan flow. Do not create an empty plan file.
- **User rejects plan entirely**: If the user does not want to proceed with this approach, return to `code.implement` for re-assessment (may switch to small-task path or exit).
- **Plan too large**: If the plan exceeds ~10 steps, ask the user whether to split into multiple independent plans (each producing working, testable code on its own) or proceed with a single large plan. Do not split without user approval.

## Suggested Next
- `code.execute` (after user approves the plan)
