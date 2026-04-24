#!/usr/bin/env python3
r"""Static cross-reference test for the taste-priors probe system.

Validates:
  1. `shared/taste-priors.md` exists and defines at least 6 probes using stable
     `Probe N — \`<name>\`` headings.
  2. `base_instruction.md` references `taste-priors.md` so stages inherit the probes.
  3. Each stage that claims a primary probe in `taste-priors.md`'s probe-to-stage map
     actually mentions that probe name in its SKILL.md body.
  4. Every fixture under `tests/fixtures/taste/` names an existing probe in a
     `Probe: <name>.` line.
  5. Every non-audit-only probe has at least one fixture that exercises it.

Exits 0 on success, non-zero with a diagnostic on failure.
"""

from __future__ import annotations

import pathlib
import re
import sys

TESTS_DIR = pathlib.Path(__file__).parent
PEER_REVIEW_DIR = TESTS_DIR.parent
SKILLS_DIR = PEER_REVIEW_DIR.parent

TASTE_PRIORS = PEER_REVIEW_DIR / "shared" / "taste-priors.md"
BASE_INSTR = PEER_REVIEW_DIR / "shared" / "base_instruction.md"
FIXTURES = TESTS_DIR / "fixtures" / "taste"

PROBE_HEADING_RE = re.compile(r"^##\s+Probe\s+\d+\s+—\s+`([a-z_]+)`\s*$", re.MULTILINE)
STAGE_MAP_ROW_RE = re.compile(
    r"^\|\s*`([a-z_]+)`\s*\|\s*`(peer-review[a-z-]*)`"
)
FIXTURE_PROBE_RE = re.compile(r"^Probe:\s*`([a-z_]+)`\.?\s*$", re.MULTILINE)

# Probes that only audit other findings; they need no input-fixture exercise.
AUDIT_ONLY = {"vote_moving_weakness"}


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def main() -> int:
    errors: list[str] = []

    if not TASTE_PRIORS.is_file():
        print(f"FAIL: missing {TASTE_PRIORS}", file=sys.stderr)
        return 1

    taste_text = TASTE_PRIORS.read_text()
    probes = PROBE_HEADING_RE.findall(taste_text)
    if len(probes) < 6:
        fail(
            f"taste-priors.md defines {len(probes)} probes; expected at least 6. Found: {probes}",
            errors,
        )

    # base_instruction must reference taste-priors.md
    base_text = BASE_INSTR.read_text()
    if "taste-priors.md" not in base_text:
        fail("base_instruction.md does not reference taste-priors.md", errors)

    # Parse probe-to-stage map (only the PRIMARY column — the second `-delimited cell).
    primary_map: dict[str, str] = {}
    for line in taste_text.splitlines():
        match = STAGE_MAP_ROW_RE.match(line)
        if match:
            probe, stage = match.group(1), match.group(2)
            # Only capture the first occurrence per probe (primary column).
            primary_map.setdefault(probe, stage)

    # Every probe listed in the heading must also appear in the map (except possibly audit-only).
    for probe in probes:
        if probe not in primary_map:
            fail(
                f"probe '{probe}' is defined but missing from the probe-to-stage map table",
                errors,
            )

    # Each primary stage's SKILL.md body must mention the probe name.
    for probe, stage in primary_map.items():
        skill_md = SKILLS_DIR / stage / "SKILL.md"
        if not skill_md.is_file():
            fail(f"taste-priors names stage '{stage}' but {skill_md} does not exist", errors)
            continue
        skill_text = skill_md.read_text()
        if probe not in skill_text:
            fail(
                f"stage '{stage}' is the primary stage for probe '{probe}' per taste-priors.md, "
                f"but {skill_md} does not mention the probe name",
                errors,
            )

    # Fixture cross-check.
    if not FIXTURES.is_dir():
        fail(f"taste fixtures directory missing: {FIXTURES}", errors)
    else:
        fixture_probes: set[str] = set()
        for fx in sorted(FIXTURES.glob("*.md")):
            text = fx.read_text()
            hits = FIXTURE_PROBE_RE.findall(text)
            if not hits:
                fail(
                    f"fixture {fx.name} has no 'Probe: `<name>`.' line",
                    errors,
                )
                continue
            for probe in hits:
                if probe not in probes:
                    fail(
                        f"fixture {fx.name} references unknown probe '{probe}'",
                        errors,
                    )
                fixture_probes.add(probe)

        # Every non-audit-only probe must have at least one fixture.
        for probe in probes:
            if probe in AUDIT_ONLY:
                continue
            if probe not in fixture_probes:
                fail(
                    f"probe '{probe}' is not audit-only but has no fixture under {FIXTURES}",
                    errors,
                )

    if errors:
        print("FAIL: taste-probe cross-reference issues:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    n_fx = len(list(FIXTURES.glob("*.md")))
    n_probes = len(probes)
    n_audit = sum(1 for p in probes if p in AUDIT_ONLY)
    print(
        f"OK: {n_probes} probes defined ({n_audit} audit-only), "
        f"{n_fx} fixtures, base_instruction wired"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
