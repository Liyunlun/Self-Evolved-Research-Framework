# code.execute

**Trigger**: Plan approved by user, ready for Codex implementation.

Codex receives the plan and implements it autonomously using Superpowers (TDD, sub-planning, step-level review). Claude's job here is to construct a clear prompt and hand off.

## Process

### 1. Record Starting State

Before calling Codex, capture the baseline so review can diff against it:

```bash
git stash list          # note any stashes
git diff --stat         # should be clean; if not, stash or commit first
git rev-parse HEAD      # record the base commit SHA
```

If the working tree is dirty, ask the user to commit or stash first.

**Write the base commit SHA into the plan file's Status section** (the `Base commit` field). This is needed by `code.review` to diff against.

### 2. Construct the Rescue Prompt

The prompt has two parts: an **inline summary** (what Codex sees immediately) and a **plan file reference** (detailed spec Codex reads from disk).

#### Prompt Template — First Execution (Round 1)

```
<task>
Implement the feature described below. The full implementation plan is at
{plan_path} — read it first before writing any code.

Goal: {copy the Goal line from the plan}

Key files to read for context:
- {path} — {role}
- {path} — {role}

Steps overview:
1. {Step 1 title}: {one-line summary of what to do}
2. {Step 2 title}: {one-line summary of what to do}
...

Test command: {test command from plan}

After completing all steps, run the full test suite and the Done Criteria
checks listed in the plan. Report which steps passed and which failed.
</task>

<completeness_contract>
Complete ALL steps listed in the plan file. Do not stop after partial
implementation. For each step, verify its Acceptance criteria before
moving to the next step. After all steps, verify the Done Criteria.
</completeness_contract>

<default_follow_through_policy>
Keep going until all steps are done and verified. Only stop to ask
if a missing dependency or genuinely ambiguous requirement would
change the correctness of the implementation.
</default_follow_through_policy>

<action_safety>
Do not modify: .claude/, skills/, memory/, hooks/, config.yaml, CLAUDE.md
Do not run git commit or git push.
Focus on files listed in the plan. If you need to modify other files
to complete the task, proceed carefully and note the changes.
</action_safety>
```

**Filling the template:**
- `{plan_path}`: the full path, e.g., `implementation_plans/2026-04-13-config-parser.md`
- `{Goal}`: copy verbatim from plan's Goal section
- `{Key files}`: copy from plan's Context section (the files Codex should read first)
- `{Steps overview}`: one line per step — title + brief summary only
- `{Test command}`: copy from plan's Context section

#### Prompt Template — Fix Rounds (Round 2, 3)

For fix rounds, use `--resume` to continue the existing Codex thread:

```
<task>
The plan at {plan_path} has been updated after review. Read the updated
Status section to see which steps are completed [x] and which need
adjustment [!].

Issues found in review:
{paste the specific issues from synthesize, one per line}

Fix the marked issues and re-verify. Run the Done Criteria checks
after all fixes are applied.
</task>

<completeness_contract>
Address ALL issues listed above. Do not stop after fixing only some.
Re-run acceptance checks for every modified step.
After fixes, run the full test suite and Done Criteria.
</completeness_contract>

<action_safety>
Do not modify: .claude/, skills/, memory/, hooks/, config.yaml, CLAUDE.md
Do not run git commit or git push.
Focus on files listed in the plan. If you need to modify other files
to complete the task, proceed carefully and note the changes.
</action_safety>
```

### 3. Call Rescue

**Round 1 (fresh):**
```
/codex:rescue --write --fresh "{constructed prompt}"
```

**Round 2+ (resume):**
```
/codex:rescue --write --resume "{constructed fix prompt}"
```

**Background vs foreground:**
- Plan with ≤ 3 steps or estimated < 5 minutes → foreground (default)
- Plan with > 3 steps or estimated > 5 minutes → add `--background`
- When using `--background`, inform the user that Codex is working and they can continue other tasks

### 4. Receive and Record Results

After Codex completes:

1. **Read Codex output** — note which steps it reports as completed, any issues encountered, any files modified outside the plan.
2. **Quick sanity check** — run `git diff --stat` to see what changed. This is NOT the review — just a quick look to confirm Codex did something reasonable.
3. **Do NOT fix issues yourself** — if Codex reports problems, they will be addressed in the review → synthesize → fix cycle.

## Error Handling

| Situation | Action |
|-----------|--------|
| Codex reports it cannot find the plan file | Check the path. Re-run with corrected path. |
| Codex times out or crashes | Report to user. Offer: retry with `--resume`, or Claude implements directly. |
| Codex reports missing dependency | Update the plan's Constraints section, ask user to install, then `--resume`. |
| Codex modifies files outside plan scope | Note for review phase. Not necessarily wrong — Codex may have had good reason. |
| Codex unavailable (auth expired, service down) | Report to user. Offer: (1) Claude implements the remaining steps directly using small-task TDD, or (2) wait and retry later. |

## Dependencies

This skill requires:
- `/codex:rescue` — Codex CLI rescue command (from `codex-plugin-cc`). Supports flags: `--write` (enable file writes), `--fresh` (new thread), `--resume` (continue previous thread), `--background` (async execution). Must be installed and authenticated. Check with `/codex:setup` if unavailable.
- Codex must have Superpowers skills installed at `~/.agents/skills/superpowers/` for automatic TDD, sub-planning, and step-level review.

## Suggested Next
- `code.review`
