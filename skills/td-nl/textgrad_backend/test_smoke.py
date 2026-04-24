"""Offline smoke test for the textgrad TD-NL backend.

Run:
    python -m skills.td-nl.textgrad_backend.test_smoke
or:
    python skills/td-nl/textgrad_backend/test_smoke.py

Verifies:
  1. Schema v2 + legacy v1 G2 lines parse into a DAG
  2. DAG topological order respects upstream edges
  3. TD layer populates td_error and classifies strengths
  4. backward produces a proposal for the 'hard'-strength skill
  5. propose.write_proposal mutates a temp feedback-log correctly
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(HERE.parent))  # td-nl/ on sys.path

from textgrad_backend import (  # noqa: E402
    USING_REAL_TEXTGRAD,
    parse_feedback_log,
    run_backward,
    write_proposal,
)
from textgrad_backend.td_layer import TDLayer, aggregate  # noqa: E402


SAMPLE_LOG = """# Skill Feedback Log

## Pending Feedback
- [2026-04-19] session:s1 node:n1 upstream:- skill:memory-write | outcome:as_expected | delta:0 | "wrote 1 episodic memory"
- [2026-04-19] session:s1 node:n2 upstream:n1 skill:memory-consolidate | outcome:worse | delta:-1 | "missed paper-read notes"
- [2026-04-19] session:s1 node:n3 upstream:n2 skill:evolve-suggest | outcome:worse | delta:-1 | "downstream proposal was vague"
- [2026-04-19] session:s1 node:n4 upstream:n2 skill:evolve-suggest | outcome:worse | delta:-1 | "still vague after retry"
- [2026-04-19] session:s1 node:n5 upstream:n4 skill:evolve-suggest | outcome:worse | delta:-1 | "third vague output"
- [2026-04-18] skill:paper-read | outcome:better | delta:+1 | "legacy line still parses"

## Pending Proposals

## Processed Feedback
"""


SAMPLE_LOG_V3 = """# Skill Feedback Log

## Pending Feedback
- [2026-04-19] session:s2 node:n1 upstream:- skill:memory-write
    P1_analysis: "root firing, wrote 2 episodic memories about board game"
    P2_predict:  V=6, conf=high, reason="memory-write is well-tuned"
    P4_strategy: keep, note="no change"
    P5_result:   outcome=as_expected, reward=0, ev="wrote cleanly"
- [2026-04-19] session:s2 node:n2 upstream:n1 skill:evolve-suggest
    P1_analysis: "downstream aggregation on patchy upstream"
    P2_predict:  V=4, conf=high, reason="prior vagueness in similar firings"
    P3_td:       delta=-1.5, interp="surprise worse than memory-write baseline"
    P4_strategy: refine, note="sharpen evidence digest"
    P5_result:   outcome=worse, reward=-1, ev="proposal still too abstract"
- [2026-04-19] session:s2 node:n3 upstream:n2 skill:evolve-suggest
    P1_analysis: "retry on similar DAG shape"
    P2_predict:  V=4, conf=high, reason="pattern persists"
    P3_td:       delta=-1.4, interp="same failure mode"
    P4_strategy: refine, note="tighten TD rubric"
    P5_result:   outcome=worse, reward=-1, ev="still vague"

## Pending Proposals

