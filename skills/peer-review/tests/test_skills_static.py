#!/usr/bin/env python3
"""
Static lint for all peer-review-* skill directories.

Checks:
  1. Each expected skill directory exists under ~/.claude/skills/.
  2. Each has a SKILL.md with valid YAML frontmatter.
  3. Frontmatter has `name` matching the directory and `description` >= 40 chars.
  4. The orchestrator SKILL.md references every stage skill by name.
  5. shared/ assets exist under the orchestrator skill.
  6. rubric.yaml parses and has entries for all 7 non-orchestrator stages.
"""
from __future__ import annotations

import pathlib
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(2)


SKILLS_ROOT = pathlib.Path.home() / ".claude" / "skills"

ORCHESTRATOR = "peer-review"
STAGE_SKILLS = [
    "peer-review-story",
    "peer-review-presentation",
    "peer-review-evaluations",
    "peer-review-correctness",
    "peer-review-significance",
    "peer-review-critique",
    "peer-review-qa",
]
ALL_SKILLS = [ORCHESTRATOR] + STAGE_SKILLS


def read_frontmatter(skill_md: pathlib.Path) -> dict | None:
    text = skill_md.read_text()
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1]) or {}


def main() -> int:
    errors: list[str] = []

    # 1 + 2 + 3
    for name in ALL_SKILLS:
        d = SKILLS_ROOT / name
        if not d.is_dir():
            errors.append(f"missing skill directory: {d}")
            continue
        s = d / "SKILL.md"
        if not s.is_file():
            errors.append(f"missing SKILL.md: {s}")
            continue
        fm = read_frontmatter(s)
        if fm is None:
            errors.append(f"malformed or missing frontmatter: {s}")
            continue
        if fm.get("name") != name:
            errors.append(f"{s}: frontmatter name={fm.get('name')!r} != dir {name!r}")
        desc = fm.get("description", "")
        if not isinstance(desc, str) or len(desc) < 40:
            errors.append(f"{s}: description too short ({len(desc)} chars, need >=40)")

    # 4: orchestrator references all stage skills
    orch_text = (SKILLS_ROOT / ORCHESTRATOR / "SKILL.md").read_text()
    for stage in STAGE_SKILLS:
        if stage not in orch_text:
            errors.append(f"orchestrator SKILL.md does not reference {stage}")

    # 5: shared assets present
    shared = SKILLS_ROOT / ORCHESTRATOR / "shared"
    for asset in ("base_instruction.md", "review_schema.md",
                  "output_format.md", "rubric.yaml"):
        p = shared / asset
        if not p.is_file():
            errors.append(f"missing shared asset: {p}")

    # 6: rubric contains expected keys
    rubric_path = shared / "rubric.yaml"
    if rubric_path.is_file():
        rubric = yaml.safe_load(rubric_path.read_text()) or {}
        expected = {"story", "presentation", "evaluations", "correctness",
                    "significance", "critique", "qa"}
        missing = expected - set(rubric.keys())
        if missing:
            errors.append(f"rubric.yaml missing stages: {sorted(missing)}")
        for stage, spec in rubric.items():
            if "must_check" not in (spec or {}):
                errors.append(f"rubric.yaml stage '{stage}' missing must_check list")

    if errors:
        print("FAIL: static lint", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(ALL_SKILLS)} skill directories lint-clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
