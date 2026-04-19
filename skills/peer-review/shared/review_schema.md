# Findings File Schema

Every stage output file MUST begin with this YAML frontmatter, followed by the three required sections below.

## YAML Frontmatter (required)

```yaml
---
stage: <story|presentation|evaluations|correctness|significance|critique|qa>
paper_id: <slug>
model_notes: <one-line note on what the stage did, e.g., "ran 3 code snippets, all reproduced">
severity_counts:
  critical: <int>
  major: <int>
  minor: <int>
---
```

## Required sections (in order)

```markdown
## Findings

- [critical] <one-line issue> (evidence: §X.Y or Fig N or Eq K)
  Detail: <2-4 lines expanding the issue, what the paper says, why it's wrong>
- [major] ...
- [minor] ...

## Evidence citations

- <paper-internal refs used, one per line>

## Open questions

- <any question to the authors, or "none">
```

## Parsing rules

- The orchestrator uses a simple YAML parser (`yaml.safe_load`) on the frontmatter block.
- `severity_counts` must match the number of `[critical]`, `[major]`, `[minor]` bullets in the Findings section. The static test verifies this.
- If a stage finds no issues, emit one bullet: `- [minor] No substantive issues detected in this dimension.` and set counts accordingly.

## File naming

Written by the orchestrator as:
`outputs/peer-review/<paper_id>/<NN>_<stage>.md`
where NN is the zero-padded stage index (01 story ... 07 qa).
