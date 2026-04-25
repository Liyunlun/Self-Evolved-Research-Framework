# Codex Contract — Shared Infrastructure (Track B Only)

> Shared reference for **codex-track** variants of `code-implement` and
> `code-review`. Defines the prompt contract for calling Codex, the
> correct invocation channel from Claude's main session, the
> forbidden-path list, background threshold, error handling, and external
> dependencies.
>
> Not a skill itself (no `SKILL.md`). The codex-track SKILL.md files
> (`code-implement/SKILL.codex.md`, `code-review/SKILL.codex.md`) direct
> Claude to read this file before calling Codex.
>
> **This file is only installed on Track B (`--codex-track codex`).**
> Track A installations (Claude-only) do not include it and do not reference
> it.

---

## 1. Dependencies

Track B installation REQUIRES all of:

- **Codex rescue runtime** — from `codex-plugin-cc`.
  - User-facing slash command: `/codex:rescue` (supports `--write`,
    `--fresh`, `--resume`, `--background`). This is for human input.
  - **Claude-side callable: the `codex:codex-rescue` subagent invoked
    via the `Agent` tool.** SER skills always go through this path — see
    §4 for why the `Skill` tool and the raw slash-command string do
    NOT work from Claude's main session.
  - Both paths funnel into the same `scripts/codex-companion.mjs task`
    runner. Must be authenticated (verified at install via
    `/codex:setup`).
- **Codex review runtime** — from `codex-plugin-cc`.
  - User-facing slash command: `/codex:review`.
  - Claude-side callable: direct `Bash` to
    `scripts/codex-companion.mjs review` (no dedicated subagent
    exists). Path resolution is shown in `code-review/SKILL.codex.md § 3`.
- Codex-side Superpowers at `~/.agents/skills/superpowers/` — Codex needs
  its own TDD / planning / review skills loaded. Verified at install.

If any of the above becomes unavailable at runtime, the calling skill must
degrade gracefully (see §5 Error Handling).

---

## 2. Prompt Contract

Every Codex invocation from SER uses four XML-like tags in this order.
Do not omit any tag. Do not reorder.

```
<task>
{what to do — concrete, anchored to the roadmap file}
</task>

<completeness_contract>
{what counts as done — every step + Done Criteria verified}
</completeness_contract>

<default_follow_through_policy>
{when to keep going vs when to stop and ask}
</default_follow_through_policy>

<action_safety>
{forbidden modifications, forbidden commands}
</action_safety>
```

---

## 3. Standard Tag Bodies

### `<task>` template (per-step)

Each codex invocation is for a **single roadmap step**. The orchestrator
loops over the roadmap's `## Steps` and dispatches one codex job per step.
The `<task>` body for step `S_i` is:

```
Implement Step {i} of the roadmap at {roadmap_path}. Read the roadmap once
to understand context, then focus only on Step {i}.

Roadmap goal (full context, applies to all steps): {Goal}

Step {i} title: {Step.title}
Step {i} purpose: {Step.purpose}
Step {i} files: {Step.files}
Step {i} what-to-do: {Step.what_to_do}
Step {i} acceptance: {Step.acceptance}

Already-completed steps in this roadmap (do NOT re-implement):
{list of [x] step titles}

Test command for the whole roadmap: {test_command}
After completing Step {i}, run only Step {i}'s acceptance command, plus a
quick `pytest <step_i_test_file>` smoke. Do NOT run the full Done Criteria
suite — that is the orchestrator's job after all steps complete.
```

**Fill rules**
- `{roadmap_path}`: full path, e.g., `docs/implement_roadmap/2026-04-21-config-parser.md`.
- `{i}`: 1-indexed step number from the roadmap's `## Steps` section.
- `{Goal}`: copy verbatim from roadmap's Goal section. Same value for every step in the loop.
- `{Step.title}`, `{Step.purpose}`, `{Step.files}`, `{Step.what_to_do}`, `{Step.acceptance}`: copy from the roadmap's Step `i` block.
- `{list of [x] step titles}`: titles of all roadmap steps already marked `[x]` in this run. Write `none` (or omit the line) for the first invocation in the loop.
- `{test_command}`: copy from roadmap's Context § Test command.
- `{step_i_test_file}`: the test file mentioned in Step `i`'s Files section, if any. Omit the smoke line if no test file applies.

### `<completeness_contract>` body (fixed text, per-step)

```
Complete the single roadmap step described in <task>. Do not stop after
partial implementation of this step. Verify the step's Acceptance criteria
before reporting completion. Do NOT attempt other steps in the roadmap —
they are dispatched separately by the orchestrator.
```

### `<default_follow_through_policy>` body (fixed text)

```
Keep going until all steps are done and verified. Only stop to ask if a
missing dependency or genuinely ambiguous requirement would change the
correctness of the implementation.
```

### `<action_safety>` body (fixed text)

```
Do not modify any of:
  .claude/, skills/, memory/, hooks/, config.yaml, CLAUDE.md
Do not run `git commit` or `git push`.
Focus on files listed in the roadmap. If a file outside the roadmap must be
modified to complete the task, proceed carefully and note the change in your
final report.
```

---

## 4. Invocation

### Channel — Agent tool, not Skill tool, not bare slash-command text

From Claude's main session, Codex MUST be invoked through the `Agent` tool
with `subagent_type: "codex:codex-rescue"`. The following look-alikes all
fail silently (they return success but create no job under
`/tmp/codex-companion/*/jobs/` and produce no entries in
`~/.codex/log/codex-tui.log`):

