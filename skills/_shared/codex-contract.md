# Codex Contract — Shared Infrastructure (Track B Only)

> Shared reference for **codex-track** variants of `code-implement` and
> `code-review`. Defines the prompt contract for calling `/codex:rescue`,
> the forbidden-path list, background threshold, error handling, and
> external dependencies.
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

- `/codex:rescue` — from `codex-plugin-cc`. Supports flags `--write`,
  `--fresh`, `--resume`, `--background`. Must be authenticated (verified
  at install via `/codex:setup`).
- `/codex:review` — from `codex-plugin-cc`. Runs Codex against local git
  state.
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

### `<task>` template

```
Implement the feature described below. The full implementation roadmap is at
{roadmap_path} — read it first before writing any code.

Goal: {copy the Goal line from the roadmap verbatim}

Key files to read for context:
- {path} — {role}
- {path} — {role}

Steps overview:
1. {Step 1 title}: {one-line summary}
2. {Step 2 title}: {one-line summary}
...

Test command: {test command from roadmap Context}

After completing all steps, run the full test suite and the Done Criteria
checks listed in the roadmap. Report which steps passed and which failed.
```

**Fill rules**
- `{roadmap_path}`: full path, e.g., `docs/implement_roadmap/2026-04-21-config-parser.md`.
- `{Goal}`: copy verbatim from roadmap's Goal section.
- `{Key files}`: copy from roadmap's Context § Key files.
- `{Steps overview}`: one line per step — title + brief summary only. Do
  NOT inline the full Files / What to do / Acceptance; Codex reads those
  from the roadmap file.
- `{Test command}`: copy from roadmap's Context § Test command.

### `<completeness_contract>` body (fixed text)

```
Complete ALL steps listed in the roadmap file. Do not stop after partial
implementation. For each step, verify its Acceptance criteria before moving
to the next step. After all steps, verify the Done Criteria.
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

### Single invocation, no loop

```
/codex:rescue --write --fresh "{full four-tag prompt}"
```

- `--write` is mandatory. Without it, Codex reads-only.
- `--fresh` is mandatory. SER has no loop; each code-implement run is a
  fresh thread.
- `--resume` is **not used** in this contract (loop removed from SER
  workflow).

### Background threshold

| Signal | Flag |
|---|---|
| Roadmap has ≤ 3 steps OR estimated < 5 min | foreground (default) |
| Roadmap has > 3 steps OR estimated > 5 min | add `--background` |

When using `--background`, the calling skill must inform the user that
Codex is working and the session can continue with other tasks. Codex
result is collected later.

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

---

## 6. Post-Invocation

After Codex returns control:

1. **Read Codex output.** Note which steps it reports completed, any issues,
   any files modified outside the roadmap scope.
2. **Sanity check:** `git diff --stat` to confirm Codex produced changes.
   This is NOT a review — just a smoke test.
3. **Do NOT self-fix.** Any issues found by Codex, or any concerns, are
   deferred to the next phase (`code-review`). Do not patch silently.
4. **Update roadmap Status.** Mark completed steps `[x]`. Mark steps with
   Codex-reported failures `[!]` with a one-line note referencing the
   Codex output. (Single-round only; no Fix Steps section appended.)
