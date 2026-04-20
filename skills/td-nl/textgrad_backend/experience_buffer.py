"""Per-skill experience buffer for continual-RL TD(0).

Each skill has an append-only JSONL file at
`skill-values/<skill>.experience.jsonl` that stores the last K transitions.
A transition is the outcome of one firing from the agent's perspective:

    {"session_id": str, "reward": int, "predicted_V": float|null,
     "strategy": "keep"|"refine"|"reset"|null, "timestamp": str}

The buffer is bounded to K entries by rotation at append time. `read_recent`
returns the most recent <= K entries (newest first is the common use, but we
return oldest-first to mirror the file order — consumers can reverse if they
want a recency-weighted view).

Design invariants:
  * Pure read/write on disk — no interpretation of semantics.
  * One file per skill — no cross-skill coupling.
  * Bounded size enforced on every append — no unbounded growth.
  * Safe to call from single-process sequential runs. (Concurrent writers
    would need file locking; not supported here since run_cycle is serial.)
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_K = 20


def _path(skill_values_dir: Path, skill: str) -> Path:
    return skill_values_dir / f"{skill}.experience.jsonl"


def read_recent(
    skill_values_dir: Path, skill: str, k: int = DEFAULT_K
) -> List[dict]:
    """Return up to k most recent entries in chronological order.
    Returns [] when the file doesn't exist."""
    p = _path(skill_values_dir, skill)
    if not p.exists():
        return []
    entries: List[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if len(entries) > k:
        entries = entries[-k:]
    return entries


def mean_reward(entries: Iterable[dict]) -> float:
    """Mean of `reward` field across entries. Returns 0.0 for empty input."""
    rewards = [float(e.get("reward", 0)) for e in entries]
    if not rewards:
        return 0.0
    return sum(rewards) / len(rewards)


def append(
    skill_values_dir: Path,
    skill: str,
    reward: float,
    *,
    session_id: str = "",
    predicted_V: Optional[float] = None,
    strategy: Optional[str] = None,
    k: int = DEFAULT_K,
    timestamp: Optional[str] = None,
) -> None:
    """Append a single transition and truncate to last k entries."""
    skill_values_dir.mkdir(parents=True, exist_ok=True)
    p = _path(skill_values_dir, skill)
    entry = {
        "session_id": session_id,
        "reward": float(reward),
        "predicted_V": predicted_V,
        "strategy": strategy,
        "timestamp": timestamp or _dt.datetime.now().isoformat(timespec="seconds"),
    }
    # Load existing, append, truncate, rewrite.
    existing = read_recent(skill_values_dir, skill, k=10_000)
    existing.append(entry)
    if len(existing) > k:
        existing = existing[-k:]
    p.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in existing) + "\n",
        encoding="utf-8",
    )
