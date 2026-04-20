"""Continual-RL TD(0) layer sitting on top of TextGrad.

For each skill that fired in the session we compute a classical Bellman
TD(0) error:
    delta_TD = r + gamma * V(s') - V(s)
where:
    r      = net delta for this skill this session (clamped to +-2; no lr
             pre-scaling - lr is applied exactly once, in apply_value_update)
    V(s)   = current Q^L 'overall' score for the skill (from skill-values/)
    V(s')  = bootstrap target blending the current firing's reward with a
             rolling-buffer estimate of recent reward (continual-RL style).
             When the skill also self-reported a dominant P4 strategy of
             'refine' or 'reset', V(s') is penalized so the td signal reflects
             the agent's own negative evaluation.
    gamma  = 0.9 default (configurable).

The magnitude of delta_TD scales the textual gradient selection:
    - |delta_TD| >= 1.0  -> keep the full textual gradient, propose spec edit
    - 0.25 <= |delta_TD| < 1.0 -> keep but mark as 'soft' (no proposal)
    - |delta_TD| < 0.25  -> drop (ignore gradient; just bump value slightly)

Plasticity-stability knobs:
  * bootstrap_step (β):     weight on current-firing reward in V(s')
  * replay_step (β2):       weight on buffered-average reward in V(s')
  * buffer_k:               buffer depth (older firings forgotten)
  * STRATEGY_PENALTY:       P4 vote modulation
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .trace import SessionGraph, TraceNode


STRATEGY_PENALTY = {
    "keep": 0.0,
    "refine": 0.5,
    "reset": 1.5,
}


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
    # weight on THIS firing's reward in the V(s') bootstrap
    bootstrap_step: float = 0.5
    # weight on the REPLAY BUFFER average reward in the V(s') bootstrap
    replay_step: float = 0.5

    def score(
        self,
        aggregates: Dict[str, SkillAggregate],
        current_values: Dict[str, float],
        buffer_reader: Optional[Callable[[str], float]] = None,
    ) -> None:
        """Populate V, V_next, td_error, strength on every aggregate in-place.

        CRL-flavored TD(0):
          r         = clipped net_delta (NOT scaled by lr here)
          V(s')     = clip( V + β·r + β2·avg_r_buffer  -  strategy_penalty ,
                            1, 10 )
                      where avg_r_buffer comes from `buffer_reader(skill)`
                      and strategy_penalty is from the dominant P4 vote.
                      If v3 provided predicted_V, we blend the self-report
                      with the bootstrap target 50/50 for stability.
          td        = r + γ·V(s') - V
          strength  = thresholded |td|

        buffer_reader: callable returning the mean reward over the per-skill
                       experience buffer, or 0.0 when empty. If None, the
                       replay term is treated as zero (matches single-firing
                       bootstrap).
        """
        for skill, agg in aggregates.items():
            V = current_values.get(skill, 5.0)
            r = _clip(float(agg.net_delta), -2.0, 2.0)

            avg_r_buffer = 0.0
            if buffer_reader is not None:
                try:
                    avg_r_buffer = float(buffer_reader(skill))
                except Exception:
                    avg_r_buffer = 0.0

            bootstrap_target = _clip(
                V
                + self.bootstrap_step * r
                + self.replay_step * avg_r_buffer,
                1.0,
                10.0,
            )

            # blend with v3 self-report when available (50/50)
            if agg.predicted_Vs:
                self_report = _clip(
                    sum(agg.predicted_Vs) / len(agg.predicted_Vs), 1.0, 10.0
                )
                V_next_target = 0.5 * bootstrap_target + 0.5 * self_report
            else:
                V_next_target = bootstrap_target

            # P4 strategy penalty: agent's own refine/reset vote drops V(s')
            dom = agg.dominant_strategy
            penalty = STRATEGY_PENALTY.get(dom or "", 0.0)
            V_next_est = _clip(V_next_target - penalty, 1.0, 10.0)

            td_batch = td0_error(
                reward=r, V=V, V_next=V_next_est, gamma=self.gamma
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
        """Single-lr value update: new = old + lr · td.
        This is the ONLY place the confidence-based learning rate is applied."""
        new = old_value + aggregate.learning_rate * aggregate.td_error
        return _clip(new, 1.0, 10.0)
