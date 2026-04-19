#!/usr/bin/env python3
"""
Negative tests: verify validators REJECT malformed inputs.

These guarantee the contracts are actually enforced, not vacuously passed.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from test_schema import validate as validate_schema   # noqa: E402
from test_output_format import validate as validate_output  # noqa: E402


BAD_FINDINGS_NO_FRONTMATTER = """## Findings
- [major] something
## Evidence citations
## Open questions
"""

BAD_FINDINGS_COUNT_MISMATCH = """---
stage: story
paper_id: x
model_notes: "n"
severity_counts:
  critical: 0
  major: 2
  minor: 0
---
## Findings
- [major] one issue
## Evidence citations
- x
## Open questions
- none
"""

BAD_FINAL_MISSING_STRENGTHS = """# A Title For The Review Of Some Paper

## Synopsis
This paper claims things. Overall the work raises substantive concerns but is interesting in parts.

## Summary
A longer paragraph summarizing the contributions of this paper across method and experiments, describing the proposed approach and the empirical evidence offered. """ + ("This is padding to reach 400 words. " * 60) + """

## Weaknesses
- [critical] An issue that should be taken seriously in the weaknesses list.

## References
None.
"""

BAD_FINAL_UNTAGGED_WEAKNESS = """# Review Title Here

## Synopsis
Short synopsis sentence.

## Summary
""" + ("Summary words. " * 80) + """

## Strengths
- A strength bullet.

## Weaknesses
- An untagged weakness with no severity marker.

## References
None.
"""


def main() -> int:
    errs: list[str] = []

    with tempfile.TemporaryDirectory() as d:
        td = pathlib.Path(d)

        # (1) findings file without frontmatter must fail
        f1 = td / "bad1.md"; f1.write_text(BAD_FINDINGS_NO_FRONTMATTER)
        if not validate_schema(f1):
            errs.append("schema validator wrongly ACCEPTED file with no frontmatter")

        # (2) severity_counts mismatch must fail
        f2 = td / "bad2.md"; f2.write_text(BAD_FINDINGS_COUNT_MISMATCH)
        if not validate_schema(f2):
            errs.append("schema validator wrongly ACCEPTED count mismatch")

        # (3) final review missing Strengths must fail
        f3 = td / "bad3.md"; f3.write_text(BAD_FINAL_MISSING_STRENGTHS)
        if not validate_output(f3):
            errs.append("output validator wrongly ACCEPTED review missing Strengths")

        # (4) final review with untagged weakness bullet must fail
        f4 = td / "bad4.md"; f4.write_text(BAD_FINAL_UNTAGGED_WEAKNESS)
        if not validate_output(f4):
            errs.append("output validator wrongly ACCEPTED untagged weakness bullet")

    if errs:
        print("FAIL: negative tests", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: 4 negative cases rejected as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
