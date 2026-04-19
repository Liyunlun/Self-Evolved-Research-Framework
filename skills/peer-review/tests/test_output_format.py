#!/usr/bin/env python3
"""
Validate a final review file against shared/output_format.md (AAAI format).

Required: exactly one '# <title>' (h1), and five '## <heading>' sections in order:
Synopsis, Summary, Strengths, Weaknesses, References.
Each Weakness bullet must carry [critical]/[major]/[minor] severity.

Usage:
    python test_output_format.py <final_review.md>
"""
from __future__ import annotations

import pathlib
import re
import sys

REQUIRED_ORDER = ["## Synopsis", "## Summary", "## Strengths", "## Weaknesses", "## References"]
WEAK_BULLET = re.compile(r"^-\s*\[(critical|major|minor)\]")


def validate(path: pathlib.Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text()
    lines = text.splitlines()

    # Exactly one h1 as title at top
    h1s = [i for i, l in enumerate(lines) if l.startswith("# ") and not l.startswith("## ")]
    if len(h1s) != 1:
        errs.append(f"expected exactly 1 H1 title line, found {len(h1s)}")
    elif h1s[0] > 2:
        errs.append("H1 title must be near the top of the file")

    # Ordered presence of the five ## sections
    positions = []
    for header in REQUIRED_ORDER:
        if header not in text:
            errs.append(f"missing required section: {header}")
            positions.append(-1)
        else:
            positions.append(text.index(header))

    ordered_positions = [p for p in positions if p >= 0]
    if ordered_positions != sorted(ordered_positions):
        errs.append("required sections are out of order")

    # Every weakness bullet must be severity-tagged
    if "## Weaknesses" in text:
        tail = text.split("## Weaknesses", 1)[1]
        next_idx = tail.find("\n## ")
        weak_block = tail if next_idx == -1 else tail[:next_idx]
        bullets = [l for l in weak_block.splitlines() if l.strip().startswith("-")]
        untagged = [l for l in bullets if not WEAK_BULLET.match(l.strip())]
        if untagged:
            errs.append(
                f"{len(untagged)} weakness bullet(s) missing severity tag: "
                f"{untagged[0][:80]!r}"
            )
        if not bullets:
            errs.append("Weaknesses section has no bullets")

    # Word count 400..1500
    wc = len(re.findall(r"\w+", text))
    if wc < 400 or wc > 1500:
        errs.append(f"word count {wc} outside required range [400, 1500]")

    return errs


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_output_format.py <final_review.md>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        return 1
    errs = validate(path)
    if errs:
        print(f"FAIL: {path}", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
