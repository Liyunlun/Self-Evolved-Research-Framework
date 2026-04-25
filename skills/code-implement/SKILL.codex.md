---
name: code-implement
description: Write or modify code with strict TDD discipline. Small tasks are handled by Claude directly (Red-Green-Refactor). Medium/large tasks read `docs/implement_roadmap/YYYY-MM-DD-{name}.md` and are delegated to the `codex:codex-rescue` subagent via the Agent tool, **one roadmap step per foreground invocation** (flags `--write --fresh`; `--background` is opt-in only), using a four-tag per-step prompt contract; Codex runs TDD internally via its own Superpowers. SER framework files always stay with Claude. Triggers on "implement X", "add feature Y", "execute the roadmap", or any code-writing request after a roadmap is ready.
---

# code-implement (Track B — Codex delegated)

**Trigger**: User wants to write new code or modify existing code, in a SER installation where `/codex:rescue` is available.

**Shared context**: Before delegating to Codex, Read `skills/_shared/codex-contract.md` for the prompt contract, invocation rules, background threshold, and error handling.

**Track**: B (Codex executor for medium/large; Claude for small and framework files). Installed via `./scripts/install-skills.sh --codex-track codex`. For Track A semantics (Claude direct TDD everywhere), see `SKILL.claude.md`.

---

## Step 0 — Red Flags (read before acting)

Stop and reconsider if any of these thoughts appear:

| Thought | Reality |
|---------|---------|
| "This is just simple code" | Simple things become complex. Use TDD. |
| "I'll test after" | Tests written after pass immediately, prove nothing. |
| "Should work now" | Not verification. Run the command, read output. |
| "Too simple for review" | All code gets reviewed. No exceptions. |
| "Let me explore first" | TDD IS the exploration. Write a failing test. |
| "3+ fixes failed, let me try once more" | Architecture problem. Stop and discuss. |

---

## Step 1 — Size & Executor Assessment

Two independent dimensions.

### Size

| Signal | Size |
|--------|------|
| Localized change, single file, < ~30 lines of new logic | **Small** |
| New module, multiple files, significant new logic (30–200+ lines) | **Medium/Large** |
| User explicitly requests a plan or design review | **Medium/Large** |

Default to **Small**. When uncertain, ask.

### Executor

| Signal | Executor |
|--------|----------|
| Small size | **Claude** (Codex not invoked for small tasks) |
| Change touches SER framework (`.claude/`, `skills/`, `hooks/`, `config.yaml`, `CLAUDE.md`) | **Claude** (always, regardless of size) |
| `/codex:setup` runtime check fails | **Claude** (graceful degradation — see Step 4e) |
| All other Medium/Large changes | **Codex** |

If size = Medium/Large and no roadmap exists yet, invoke `code-roadmap` first, then return here.

---

## Step 2 — Small task (executor = Claude)

Identical to Track A Step 2. Single RIGID Red-Green-Refactor cycle:

1. **RED**: Write failing test next to source. Confirm it fails for the right reason.
2. **GREEN**: Minimal code to pass.
3. **REFACTOR**: Clean up, keep tests green.

### Rules
- Run tests after every change.
- Baseline existing tests first if any exist.
- "I'll test after" is forbidden.
- Three failed fix attempts → stop, question architecture.

---

## Step 3 — Medium/Large with Framework-File Guard (executor = Claude)

If the roadmap touches SER framework paths listed under Executor signals, Codex must NOT be invoked — Codex's `action_safety` tag forbids those paths anyway. Claude executes the roadmap step-by-step using Track A Step 3 semantics (pre-flight → per-step TDD → Done Criteria).

---

## Step 4 — Medium/Large delegated to Codex

### Step 4a — Pre-flight

1. `git diff --stat` — must be empty. If not, ask user to commit or stash.
2. `git stash list` — note any stashes.
3. `git rev-parse HEAD` — record base SHA.
4. Open `docs/implement_roadmap/YYYY-MM-DD-{name}.md`.
5. Write the base SHA into Status under `Base commit:`. Update `Last updated:`.
6. Runtime Codex check: invoke `/codex:setup`. If it fails (auth expired, service down, CLI missing), jump to **Step 4e** (Claude fallback).

### Step 4b — Per-step prompt template

For each roadmap step `S_i`, build a per-step four-tag prompt. Follow `skills/_shared/codex-contract.md § 2–3`. The four tags in order:

- `<task>` — per-step shape: scope to step `i` only. Includes Goal (full roadmap context, repeated each step), Step.title, Step.purpose, Step.files, Step.what_to_do, Step.acceptance, and the list of already-completed step titles. See contract § 3 for the template.
- `<completeness_contract>` — per-step variant from the contract file: complete this single step, do not attempt other steps.
- `<default_follow_through_policy>` — fixed body.
- `<action_safety>` — fixed body (forbidden paths + no `git commit`/`git push`).

Do not omit any tag. Do not reorder.

### Step 4c — Per-step dispatch loop

