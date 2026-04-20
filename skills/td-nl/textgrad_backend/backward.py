"""Orchestrate the full backward pass:

  1. Parse feedback-log -> per-session DAGs
  2. For each session:
       a. Aggregate per skill (G1)
       b. Run TD layer -> td_errors + strengths
       c. Build a textgrad computation graph mirroring the DAG:
            - Each skill spec is a requires_grad Variable (shared across nodes)
            - Each firing node becomes an output Variable whose predecessors
              include its skill-spec Variable + its upstream firing-nodes
            - A TextLoss is attached at the leaf with the aggregated critique
       d. Call loss.backward(<aggregated critique>) to push textual gradients
          into every requires_grad skill-spec Variable
       e. Optimizer.step() only over skills with strength == 'hard'
  3. Return the resulting proposals (pure data; writing happens in propose.py)

Design note: we do NOT actually mutate SKILL.md files here. The optimizer
step produces new candidate spec text on the Variable objects; propose.py
writes that as a PROPOSAL entry in feedback-log.md, which evolve-apply
then approves into SKILL.md. This preserves the one-edit-per-session cap
and the history/rollback invariant.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .variables import (
    Variable,
    TextLoss,
    TextualGradientDescent,
    USING_REAL_TEXTGRAD,
    load_skill_variable,
)
from .trace import SessionGraph, TraceNode, parse_feedback_log
from .td_layer import SkillAggregate, TDLayer, aggregate
from .engines import make_default_engine
from . import experience_buffer


OVERALL_RE = re.compile(r"-\s*overall:\s*([\d.]+)")


def read_skill_value(skill_values_dir: Path, skill: str) -> float:
    """Read the current 'overall' score from skill-values/{skill}.md.
    Missing files default to 5.0 (mid-scale bootstrap)."""
    path = skill_values_dir / f"{skill}.md"
    if not path.exists():
        return 5.0
    text = path.read_text(encoding="utf-8")
    m = OVERALL_RE.search(text)
    if not m:
        return 5.0
    try:
        return float(m.group(1))
    except ValueError:
        return 5.0


def write_skill_value(skill_values_dir: Path, skill: str, value: float) -> None:
    """Persist the updated Q^L to skill-values/{skill}.md. Creates the file
    on first write; on update, rewrites only the 'overall' line in-place."""
    import datetime as _dt

    skill_values_dir.mkdir(parents=True, exist_ok=True)
    path = skill_values_dir / f"{skill}.md"
    new_line = f"- overall: {value:.3f}"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        new_text, n = OVERALL_RE.subn(new_line, text, count=1)
        if n == 0:
            new_text = text.rstrip() + f"\n{new_line}\n"
    else:
        new_text = (
            f"# Skill Value Q^L({skill})\n"
            f"<!-- Created/updated by td-nl backward on {_dt.date.today()} -->\n\n"
            f"### Scores (1-10)\n"
            f"{new_line}\n"
        )
    path.write_text(new_text, encoding="utf-8")


@dataclass
class Proposal:
    skill: str
    old_value: float
    new_value: float
    td_error: float
    strength: str
    gradient_text: str
    diff_text: str
    evidence_summary: str
    risk_note: str


@dataclass
class BackwardResult:
    session: str
    aggregates: Dict[str, SkillAggregate]
    proposals: List[Proposal]
    v_l_old: float
    v_l_new: float


def _summarize_evidence(evs: List[str], limit: int = 3) -> str:
    if not evs:
        return "no evidence"
    head = "; ".join(f'"{e}"' for e in evs[:limit])
    tail = "" if len(evs) <= limit else f" (+{len(evs)-limit} more)"
    return head + tail


def _build_graph_for_session(
    graph: SessionGraph, skills_root: Path
) -> Tuple[Dict[str, Variable], Dict[str, Variable]]:
    """Returns (spec_vars, firing_vars).
      spec_vars[skill]      -> Variable(requires_grad=True) for SKILL.md
      firing_vars[node_id]  -> Variable representing that firing's output
    """
    spec_vars: Dict[str, Variable] = {}
    for skill in graph.skills():
        path = skills_root / skill / "SKILL.md"
        if path.exists():
            spec_vars[skill] = load_skill_variable(str(path), skill)
        else:
            # still give it a Variable so the graph is complete
            spec_vars[skill] = Variable(
                value=f"(missing spec for {skill})",
                role_description=f"placeholder spec for missing skill '{skill}'",
                requires_grad=True,
            )

    firing_vars: Dict[str, Variable] = {}
    for node in graph.topo_order():
        preds: List[Variable] = [spec_vars[node.skill]]
        for u in node.upstream_nodes:
            if u.node_id in firing_vars:
                preds.append(firing_vars[u.node_id])
        firing_vars[node.node_id] = Variable(
            value=f"[firing of {node.skill} at {node.date}] outcome={node.outcome} ev={node.evidence!r}",
            role_description=f"output of skill '{node.skill}' firing (node {node.node_id})",
            requires_grad=False,
            predecessors=preds,
        )
    return spec_vars, firing_vars


def _aggregated_critique(aggregates: Dict[str, SkillAggregate]) -> str:
    parts = []
    for skill, agg in sorted(aggregates.items()):
        parts.append(
            f"[{skill}] net_delta={agg.net_delta} td={agg.td_error:+.2f} "
            f"strength={agg.strength} evidence={_summarize_evidence(agg.evidences)}"
        )
    return " || ".join(parts)


_UNSET = object()


def run_backward(
    feedback_log: Path,
    skills_root: Path,
    skill_values_dir: Path,
    value_function_file: Path,
    gamma: float = 0.9,
    engine=_UNSET,
) -> List[BackwardResult]:
    """Run the full session-close backward pass. Returns per-session results.

    engine: LLM engine used by the (shim or real) TextualGradientDescent.
            Default auto-selects via engines.make_default_engine() - currently
            ClaudeCodeCLIEngine when `claude` is on PATH, else None (pure
            deterministic shim). Pass None explicitly to force deterministic.
    """
    if engine is _UNSET:
        engine = make_default_engine()
    graphs = parse_feedback_log(feedback_log)
    td = TDLayer(gamma=gamma)
    results: List[BackwardResult] = []

    # read current V^L overall (used only for reporting)
    vl_old = 5.0
    if value_function_file.exists():
        m = OVERALL_RE.search(value_function_file.read_text(encoding="utf-8"))
        if m:
            try:
                vl_old = float(m.group(1))
            except ValueError:
                pass

    def _buffer_reader(skill: str) -> float:
        entries = experience_buffer.read_recent(skill_values_dir, skill)
        return experience_buffer.mean_reward(entries)

    for g in graphs:
        aggs = aggregate(g)
        if not aggs:
            continue
        current_vals = {s: read_skill_value(skill_values_dir, s) for s in aggs}
        td.score(aggs, current_vals, buffer_reader=_buffer_reader)

        spec_vars, firing_vars = _build_graph_for_session(g, skills_root)

        # attach a TextLoss at each leaf firing-node carrying an evaluation
        # instruction derived from that firing's evidence + td_error
        critique = _aggregated_critique(aggs)
        # we fold all leaves into a synthetic loss head to share one backward call
        leaves = g.leaves()
        synthetic_head = Variable(
            value="<session-close head>",
            role_description="virtual node aggregating all leaves for one backward",
            requires_grad=False,
            predecessors=[firing_vars[n.node_id] for n in leaves],
        )
        loss_fn = TextLoss(
            evaluation_instruction=(
                "Identify concrete edits to the parent skill specs that would "
                "have prevented the observed failures and amplified the observed "
                "successes. Keep YAML frontmatter intact. Preserve public trigger "
                "semantics. Be specific - cite section names when possible. "
                f"Session critique: {critique}"
            )
        )
        loss = loss_fn(synthetic_head)
        loss.backward(loss_fn.evaluation_instruction if not USING_REAL_TEXTGRAD else "")

        # optimizer.step() only over 'hard' skills (enforces 1-edit-per-session
        # by downstream proposal writer, not here)
        hard_specs = [
            spec_vars[s]
            for s, a in aggs.items()
            if a.strength == "hard" and s in spec_vars
        ]
        proposals: List[Proposal] = []
        if hard_specs:
            optim = TextualGradientDescent(parameters=hard_specs, engine=engine)
            optim.step()
            for skill, agg in aggs.items():
                if agg.strength != "hard" or skill not in spec_vars:
                    continue
                new_spec_text = spec_vars[skill].value  # after .step()
                old_val = current_vals[skill]
                new_val = TDLayer.apply_value_update(old_val, agg)
                proposals.append(
                    Proposal(
                        skill=skill,
                        old_value=old_val,
                        new_value=new_val,
                        td_error=agg.td_error,
                        strength=agg.strength,
                        gradient_text="\n".join(
                            spec_vars[skill].gradients if hasattr(spec_vars[skill], "gradients") else []
                        )
                        or "(see updated spec text)",
                        diff_text=new_spec_text,
                        evidence_summary=_summarize_evidence(agg.evidences),
                        risk_note=(
                            "Edit affects trigger description or process steps; "
                            "rollback snapshot will be stored in td-nl/history/."
                        ),
                    )
                )

        # compute session V^L delta (simple mean over updated skill values)
        updated_vals = {
            s: TDLayer.apply_value_update(current_vals[s], aggs[s]) for s in aggs
        }
        vl_new = sum(updated_vals.values()) / max(1, len(updated_vals))
        # Persist per-skill Q^L and append this firing's transition to the
        # experience buffer so continual learning has the rolling history on
        # the next firing.
        for skill, new_val in updated_vals.items():
            write_skill_value(skill_values_dir, skill, new_val)
            a = aggs[skill]
            pV = (sum(a.predicted_Vs) / len(a.predicted_Vs)) if a.predicted_Vs else None
            experience_buffer.append(
                skill_values_dir,
                skill,
                reward=float(a.net_delta),
                session_id=g.session,
                predicted_V=pV,
                strategy=a.dominant_strategy,
            )
        results.append(
            BackwardResult(
                session=g.session,
                aggregates=aggs,
                proposals=proposals,
                v_l_old=vl_old,
                v_l_new=vl_new,
            )
        )
    return results
