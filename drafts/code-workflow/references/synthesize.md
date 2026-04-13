# code.synthesize

**Trigger**: Both Review A (Claude plan compliance) and Review B (Codex code quality) are completed for a plan-based implementation.

Claude reads both reviews, decides whether to pass or loop, and manages the fix cycle.

## Process

### 1. Read Both Reviews

Lay out the findings side by side:

| Source | Finding | Severity | Category |
|--------|---------|----------|----------|
| Claude | {finding from Review A} | {critical/important/minor} | plan compliance |
| Codex | {finding from Review B} | {critical/important/minor} | code quality |

### 2. Classify Each Finding

| Pattern | Interpretation | Action |
|---------|---------------|--------|
| Both reviewers flag the same issue | High-confidence real problem | Must fix |
| Only Claude flags: acceptance criteria not met | Plan compliance gap | Must fix |
| Only Claude flags: unplanned changes | Scope concern | Assess: was it justified? If yes, note and pass. If no, must fix. |
| Only Codex flags: logic/security/edge case | Code quality issue | Fix if critical/important. Note if minor. |
| Contradictory findings | Disagreement | Analyze evidence from both sides. Decide based on which has stronger grounding. |
| Neither flags issues | Clean | Pass |

### 3. Decision

#### PASS — proceed to commit

All of the following must be true:
- All Done Criteria from the plan pass
- No critical or important findings remain unfixed
- Both reviewers agree (or remaining disagreements are minor and assessed)

**Action**: proceed to `code.commit`.

#### FIX NEEDED — update plan and loop

One or more critical/important findings remain.

**Action**:

#### Step 3a: Update the Plan File

Open `implementation_plans/YYYY-MM-DD-{name}.md` and update the Status section:

```markdown
## Status

- [x] Step 1: {title} — completed
- [x] Step 2: {title} — completed
- [!] Step 3: {title} — needs adjustment: {brief description of issue}
- [ ] Step 4: {title} — not yet attempted

### Fix Steps (Round 2)

- [ ] Fix 3a: {title}
  - Purpose: {why this fix is needed}
  - Files: {which files to modify}
  - What to do: {concrete description}
  - Acceptance: {how to verify the fix}
- [ ] Fix 3b: {title}
  - Purpose: ...
  - Files: ...
  - What to do: ...
  - Acceptance: ...

- **Round**: 2 (max 3 auto, then ask user)
- **Last updated**: {YYYY-MM-DD}
- **Issues from Round 1**:
  - {Claude: finding description}
  - {Codex: finding description}
```

Rules for updating the plan:
- Mark completed steps with `[x]` — do NOT modify their content.
- Mark steps needing adjustment with `[!]` and describe the issue.
- Add new "Fix Steps" for the current round, each with Purpose, Files, What to do, Acceptance — same format as original steps.
- Keep the original Goal unchanged. The goal does not change between rounds.
- Increment the Round counter.
- Record which issues triggered this round.

#### Step 3b: Loop back to execute

Proceed to `code.execute` with the updated plan. The execute phase will use `--resume` to continue the Codex thread.

### 4. Round Tracking

| Round | Action |
|-------|--------|
| 1 | Initial execution + review |
| 2 | First fix cycle — auto-proceed |
| 3 | Second fix cycle — auto-proceed |
| 4+ | **STOP**. Must get user approval before continuing. |

Maximum 3 execution rounds (1 initial + 2 fix cycles) without user intervention. When round > 3, present this to the user:

```
This plan has gone through 3 fix rounds without fully passing review.

Completed so far:
- {list of completed steps}

Remaining issues:
- {list of outstanding findings}

Options:
1. Continue with another fix round
2. Claude takes over and fixes remaining issues directly
3. Revise the plan (start a fresh plan with adjusted approach)
4. Stop here and commit what we have
```

Wait for user's choice before proceeding.

### 5. Final Verification (Before Commit)

When all reviews pass, before handing off to `code.commit`:

1. Run the full test command from the plan: `{test command}` — must pass.
2. Run each Done Criteria check — must pass.
3. Run `git diff --stat` — present the full change summary to the user.
4. Confirm: "All Done Criteria pass. Ready to commit. Proceed?"

## Suggested Next
- `code.commit` (if pass)
- `code.execute` (if fix needed, round ≤ 3)
- Ask user (if round > 3)
