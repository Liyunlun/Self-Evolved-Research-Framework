#!/usr/bin/env bash
# Static test for peer-review-sac: validates the golden sac_summary.md matches
# the structural contract documented in SKILL.md.
#
# Checks:
#   1. Exactly one H1 title at the top.
#   2. The four required section headings appear in order.
#   3. AAAI-format headers (Synopsis / Summary / Strengths / Weaknesses / References)
#      do NOT appear — SAC is deliberately not an AAAI review.
#   4. Unified Recommendation first non-blank line is one of the four allowed tokens.
#   5. Vote line is present and mentions each reviewer id.
#   6. All severity tags match [critical] / [major] / [minor].
#   7. Decision correctness: median over (weak accept, weak reject, weak reject) at
#      oral level is weak reject.

set -uo pipefail
cd "$(dirname "$0")"

FIXTURE="fixtures/golden_sac_summary.md"
errors=0

log_fail() { echo "FAIL: $1" >&2; errors=$((errors+1)); }

[ -f "$FIXTURE" ] || { log_fail "fixture missing: $FIXTURE"; exit 1; }

# 1. Exactly one H1 near top
h1_count=$(grep -c '^# [^#]' "$FIXTURE")
if [ "$h1_count" -ne 1 ]; then
    log_fail "expected exactly 1 H1 title, found $h1_count"
fi
first_nonblank=$(grep -n '.' "$FIXTURE" | head -1 | cut -d: -f1)
if [ "$first_nonblank" -gt 2 ]; then
    log_fail "H1 title must be near the top (line <=2), actually line $first_nonblank"
fi

# 2. Required sections in order
required=("## Reviewers" "## Points of consensus" "## Points of disagreement" "## Unified Recommendation")
prev_line=0
for section in "${required[@]}"; do
    line=$(grep -n -F "$section" "$FIXTURE" | head -1 | cut -d: -f1)
    if [ -z "$line" ]; then
        log_fail "missing required section: $section"
    elif [ "$line" -le "$prev_line" ]; then
        log_fail "section '$section' out of order (line $line <= previous $prev_line)"
    else
        prev_line=$line
    fi
done

# 3. Forbidden AAAI headers
forbidden=("## Synopsis" "## Summary" "## Strengths" "## Weaknesses" "## References")
for section in "${forbidden[@]}"; do
    if grep -q -F "$section" "$FIXTURE"; then
        log_fail "forbidden AAAI header present: $section"
    fi
done

# 4. Unified Recommendation token validation
rec_line=$(awk '/^## Unified Recommendation/{flag=1; next} flag && NF{print; exit}' "$FIXTURE")
case "$rec_line" in
    "accept"|"weak accept"|"weak reject"|"reject") : ;;
    *) log_fail "Unified Recommendation first non-blank line must be one of {accept, weak accept, weak reject, reject}; got: '$rec_line'" ;;
esac

# 7. Decision correctness for this fixture: must be "weak reject"
if [ "$rec_line" != "weak reject" ]; then
    log_fail "expected 'weak reject' for fixture (median of weak accept / weak reject / weak reject at oral); got '$rec_line'"
fi

# 5. Vote line mentions each reviewer id
vote_line=$(grep -m1 '^Vote:' "$FIXTURE" || true)
if [ -z "$vote_line" ]; then
    log_fail "missing 'Vote:' line under Unified Recommendation"
else
    for rid in R1 R2 R3; do
        echo "$vote_line" | grep -q "$rid=" || log_fail "Vote line missing $rid= entry"
    done
fi

# 6. Severity tags only use allowed forms
bad_sev=$(grep -oE '\[[a-z]+\]' "$FIXTURE" | grep -vE '^\[(critical|major|minor)\]$' || true)
if [ -n "$bad_sev" ]; then
    log_fail "invalid severity tag(s): $bad_sev"
fi

if [ "$errors" -gt 0 ]; then
    echo "FAIL: peer-review-sac golden ($errors error(s))" >&2
    exit 1
fi

echo "OK: peer-review-sac golden sac_summary.md passes all 7 structural checks"
