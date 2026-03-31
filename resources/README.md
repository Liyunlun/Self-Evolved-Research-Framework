# Resources — Reference Materials

All external reference materials live here. When a micro-skill needs to look up
a paper, inspect a codebase, or cite prior work, it should look in this directory first.

## Structure

- `papers/` — Paper reading notes (markdown with YAML frontmatter)
- `repos/` — Cloned or linked reference repositories (related projects, baselines, tools)

## Papers (`papers/`)

Paper reading notes use markdown with YAML frontmatter.
See CLAUDE.md § Paper Notes for the schema.

### Reading Rules
- Read Quick Reference section first; only read full notes if deeper understanding needed
- For deep reading, use `/fey-r` (Feynman-technique interactive reading)
- After fey-r completes, prepend a Quick Reference section to the notes

### When to create a paper note
- After `paper.read` completes on a new paper
- When citing a paper in `writing.draft` and no note exists yet
- When `idea.verify` identifies a relevant existing paper

## Repos (`repos/`)

Reference repositories for code inspection, baseline comparison, or tool usage.

### Convention
- Clone with `git clone --depth 1` to save space (shallow clone)
- Each repo gets its own subdirectory: `repos/{repo-name}/`
- If a repo is too large, add only the relevant files or a README linking to the source

### When to reference repos
- `paper.read` on a paper with a code release → clone to `repos/`
- `experiment.run` needs a baseline implementation → check `repos/` first
- `idea.verify` needs to inspect how an existing system works → clone to `repos/`
- `writing.draft` needs to describe an implementation detail → read from `repos/`

## Lookup Order

When a micro-skill needs external reference:
1. Check `resources/papers/` for existing reading notes
2. Check `resources/repos/` for cloned codebases
3. If not found, fetch/clone and add to the appropriate subdirectory

## Docs (`docs/`)

Supporting documentation generated during the research lifecycle.

- `docs/plans/` — Experiment and implementation plans
- `docs/reports/` — Progress reports and summaries
