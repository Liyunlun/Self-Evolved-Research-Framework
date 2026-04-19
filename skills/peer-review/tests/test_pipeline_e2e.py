#!/usr/bin/env python3
"""
End-to-end pipeline smoke test using golden recorded responses.

Simulates the orchestrator flow:
  1. Each of the 7 stage output goldens exists and passes schema/output validation.
  2. The final review (06_final.md) contains all 6 AAAI sections, word-count ok.
  3. QA (07_qa.md) flags the seeded fabricated citation (critical >= 1).
  4. Cross-stage: weaknesses in 06_final.md reflect findings from earlier stages
     (simple check: at least one weakness mentions the word from each earlier stage).
"""
from __future__ import annotations

import pathlib
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(2)

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from test_schema import validate as validate_schema  # noqa: E402
from test_output_format import validate as validate_output  # noqa: E402

FIXTURES = HERE / "fixtures"

STAGE_FILES = [
    ("story",        "golden_01_story.md"),
    ("presentation", "golden_02_presentation.md"),
    ("evaluations",  "golden_03_evaluations.md"),
    ("correctness",  "golden_04_correctness.md"),
    ("significance", "golden_05_significance.md"),
]
FINAL_FILE = "golden_06_final.md"
QA_FILE = "golden_07_qa.md"

# Each stage must leave a recognizable fingerprint in the final weaknesses list
WEAKNESS_FINGERPRINTS = {
    "story":        ["gap", "contribution"],
    "presentation": ["heading", "typo", "caption", "method"],
    "evaluations":  ["1.30", "baseline", "seed", "accuracy"],
    "correctness":  ["dimension", "r^3", "r^2", "equation"],
    "significance": ["nonexistent", "fabricat", "cannot be verified", "hallucinat"],
}


def parse_frontmatter(p: pathlib.Path) -> dict:
    text = p.read_text()
    parts = text.split("---", 2)
    return yaml.safe_load(parts[1]) or {}


def main() -> int:
    errs: list[str] = []

    # 1. Stage goldens schema-pass
    for stage, fname in STAGE_FILES:
        errs_i = validate_schema(FIXTURES / fname, expected_stage=stage)
        if errs_i:
            errs.append(f"{fname}: {errs_i}")

    # QA schema-pass
    qa_errs = validate_schema(FIXTURES / QA_FILE, expected_stage="qa")
    if qa_errs:
        errs.append(f"{QA_FILE}: {qa_errs}")

    # 2. Final review format
    out_errs = validate_output(FIXTURES / FINAL_FILE)
    if out_errs:
        errs.append(f"{FINAL_FILE}: {out_errs}")

    # 3. QA flags at least one [critical]
    qa_fm = parse_frontmatter(FIXTURES / QA_FILE)
    if qa_fm.get("severity_counts", {}).get("critical", 0) < 1:
        errs.append(f"{QA_FILE}: expected critical>=1 for bad-citation fixture")

    # 4. Cross-stage fingerprints present in final review Weaknesses
    final_text = (FIXTURES / FINAL_FILE).read_text().lower()
    weak_block = ""
    if "## weaknesses" in final_text:
        weak_block = final_text.split("## weaknesses", 1)[1]
        nxt = weak_block.find("\n## ")
        if nxt != -1:
            weak_block = weak_block[:nxt]

    for stage, fingerprints in WEAKNESS_FINGERPRINTS.items():
        if not any(fp in weak_block for fp in fingerprints):
            errs.append(
                f"final review Weaknesses does not reflect stage '{stage}' "
                f"(none of {fingerprints} found)"
            )

    if errs:
        print("FAIL: E2E pipeline", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK: E2E pipeline — 7 stages schema-valid, 6 AAAI sections present, "
          "QA critical>=1, all stage fingerprints in final review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