Per `skills/_shared/codex-contract.md § 4`, from Claude's main session Codex is ONLY reachable via the `Agent` tool with `subagent_type: "codex:codex-rescue"`. Do NOT call the `Skill` tool with `codex:rescue` and do NOT emit the literal `/codex:rescue ...` slash-command string — both paths return success without spawning a Codex job.

Each roadmap step is dispatched as an **independent foreground codex invocation**. Loop over the roadmap's `## Steps` section in order. For each step `S_i`:

1. Build the per-step four-tag prompt per Step 4b (only `S_i`'s scope + already-completed list).
2. Invoke codex in **foreground** — no `run_in_background` on the Agent, no `--background` in the prompt:
   ```
   Agent({
     subagent_type: "codex:codex-rescue",
     description: "Codex — {short roadmap name} step {i}",
     prompt: "--write --fresh\n\n{per-step four-tag prompt}"
   })
   ```
   Agent blocks while codex runs to completion. For a typical 5–15 min step this is acceptable; the user's main session pauses but resumes immediately when codex finishes.
3. Run per-step post-processing per Step 4d (verify dispatch, run step Acceptance, update Status).
4. Decide continue vs stop:
   - Step Acceptance passed (`[x]`) → continue to `S_{i+1}`.
   - Step Acceptance failed (`[!]`) → **stop**. Surface to user. Do NOT auto-fix; defer to `code-debug` or user direction.

`--write` and `--fresh` are mandatory. The flags can appear anywhere in the `prompt`; the subagent strips them before forwarding to `codex-companion.mjs task`.

**Background flag — opt-in only.** `--background` is opt-in for individual steps that genuinely take >5 min AND the user explicitly authorizes non-blocking dispatch. Default for per-step dispatch is foreground. Background mode has been observed to abort silently with `turn_aborted: interrupted` in some Claude Code SDK contexts (zero work product on disk, companion job state cleared). Foreground is the safer default.

**Do NOT double-background.** Never set `run_in_background: true` on the `Agent` tool while ALSO including `--background` in the prompt — that combination cascades SIGINT to codex within ~5–10 s of Agent return.

### Step 4d — Per-step post-processing

After each `Agent` invocation in the Step 4c loop returns:

1. **Verify dispatch landed.** Sanity-check that codex actually started:
   ```bash
   ls -lt /tmp/codex-companion/*/jobs/ 2>/dev/null | head -5
   ```
   If no job file from this run, the invocation used the wrong channel (see `skills/_shared/codex-contract.md § 5` last row). Re-invoke via `Agent` exactly as shown in Step 4c.
2. **Read codex's per-step report.** Note what it claims completed and any issues raised.
3. **Sanity-check the diff.** `git diff --stat` should show changes only in `S_i`'s declared files; out-of-scope edits are noted, not auto-reverted.
4. **Run step Acceptance.** Execute `S_i`'s Acceptance command from the roadmap. A quick smoke run of the step's test file is fine; the **full Done Criteria suite is reserved for Step 5** after every step is `[x]`.
5. **Update roadmap Status** for `S_i`:
   - `[x]` if Acceptance passed.
   - `[!]` with a one-line note referencing the failure if Acceptance failed.
   Update `Last updated:`.
6. **Do NOT self-fix.** Issues are deferred to `code-debug` or `code-review`.

After all steps are `[x]`, proceed to Step 5 (Done Criteria).

### Step 4e — Claude fallback (Codex unavailable / framework file)

When `/codex:setup` fails, or the roadmap touches framework paths, Claude executes the roadmap step-by-step using Track A Step 3b/3c procedure:

- Per step: RED → GREEN → Acceptance → REFACTOR → Status update.
- After all steps: run each Done Criterion.

Announce the fallback to the user:
```
[code-implement / codex] Codex unavailable — falling back to Claude.
  Cause: {error from /codex:setup}
  Roadmap will still be followed step-by-step.
  To recover Codex path: run /codex:setup, then re-invoke for remaining steps.
```

---

## Step 5 — Done Criteria

After Codex (or fallback Claude) completes all steps:

1. Run each Done Criterion from the roadmap.
2. All pass → flow proceeds to `code-review`.
3. Any fails → mark related step `[!]`, surface to user.

---

## Output

```
[code-implement / codex] {small|roadmap-codex|roadmap-fallback} execution complete
  Executor: {claude | codex}
  Steps: {k}/{K} completed
  Ready for: code-review
```

**Inputs**: User request OR `docs/implement_roadmap/YYYY-MM-DD-{name}.md`; `skills/_shared/codex-contract.md`
**Outputs**: Code + test files; updated roadmap Status; Codex output log (if invoked)
**Token**: ~3-15K (small) / ~4-12K Claude-side for prompt + post-processing (Codex-side usage is separate)
**Composition**:
- Completes → `code-review`
- Codex reports a step blocked, cause unclear → `code-debug`
- Codex unavailable → fallback to Claude (same skill, Step 4e)
