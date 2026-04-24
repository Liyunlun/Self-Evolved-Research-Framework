#!/usr/bin/env bash
# Run the full test suite for the peer-review skill family.
#
# Layers:
#   1. Static lint         — SKILL.md files, shared assets, cross-refs.
#   2. Schema validators   — contracts reject malformed inputs (negative tests).
#   3. Stage findings      — golden fixtures contain expected [severity] flags.
#   4. E2E pipeline        — full pipeline on fixture paper passes all contracts.
#
# Exit 0 = all green; non-zero = first failing layer.

set -uo pipefail
cd "$(dirname "$0")"

# Use the user's local python so PyYAML is available.
PY="${PY:-/home/shs/anaconda3/bin/python3}"
if ! command -v "$PY" >/dev/null; then
    PY="python3"
fi

run() {
    local label="$1"; shift
    printf '== %-28s == ' "$label"
    if "$@"; then
        :
    else
        echo "FAILED"
        exit 1
    fi
}

echo "---- peer-review test suite ----"

run "Layer 1: static lint"        "$PY" test_skills_static.py
run "Layer 2: negative cases"     "$PY" test_negative_cases.py
run "Layer 3: stage findings"     "$PY" test_stage_findings.py
run "Layer 4: E2E pipeline"       "$PY" test_pipeline_e2e.py
run "Layer 5: SAC golden"         bash "../../peer-review-sac/tests/test_sac.sh"
run "Layer 6: taste probes"       "$PY" test_taste_probes.py

echo "---- all tests passed ----"
