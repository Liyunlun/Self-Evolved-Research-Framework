#!/usr/bin/env python3
"""
Validate a final review file against shared/output_format.md (AAAI format).

Required: exactly one '# <title>' (h1), and five '## <heading>' sections in order:
Synopsis, Summary, Strengths, Weaknesses, References.
Each Weakness bullet must carry [critical]/[major]/[minor] severity.

Optional: a `## Verdict` section (enabled by `--verdict` on the orchestrator).
When present, it must follow `## References` and contain:
  - Rate: <one of: strong accept | accept | weak accept | weak reject | reject | strong reject>
  - Confidence: <integer 1-5>
  - Rationale: <one or more sentences>

Usage:
    python test_output_format.py <final_review.md> [--verdict]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REQUIRED_ORDER = ["## Synopsis", "## Summary", "## Strengths", "## Weaknesses", "## References"]
WEAK_BULLET = re.compile(r"^-\s*\[(critical|major|minor)\]")
VALID_RATES = {"strong accept", "accept", "weak accept",
               "weak reject", "reject", "strong reject"}
RATE_RE = re.compile(r"^-\s*Rate:\s*(.+?)\s*$")
CONF_RE = re.compile(r"^-\s*Confidence:\s*([0-9]+)\s*$")
RATIONALE_RE = re.compile(r"^-\s*Rationale:\s*(.+)$")


def validate(path: pathlib.Path, require_verdict: bool = False) -> list[str]:
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

    # Optional Verdict section
    has_verdict = "## Verdict" in text
    if require_verdict and not has_verdict:
        errs.append("missing required section: ## Verdict (required when --verdict is set)")
    if not require_verdict and has_verdict:
        errs.append("## Verdict present but --verdict was not requested")
    if has_verdict:
        # Must come after ## References
        refs_idx = text.find("## References")
        verdict_idx = text.find("## Verdict")
        if refs_idx != -1 and verdict_idx < refs_idx:
            errs.append("## Verdict must come AFTER ## References")
        verdict_tail = text.split("## Verdict", 1)[1]
        next_idx = verdict_tail.find("\n## ")
        verdict_block = verdict_tail if next_idx == -1 else verdict_tail[:next_idx]
        v_lines = [l.strip() for l in verdict_block.splitlines() if l.strip()]
        rate_match = next((RATE_RE.match(l) for l in v_lines if RATE_RE.match(l)), None)
        conf_match = next((CONF_RE.match(l) for l in v_lines if CONF_RE.match(l)), None)
        rationale_match = next((RATIONALE_RE.match(l) for l in v_lines if RATIONALE_RE.match(l)), None)
        if not rate_match:
            errs.append("Verdict section missing '- Rate: ...' line")
        else:
            rate_val = rate_match.group(1).strip().lower()
            if rate_val not in VALID_RATES:
                errs.append(f"invalid Rate {rate_val!r} (must be one of {sorted(VALID_RATES)})")
        if not conf_match:
            errs.append("Verdict section missing '- Confidence: <int>' line")
        else:
            conf_val = int(conf_match.group(1))
            if conf_val < 1 or conf_val > 5:
                errs.append(f"Confidence {conf_val} out of range [1, 5]")
        if not rationale_match:
            errs.append("Verdict section missing '- Rationale: ...' line")

    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--verdict", action="store_true",
                    help="require a ## Verdict section (Rate + Confidence + Rationale)")
    args = ap.parse_args()
    path = pathlib.Path(args.path)
    if not path.exists():
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        return 1
    errs = validate(path, require_verdict=args.verdict)
    if errs:
        print(f"FAIL: {path}", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
