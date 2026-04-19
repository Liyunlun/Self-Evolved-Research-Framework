#!/usr/bin/env python3
"""
For each stage 01-07, verify the golden fixture findings file:
  (a) passes schema validation (schema conformance)
  (b) contains the expected [severity] flag for the seeded flaw in expected_flaws.yaml

This is the "stage unit test": given a hermetic recorded response (golden file),
we assert the contract the stage skill is required to satisfy.
"""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(2)

# Reuse schema validator
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from test_schema import validate as validate_schema  # noqa: E402

FIXTURES = HERE / "fixtures"

STAGE_TO_GOLDEN = {
    "story":         "golden_01_story.md",
    "presentation":  "golden_02_presentation.md",
    "evaluations":   "golden_03_evaluations.md",
    "correctness":   "golden_04_correctness.md",
    "significance":  "golden_05_significance.md",
    "qa":            "golden_07_qa.md",
}


def main() -> int:
    errors: list[str] = []

    expected = yaml.safe_load((FIXTURES / "expected_flaws.yaml").read_text())

    for stage, fname in STAGE_TO_GOLDEN.items():
        path = FIXTURES / fname
        if not path.is_file():
            errors.append(f"{stage}: golden file missing: {path}")
            continue

        # (a) schema conformance
        schema_errs = validate_schema(path, expected_stage=stage)
        if schema_errs:
            errors.append(f"{stage}: schema errors in {path.name}: {schema_errs}")
            continue

        # (b) expected severity + pattern
        text = path.read_text().lower()
        for spec in expected.get(stage, []):
            sev = spec["severity"]
            pat = spec["pattern"].lower()
            # Look for the severity tag with a matching pattern nearby.
            # Simple heuristic: find any line starting with "- [sev]" and check pattern
            #  in that line or the next line (Detail continuation).
            lines = text.splitlines()
            hit = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"- [{sev}]"):
                    window = line
                    # Include up to next 3 lines of detail
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if lines[j].strip().startswith("- ["):
                            break
                        window += " " + lines[j]
                    if re.search(pat, window):
                        hit = True
                        break
            if not hit:
                errors.append(
                    f"{stage}: expected [{sev}] finding matching /{pat}/ not present "
                    f"in {path.name}"
                )

    if errors:
        print("FAIL: stage findings tests", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(STAGE_TO_GOLDEN)} stage findings match expected flaws")
    return 0


if __name__ == "__main__":
    sys.exit(main())