- ❌ `Skill` tool with `skill: "codex:rescue"` — the Skill tool only
  renders the slash-command body as instruction text. The slash-command's
  `context: fork` + `allowed-tools: Bash(node:*)` only fire when a human
  user types `/codex:rescue` directly in the chat. Claude invoking it via
  `Skill` does NOT fork and does NOT execute the Bash call.
- ❌ Emitting the literal string `/codex:rescue --write --fresh ...` in
  Claude's response — that is human input syntax, not a tool call.
- ❌ Direct `Bash` to `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" task ...`
  — `CLAUDE_PLUGIN_ROOT` is not set in Claude's main-session shell, so the
  path resolves to `/scripts/codex-companion.mjs` and the call fails.
  Subagents defined inside the codex plugin DO have `CLAUDE_PLUGIN_ROOT`
  set, which is why the `Agent` path works.

### Per-step dispatch loop

Codex receives ONE roadmap step per `Agent` invocation. The orchestrator
(Claude's main session) loops over the roadmap's `## Steps`, dispatching
each `S_i` independently. Per-step dispatch keeps blast radius small and
recoverable: a failure on `S_i` leaves `S_1..S_{i-1}` validated and the
failure localized to one step.

For each step `S_i`:

```
Agent({
  subagent_type: "codex:codex-rescue",
  description: "Codex — {short roadmap name} step {i}",
  prompt: "--write --fresh --background\n\n{per-step four-tag prompt for S_i}"
})
```

- `--write` is mandatory. Without it, Codex runs read-only.
- `--fresh` is mandatory. Each per-step dispatch is a clean codex thread;
  no `--resume`. Loop continuity is maintained by the orchestrator's
  per-step prompt (which lists already-completed steps), not by codex
  thread state.
- `--background` is the default. The `codex:codex-rescue` subagent passes
  this flag through to `codex-companion.mjs task --background`, which
  spawns a detached worker process (PPID=1, own PGID/SID) that survives
  subagent cleanup. The orchestrator polls for completion before
  dispatching `S_{i+1}`.
- The flags may appear anywhere in the `prompt`. The `codex:codex-rescue`
  subagent passes `--background`, `--write`, `--fresh` through to
  `codex-companion.mjs task` as command-line flags, and strips `--resume`
  / `--fresh` from the task text.

### Background execution model

`--background` tells the companion to spawn a **detached worker** that
runs independently of the parent process tree. The worker completes even
if the subagent or parent session ends. After dispatching a step, the
orchestrator must poll for completion before dispatching the next step:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" status {task-id}
```

Or check the job's log file for "Turn completed" / "Turn failed".

**Foreground alternative.** Omit `--background` to have the `Agent` call
block until codex finishes (typically 5–15 min per step). Use foreground
when the orchestrator has no other work to do while waiting.

**Plugin requirement.** The `codex:codex-rescue` agent definition must
treat `--background` as a companion-level flag, not a routing control.
If the subagent strips `--background` and sets `run_in_background: true`
on its Bash call instead, the SDK will kill the foreground companion
process when the subagent finishes, aborting the codex turn. This was
the root cause of `turn_aborted: interrupted` failures observed before
2026-04-25. The fix is in the plugin's `agents/codex-rescue.md`.

---

## 5. Error Handling

| Situation | Action |
|---|---|
| Codex reports it cannot find the roadmap file | Verify path. Re-run with corrected path in the `<task>` body. |
| Codex times out or crashes | Report to user. Offer: (a) retry with same prompt, (b) Claude implements directly using Track A fallback procedure. |
| Codex reports missing dependency | Update roadmap's Constraints section noting the dependency, ask user to install, then re-invoke (fresh, not resume). |
| Codex modifies files outside roadmap scope | Note for `code-review` phase. Not automatically wrong — Codex may have had good reason. Review decides. |
| `/codex:setup` check fails at runtime | Degrade to Claude direct TDD for this task. Follow the roadmap step-by-step using Track A semantics. Notify user with the failure reason and recovery hint (`/codex:setup` to re-auth). |
| Roadmap touches `.claude/` `skills/` `hooks/` `config.yaml` `CLAUDE.md` | Never send to Codex regardless of track. Claude handles these directly. |
| Invocation reports success but `ls -lt /tmp/codex-companion/*/jobs/ \| head` shows no new job file for this run, AND `~/.codex/log/codex-tui.log` has no new entries since the call | Wrong invocation channel. You called `Skill: codex:rescue` or emitted `/codex:rescue ...` as text instead of using `Agent(subagent_type: "codex:codex-rescue")`. See §4 for the only working channel from Claude's main session. Do NOT retry the same channel; re-invoke via `Agent`. |

---

## 6. Post-Invocation (per step)

After each per-step `Agent` invocation returns control:

1. **Verify dispatch landed.** Sanity-check that codex actually started
   this step (see § 5 last row for the failure-mode signature).
2. **Read codex's per-step report.** Note completion status of the single
   dispatched step, any issues raised, any files modified outside `S_i`'s
   declared scope.
3. **Sanity check.** `git diff --stat` to confirm codex produced changes
   for `S_i`'s files. This is NOT a review — just a smoke test.
4. **Do NOT self-fix.** Any issues found by codex, or any concerns, are
   deferred to the next phase (`code-review` or `code-debug`). Do not
   patch silently.
5. **Update roadmap Status** for the dispatched step: `[x]` if Acceptance
   passed, `[!]` with a one-line note if it failed. (Single-round only;
   no Fix Steps section appended.)

The full Done Criteria suite runs only after every roadmap step is `[x]`,
not after each individual step.
