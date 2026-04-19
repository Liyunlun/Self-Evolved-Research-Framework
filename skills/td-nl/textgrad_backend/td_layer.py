"""TD(0) layer sitting on top of TextGrad.

For each skill that fired in the session we compute a TD error:
    delta_TD = r + gamma * V(s') - V(s)
where:
    r      = sum of G2 per-firing deltas for this skill this session (clamped)
    V(s)   = current Q^L 'overall' score for this skill (from skill-values/)
    V(s')  = predicted next-state value. Bootstrap:
             we approximate V(s') by V(s) + clipped(r) - a one-step Bellman
             guess in the absence of an explicit world model. (This matches
             how TD(0) is used as a bootstrap over a single transition.)
    gamma  = 0.9 default (configurable).

The magnitude of delta_TD scales the textual gradient selection:
    - |delta_TD| >= 1.0  -> keep the full textual gradient, propose spec edit
    - 0.25 <= |delta_TD| < 1.0 -> keep but mark as 'soft' (no proposal unless
                                   direction was consistent across 3 sessions)
    - |delta_TD| < 0.25  -> drop (ignore gradient; just bump value slightly)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .trace import SessionGraph, TraceNode


@dataclass
class SkillAggregate:
    skill: str
    n_better: int
    n_expected: int
    n_worse: int
    net_delta: int
    evidences: List[str]
    # v3-aware fields (None when no v3 blocks contributed):
    predicted_Vs: List[float] = None  # type: ignore[assignment]
    inline_tds: List[float] = None  # type: ignore[assignment]
    conf_votes: Dict[str, int] = None  # type: ignore[assignment]
    strategy_votes: Dict[str, int] = None  # type: ignore[assignment]
    analyses: List[str] = None  # type: ignore[assignment]
    # filled by TDLayer.score():
    V: float = 0.0
    V_next: float = 0.0
    td_error: float = 0.0
    strength: str = "drop"  # drop | soft | hard

    def __post_init__(self):
        if self.predicted_Vs is None:
            self.predicted_Vs = []
        if self.inline_tds is None:
            self.inline_tds = []
        if self.conf_votes is None:
            self.conf_votes = {}
        if self.strategy_votes is None:
            self.strategy_votes = {}
        if self.analyses is None:
            self.analyses = []

    @property
    def confidence(self) -> str:
        # Prefer v3 self-reported confidence when available (majority vote).
        if self.conf_votes:
            return max(self.conf_votes.items(), key=lambda kv: kv[1])[0]
        n = self.n_better + self.n_expected + self.n_worse
        if n >= 6:
            return "high"
        if n >= 3:
            return "medium"
        return "low"

    @property
    def learning_rate(self) -> float:
        return {"high": 1.0, "medium": 0.5, "low": 0.25}[self.confidence]

    @property
    def dominant_strategy(self) -> Optional[str]:
        """Most common P4 strategy across v3 firings, or None if no v3."""
        if not self.strategy_votes:
            return None
        return max(self.strategy_votes.items(), key=lambda kv: kv[1])[0]


def aggregate(graph: SessionGraph) -> Dict[str, SkillAggregate]:
    """Collapse a session DAG into per-skill aggregates.
    Harvests v3 fields (predicted_V, inline_td, conf, strategy, analysis)
    when present so TDLayer.score can use self-reported signals."""
    buckets: Dict[str, SkillAggregate] = {}
    for node in graph.nodes.values():
        agg = buckets.get(node.skill)
        if agg is None:
            agg = SkillAggregate(
                skill=node.skill,
                n_better=0,
                n_expected=0,
                n_worse=0,
                net_delta=0,
                evidences=[],
            )
            buckets[node.skill] = agg
        if node.outcome == "better":
            agg.n_better += 1
        elif node.outcome == "worse":
            agg.n_worse += 1
        else:
            agg.n_expected += 1
        agg.net_delta += node.delta
        if node.evidence:
            agg.evidences.append(node.evidence)
        # v3-specific harvesting
        if node.predicted_V is not None:
            agg.predicted_Vs.append(node.predicted_V)
        if node.inline_td is not None:
            agg.inline_tds.append(node.inline_td)
        if node.predicted_conf:
            agg.conf_votes[node.predicted_conf] = agg.conf_votes.get(node.predicted_conf, 0) + 1
        if node.strategy:
            agg.strategy_votes[node.strategy] = agg.strategy_votes.get(node.strategy, 0) + 1
        if node.analysis:
            agg.analyses.append(node.analysis)
    return buckets


def td0_error(reward: float, V: float, V_next: float, gamma: float = 0.9) -> float:
    return reward + gamma * V_next - V


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class TDLayer:
    gamma: float = 0.9
    hard_threshold: float = 1.0
    soft_threshold: float = 0.25
    # scaling: reward bootstrap step for V_next estimate
    bootstrap_step: float = 0.5

    def score(
        self,
        aggregates: Dict[str, SkillAggregate],
        current_values: Dict[str, float],
    ) -> None:
        """Populate V, V_next, td_error, strength on every aggregate in-place.

        If v3 blocks supplied `predicted_V` we use the mean of those as V(s')
        (self-report), overriding the bootstrap estimate. If v3 blocks also
        supplied an `inline_td`, we blend it 50/50 with the batch TD error to
        reconcile per-firing and per-session views."""
        for skill, agg in aggregates.items():
            V = current_values.get(skill, 5.0)
            r_clipped = _clip(agg.net_delta * agg.learning_rate, -2.0, 2.0)

            # V(s'): prefer self-report, else bootstrap
            if agg.predicted_Vs:
                V_next_est = _clip(
                    sum(agg.predicted_Vs) / len(agg.predicted_Vs), 1.0, 10.0
                )
            else:
                V_next_est = _clip(V + self.bootstrap_step * r_clipped, 1.0, 10.0)

            td_batch = td0_error(
                reward=r_clipped, V=V, V_next=V_next_est, gamma=self.gamma
            )
            # blend with inline TDs if we have them
            if agg.inline_tds:
                td_inline = sum(agg.inline_tds) / len(agg.inline_tds)
                td = 0.5 * td_batch + 0.5 * td_inline
            else:
                td = td_batch

            agg.V = V
            agg.V_next = V_next_est
            agg.td_error = td
            mag = abs(td)
            if mag >= self.hard_threshold:
                agg.strength = "hard"
            elif mag >= self.soft_threshold:
                agg.strength = "soft"
            else:
                agg.strength = "drop"

    @staticmethod
    def apply_value_update(
        old_value: float, aggregate: SkillAggregate
    ) -> float:
        """Bellman-style scalar update.
        new = old + lr * (r + gamma*V_next - V)
        clamped to [1, 10]. Uses the same td_error computed in score()."""
        new = old_value + aggregate.learning_rate * aggregate.td_error
        return _clip(new, 1.0, 10.0)
