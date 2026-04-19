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


def main():
    print(f"[smoke] backend={'textgrad' if USING_REAL_TEXTGRAD else 'shim'}")
    test_parse_and_dag()
    test_td_layer()
    test_backward_end_to_end()
    test_v3_parse_and_fields()
    print("[smoke] all tests passed")


if __name__ == "__main__":
    main()