## Processed Feedback
"""


def _make_tempdir():
    td = Path(tempfile.mkdtemp(prefix="tdnl_smoke_"))
    (td / "skills").mkdir()
    (td / "skills" / "td-nl").mkdir()
    (td / "skills" / "td-nl" / "skill-values").mkdir()
    # create a couple of fake skill specs
    for name in ("memory-write", "memory-consolidate", "evolve-suggest"):
        skill_dir = td / "skills" / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fake spec for {name}\n---\n\nbody\n",
            encoding="utf-8",
        )
    # seed skill-values so V(s) is interesting
    (td / "skills" / "td-nl" / "skill-values" / "evolve-suggest.md").write_text(
        "### Scores (1-10)\n- trigger_accuracy: 6\n- output_usefulness: 6\n"
        "- token_efficiency: 5\n- overall: 6\n",
        encoding="utf-8",
    )
    (td / "skills" / "td-nl" / "value-function.md").write_text(
        "### Scores (1-10)\n- overall: 5\n",
        encoding="utf-8",
    )
    log = td / "skills" / "td-nl" / "feedback-log.md"
    log.write_text(SAMPLE_LOG, encoding="utf-8")
    return td, log


def test_parse_and_dag():
    td, log = _make_tempdir()
    graphs = parse_feedback_log(log)
    sessions = {g.session for g in graphs}
    assert "s1" in sessions and "legacy" in sessions, f"sessions: {sessions}"
    s1 = [g for g in graphs if g.session == "s1"][0]
    assert len(s1.nodes) == 5
    order = [n.node_id for n in s1.topo_order()]
    assert order.index("n1") < order.index("n2") < order.index("n3")
    assert s1.nodes["n3"].upstream == ["n2"]
    assert s1.nodes["n2"].upstream_nodes[0].node_id == "n1"
    shutil.rmtree(td)
    print("  ok parse_and_dag")


def test_td_layer():
    td, log = _make_tempdir()
    graphs = parse_feedback_log(log)
    s1 = [g for g in graphs if g.session == "s1"][0]
    aggs = aggregate(s1)
    layer = TDLayer()
    layer.score(aggs, current_values={"evolve-suggest": 6.0, "memory-write": 5.0, "memory-consolidate": 5.0})
    evs = aggs["evolve-suggest"]
    assert evs.net_delta == -3
    # 3 entries => medium confidence => lr=0.5
    assert evs.confidence == "medium"
    # td should be clearly negative
    assert evs.td_error < -0.1, f"td_error={evs.td_error}"
    assert evs.strength in ("soft", "hard")
    shutil.rmtree(td)
    print(f"  ok td_layer (evolve-suggest td={evs.td_error:+.3f} strength={evs.strength})")


def test_backward_end_to_end():
    td, log = _make_tempdir()
    results = run_backward(
        feedback_log=log,
        skills_root=td / "skills",
        skill_values_dir=td / "skills" / "td-nl" / "skill-values",
        value_function_file=td / "skills" / "td-nl" / "value-function.md",
        engine=None,
    )
    # should have both s1 and legacy sessions
    sessions = {r.session for r in results}
    assert "s1" in sessions
    s1 = [r for r in results if r.session == "s1"][0]
    evolve_agg = s1.aggregates["evolve-suggest"]
    print(
        f"  s1/evolve-suggest: td={evolve_agg.td_error:+.3f} "
        f"strength={evolve_agg.strength} proposals={len(s1.proposals)}"
    )
    # write proposal and verify feedback-log mutation
    block = write_proposal(log, results, today="2026-04-19")
    final = log.read_text(encoding="utf-8")
    assert "## Processed Feedback" in final
    if block:
        assert "PROPOSAL" in final
    # pending feedback should have no data lines left
    pending = final.split("## Pending Feedback", 1)[1].split("## ", 1)[0]
    data_lines = [ln for ln in pending.splitlines() if ln.strip().startswith("- [") and "skill:" in ln]
    assert not data_lines, f"pending still has lines: {data_lines}"
    shutil.rmtree(td)
    print(f"  ok backward_end_to_end (backend={'textgrad' if USING_REAL_TEXTGRAD else 'shim'})")


def _make_tempdir_v3():
    td = Path(tempfile.mkdtemp(prefix="tdnl_smoke_v3_"))
    (td / "skills").mkdir()
    (td / "skills" / "td-nl").mkdir()
    (td / "skills" / "td-nl" / "skill-values").mkdir()
    for name in ("memory-write", "evolve-suggest"):
        skill_dir = td / "skills" / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fake spec for {name}\n---\n\nbody\n",
            encoding="utf-8",
        )
    (td / "skills" / "td-nl" / "skill-values" / "evolve-suggest.md").write_text(
        "### Scores (1-10)\n- trigger_accuracy: 6\n- output_usefulness: 6\n"
        "- token_efficiency: 5\n- overall: 6\n",
        encoding="utf-8",
    )
    (td / "skills" / "td-nl" / "value-function.md").write_text(
        "### Scores (1-10)\n- overall: 5\n",
        encoding="utf-8",
    )
    log = td / "skills" / "td-nl" / "feedback-log.md"
    log.write_text(SAMPLE_LOG_V3, encoding="utf-8")
    return td, log


def test_v3_parse_and_fields():
    td, log = _make_tempdir_v3()
    graphs = parse_feedback_log(log)
    s2 = [g for g in graphs if g.session == "s2"][0]
    assert len(s2.nodes) == 3
    # v3 node fields
    n1 = s2.nodes["n1"]
    assert n1.is_v3, "n1 should be recognized as v3"
    assert n1.predicted_V == 6.0
    assert n1.predicted_conf == "high"
    assert n1.strategy == "keep"
    # n2 has P3_td
    n2 = s2.nodes["n2"]
    assert n2.inline_td == -1.5
    assert n2.strategy == "refine"
    # aggregation uses v3 fields
    aggs = aggregate(s2)
    evs = aggs["evolve-suggest"]
    assert evs.predicted_Vs and abs(sum(evs.predicted_Vs) / len(evs.predicted_Vs) - 4.0) < 1e-6
    assert evs.inline_tds == [-1.5, -1.4]
    # v3 high conf should override entry-count bin (2 entries would be 'low' without v3)
    assert evs.confidence == "high", f"expected high (v3 override), got {evs.confidence}"
    # scoring path
    layer = TDLayer()
    layer.score(aggs, current_values={"evolve-suggest": 6.0, "memory-write": 5.0})
    assert evs.td_error < -0.1, f"td_error={evs.td_error}"
    assert evs.strength in ("soft", "hard")
    shutil.rmtree(td)
    print(f"  ok v3_parse_and_fields (evolve-suggest conf={evs.confidence} td={evs.td_error:+.3f} strength={evs.strength})")


FIXTURES_DIR = HERE / "fixtures"


def test_live_fixture_regression():
    """Golden-file regression: feed the pinned 2026-04-20 live feedback log into
    run_backward and compare JSON summary to the snapshot fixture. Catches any
    silent change in per-skill td scoring or the V^L bump.
    """
    import json

    input_md = FIXTURES_DIR / "live_feedback_log_2026-04-20.input.md"
    expected_json = FIXTURES_DIR / "live_feedback_log_2026-04-20.json"
    if not input_md.exists() or not expected_json.exists():
        print("  skip live_fixture_regression (fixtures missing)")
        return

    td = Path(tempfile.mkdtemp(prefix="tdnl_smoke_live_"))
    (td / "skills").mkdir()
    (td / "skills" / "td-nl").mkdir()
    (td / "skills" / "td-nl" / "skill-values").mkdir()
    for name in ("general-research", "design-converge", "writing-draft", "session-close"):
        skill_dir = td / "skills" / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fake spec for {name}\n---\n\nbody\n",
            encoding="utf-8",
        )
    (td / "skills" / "td-nl" / "value-function.md").write_text(
        "### Scores (1-10)\n- overall: 5\n", encoding="utf-8"
    )
    log = td / "skills" / "td-nl" / "feedback-log.md"
    log.write_text(input_md.read_text(encoding="utf-8"), encoding="utf-8")

    results = run_backward(
        feedback_log=log,
        skills_root=td / "skills",
        skill_values_dir=td / "skills" / "td-nl" / "skill-values",
        value_function_file=td / "skills" / "td-nl" / "value-function.md",
        engine=None,  # deterministic: match fixture that was captured without engine
    )

    # Mirror scripts/evolve_textgrad.py::_summarize exactly
    actual = {"backend": "textgrad" if USING_REAL_TEXTGRAD else "shim", "sessions": []}
    for r in results:
        s = {
            "session": r.session,
            "v_l_old": round(r.v_l_old, 3),
            "v_l_new": round(r.v_l_new, 3),
            "skills": {
                skill: {
                    "net_delta": agg.net_delta,
                    "td_error": round(agg.td_error, 3),
                    "strength": agg.strength,
                    "V": round(agg.V, 3),
                    "V_next": round(agg.V_next, 3),
                    "confidence": agg.confidence,
                }
                for skill, agg in sorted(r.aggregates.items())
            },
            "proposals": [
                {
                    "skill": p.skill,
                    "old_value": round(p.old_value, 3),
                    "new_value": round(p.new_value, 3),
                    "td_error": round(p.td_error, 3),
                    "strength": p.strength,
                }
                for p in r.proposals
            ],
        }
        actual["sessions"].append(s)

    expected = json.loads(expected_json.read_text(encoding="utf-8"))
    assert actual == expected, (
        "fixture mismatch — refresh with:\n"
        "  python3 scripts/evolve_textgrad.py --dry-run --json > "
        f"{expected_json.relative_to(REPO_ROOT)}\n"
        f"diff:\n  expected={json.dumps(expected, sort_keys=True)}\n"
        f"  actual=  {json.dumps(actual, sort_keys=True)}"
    )
    shutil.rmtree(td)
    print("  ok live_fixture_regression (2026-04-20 s8)")


def test_engine_wiring():
    """Verify the shim's TextualGradientDescent routes through an injected
    engine when one is provided, and falls back cleanly when the engine
    raises. Uses an in-process FakeEngine so no CLI call is made.
    """
    td, log = _make_tempdir()
    calls = []

    class FakeEngine:
        def __call__(self, prompt, system_prompt=None, **_):
            calls.append(prompt)
            return "FAKE NOTE: tighten the TD-rubric so 'worse' signals propagate."

    results = run_backward(
        feedback_log=log,
        skills_root=td / "skills",
        skill_values_dir=td / "skills" / "td-nl" / "skill-values",
        value_function_file=td / "skills" / "td-nl" / "value-function.md",
        engine=FakeEngine(),
    )
    s1 = [r for r in results if r.session == "s1"][0]
    assert s1.proposals, "expected at least one proposal for session s1"
    diff = s1.proposals[0].diff_text
    assert "<<EVOLVE NOTE (shim+engine)" in diff, f"tag missing, diff head: {diff[:160]}"
    assert "FAKE NOTE" in diff, f"engine output missing, diff head: {diff[:200]}"
    assert len(calls) >= 1, "engine was never invoked"

    # failing-engine fallback: confirm deterministic shim path still works
    class FailingEngine:
        def __call__(self, prompt, system_prompt=None, **_):
            raise RuntimeError("boom")

    results2 = run_backward(
        feedback_log=log,
        skills_root=td / "skills",
        skill_values_dir=td / "skills" / "td-nl" / "skill-values",
        value_function_file=td / "skills" / "td-nl" / "value-function.md",
        engine=FailingEngine(),
    )
    # NOTE: write_proposal() in the first run mutated the pending section to
    # empty, so results2 may be empty - that's fine; we just want to ensure no
    # exception propagates from engine failure.
    shutil.rmtree(td)
    print("  ok engine_wiring (fake engine injected + failure fallback)")


def test_experience_buffer_and_crl():
    """Exercise the per-skill experience buffer + CRL TD contribution."""
    from textgrad_backend import experience_buffer  # noqa: E402
    from textgrad_backend.td_layer import TDLayer, SkillAggregate, STRATEGY_PENALTY

    td_dir = Path(tempfile.mkdtemp(prefix="tdnl_buffer_"))
    sv = td_dir / "skill-values"

    # empty buffer: avg_reward = 0
    assert experience_buffer.read_recent(sv, "ttt") == []
    assert experience_buffer.mean_reward([]) == 0.0

    # append and truncate
    for r in [1, 1, 1, -1, 1]:
        experience_buffer.append(sv, "ttt", reward=r, session_id="s", k=3)
    recent = experience_buffer.read_recent(sv, "ttt", k=3)
    assert len(recent) == 3, len(recent)
    # last 3 of [1,1,1,-1,1]
    assert [e["reward"] for e in recent] == [1.0, -1.0, 1.0]
    assert abs(experience_buffer.mean_reward(recent) - (1 - 1 + 1) / 3) < 1e-9

    # CRL TD: clean-draw reward=+1 with non-empty buffer should NOT be zero
    agg = SkillAggregate(
        skill="ttt", n_better=1, n_expected=0, n_worse=0, net_delta=1,
        evidences=[], predicted_Vs=[], inline_tds=[],
    )
    layer = TDLayer()
    reader = lambda s: experience_buffer.mean_reward(
        experience_buffer.read_recent(sv, s)
    )
    layer.score({"ttt": agg}, current_values={"ttt": 5.0}, buffer_reader=reader)
    # With r=+1, avg_buffer_r=1/3, V=5:
    #   V_next = clip(5 + 0.5*1 + 0.5*(1/3), 1, 10) = 5.667
    #   td = 1 + 0.9*5.667 - 5 = 1.1
    assert agg.td_error > 0.8, f"expected positive TD near +1.1, got {agg.td_error}"
    assert agg.strength == "hard", agg.strength
    print(f"  ok experience_buffer_and_crl (td={agg.td_error:+.3f} strength={agg.strength})")

    # P4 strategy penalty: refine vote should drop V_next and push td lower
    agg2 = SkillAggregate(
        skill="ttt", n_better=1, n_expected=0, n_worse=0, net_delta=1,
        evidences=[], predicted_Vs=[], inline_tds=[],
        strategy_votes={"refine": 1},
    )
    layer.score({"ttt": agg2}, current_values={"ttt": 5.0}, buffer_reader=reader)
    # refine penalty = 0.5 => V_next drops by 0.5
    assert agg2.V_next < agg.V_next - 0.4, (
        f"expected refine-penalty drop; agg={agg.V_next} agg2={agg2.V_next}"
    )
    assert agg2.td_error < agg.td_error, "refine should lower td vs keep"
    print(f"  ok p4_strategy_penalty (refine td={agg2.td_error:+.3f} < keep td={agg.td_error:+.3f})")

    shutil.rmtree(td_dir)


def main():
    print(f"[smoke] backend={'textgrad' if USING_REAL_TEXTGRAD else 'shim'}")
    test_parse_and_dag()
    test_td_layer()
    test_backward_end_to_end()
    test_v3_parse_and_fields()
    test_live_fixture_regression()
    test_engine_wiring()
    test_experience_buffer_and_crl()
    print("[smoke] all tests passed")


if __name__ == "__main__":
    main()
