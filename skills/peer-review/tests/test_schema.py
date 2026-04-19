#!/usr/bin/env python3
"""
Validate a findings file against shared/review_schema.md.

Usage:
    python test_schema.py <findings_file.md> [--stage <name>]

Exit codes:
    0 = pass
    1 = fail (prints the first error)
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


VALID_STAGES = {"story", "presentation", "evaluations", "correctness",
                "significance", "critique", "qa"}
REQUIRED_SECTIONS = ["## Findings", "## Evidence citations", "## Open questions"]
SEVERITY_TAG = re.compile(r"^-\s*\[(critical|major|minor)\]")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("missing YAML frontmatter (file must start with '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("malformed YAML frontmatter (no closing '---')")
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


def validate(path: pathlib.Path, expected_stage: str | None = None) -> list[str]:
    errs: list[str] = []
    text = path.read_text()

    try:
        fm, body = split_frontmatter(text)
    except ValueError as e:
        return [str(e)]

    # frontmatter checks
    for key in ("stage", "paper_id", "model_notes", "severity_counts"):
        if key not in fm:
            errs.append(f"frontmatter missing key: {key}")

    stage = fm.get("stage")
    if stage not in VALID_STAGES:
        errs.append(f"invalid stage '{stage}' (must be one of {sorted(VALID_STAGES)})")
    if expected_stage and stage != expected_stage:
        errs.append(f"stage '{stage}' != expected '{expected_stage}'")

    sc = fm.get("severity_counts", {})
    if not isinstance(sc, dict):
        errs.append("severity_counts must be a mapping")
        sc = {}
    for k in ("critical", "major", "minor"):
        if k not in sc:
            errs.append(f"severity_counts missing key: {k}")
        elif not isinstance(sc[k], int) or sc[k] < 0:
            errs.append(f"severity_counts.{k} must be a non-negative int")

    # required sections present
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errs.append(f"missing required section header: {section}")

    # Parse bullets under ## Findings to count severities
    findings_block = ""
    if "## Findings" in body:
        after = body.split("## Findings", 1)[1]
        # up to next ## heading
        next_idx = after.find("\n## ")
        findings_block = after if next_idx == -1 else after[:next_idx]

    counted = {"critical": 0, "major": 0, "minor": 0}
    for line in findings_block.splitlines():
        m = SEVERITY_TAG.match(line.strip())
        if m:
            counted[m.group(1)] += 1

    declared = {k: sc.get(k, 0) for k in counted}
    if counted != declared:
        errs.append(
            f"severity_counts mismatch: declared={declared}, counted-in-findings={counted}"
        )

    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=pathlib.Path)
    ap.add_argument("--stage", default=None)
    args = ap.parse_args()

    if not args.path.exists():
        print(f"FAIL: file not found: {args.path}", file=sys.stderr)
        return 1

    errs = validate(args.path, args.stage)
    if errs:
        print(f"FAIL: {args.path}", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
