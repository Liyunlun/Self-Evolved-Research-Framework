"""Play Tic-Tac-Toe games between agents. Agent protocol:

    agent(board: Board, symbol: str) -> int   # returns cell 1-9

Two kinds of agents ship here:
  * SkillAgent  — calls ClaudeCodeCLIEngine, wraps prompt with a SKILL.md body
  * MinimaxAgent — deterministic perfect-play oracle (used for eval only)

A game record is a dict with keys:
  roles        : {"X": <agent_name>, "O": <agent_name>}
  moves        : [ {symbol, cell, raw, retries, final_board} ]
  winner       : "X" | "O" | None   (None = draw)
  terminal     : "win" | "draw" | "forfeit"
  forfeit_side : "X" | "O" | None
  forfeit_reason : str | None
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from tic_tac_toe.game import Board, PLAYERS  # type: ignore[import-not-found]
from tic_tac_toe import minimax  # type: ignore[import-not-found]

# Make the textgrad_backend engines importable
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "td-nl"))

from textgrad_backend.engines import ClaudeCodeCLIEngine  # noqa: E402


MOVE_RE = re.compile(r"[1-9]")

SYSTEM_PROMPT_TEMPLATE = """You are playing Tic-Tac-Toe as player {symbol}.

You are operating under the following skill specification. Read it,
then apply it when choosing a move.

=== BEGIN SKILL SPEC ===
{skill_body}
=== END SKILL SPEC ===

Response format (STRICT): reply with exactly one digit 1-9 — the cell
you want to play, using keypad layout. No other text, no whitespace,
no punctuation, no explanation. Just the digit."""

USER_PROMPT_TEMPLATE = """Current board (your symbol is {symbol}):

{board_render}

Legal cells: {legal}

Your move (one digit 1-9):"""


def strip_frontmatter(text: str) -> str:
    """Return the body of a SKILL.md (YAML frontmatter removed)."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip()
    return text


def parse_move(raw: str, legal: List[int]) -> Optional[int]:
    """Extract the first legal digit from raw output. Returns None if none."""
    for ch in raw:
        if ch.isdigit() and int(ch) in legal:
            return int(ch)
    for m in MOVE_RE.finditer(raw):
        cell = int(m.group())
        if cell in legal:
            return cell
    return None


@dataclass
class MoveRecord:
    symbol: str
    cell: int
    raw: str
    retries: int
    board_after: str


@dataclass
class GameRecord:
    roles: Dict[str, str]
    moves: List[MoveRecord] = field(default_factory=list)
    winner: Optional[str] = None
    terminal: str = "win"  # win | draw | forfeit
    forfeit_side: Optional[str] = None
    forfeit_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "roles": self.roles,
            "moves": [m.__dict__ for m in self.moves],
            "winner": self.winner,
            "terminal": self.terminal,
            "forfeit_side": self.forfeit_side,
            "forfeit_reason": self.forfeit_reason,
        }


def grade_game(record: GameRecord) -> dict:
    """Replay a game and count per-side mistakes vs minimax. A mistake is
    a played cell that isn't in the optimal-moves set for that position.
    Does NOT call any LLM - pure over the recorded moves."""
    board = Board()
    grading = {
        "X_moves": 0,
        "O_moves": 0,
        "X_mistakes": 0,
        "O_mistakes": 0,
        "move_trace": [],
    }
    for m in record.moves:
        if board.is_terminal():
            break
        to_move = m.symbol
        opt = minimax.optimal_moves(board, to_move)
        is_mistake = m.cell not in opt
        grading[f"{to_move}_moves"] += 1
        if is_mistake:
            grading[f"{to_move}_mistakes"] += 1
        grading["move_trace"].append(
            {
                "symbol": to_move,
                "cell": m.cell,
                "optimal": opt,
                "mistake": is_mistake,
            }
        )
        board.play(m.cell, to_move)
    return grading


Agent = Callable[[Board, str], int]


def skill_agent(
    engine: ClaudeCodeCLIEngine,
    skill_path: Path,
    name: str = "skill-agent",
) -> Agent:
    """Build a SkillAgent bound to a specific SKILL.md file. The spec is
    read once at agent construction; callers that want to test an evolved
    spec should create a fresh agent after the spec changes."""
    body = strip_frontmatter(skill_path.read_text(encoding="utf-8"))

    def agent(board: Board, symbol: str) -> int:
        legal = board.legal_moves()
        system = SYSTEM_PROMPT_TEMPLATE.format(symbol=symbol, skill_body=body)
        user = USER_PROMPT_TEMPLATE.format(
            symbol=symbol,
            board_render=board.render(),
            legal=", ".join(str(c) for c in legal),
        )
        last_raw = ""
        last_err: Optional[Exception] = None
        for attempt in range(2):
            prompt = user
            if attempt == 1:
                prompt += (
                    "\n\nYour previous response was not a valid legal cell. "
                    "Reply with exactly one digit from this list: "
                    f"{', '.join(str(c) for c in legal)}."
                )
            try:
                raw = engine(prompt, system_prompt=system)
            except Exception as e:  # timeout / CLI error / non-zero exit
                last_err = e
                last_raw = f"<engine error: {type(e).__name__}: {str(e)[:120]}>"
                continue
            last_raw = raw
            cell = parse_move(raw, legal)
            if cell is not None:
                agent.last_raw = raw  # type: ignore[attr-defined]
                agent.last_retries = attempt  # type: ignore[attr-defined]
                return cell
        agent.last_raw = last_raw  # type: ignore[attr-defined]
        agent.last_retries = 2  # type: ignore[attr-defined]
        reason = (
            f"{name}({symbol}) failed to emit a legal move after 2 attempts; "
            f"last_raw={last_raw!r}"
        )
        if last_err is not None:
            reason += f"; last_err={type(last_err).__name__}"
        raise ForfeitError(reason)

    agent.__name__ = name  # type: ignore[attr-defined]
    return agent


def minimax_agent(name: str = "minimax") -> Agent:
    def agent(board: Board, symbol: str) -> int:
        return minimax.best_move(board, symbol)

    agent.__name__ = name  # type: ignore[attr-defined]
    agent.last_raw = ""  # type: ignore[attr-defined]
    agent.last_retries = 0  # type: ignore[attr-defined]
    return agent


class ForfeitError(RuntimeError):
    pass


def play_one_game(x_agent: Agent, o_agent: Agent) -> GameRecord:
    """Play one game; X moves first. Never raises - forfeits on bad output."""
    board = Board()
    record = GameRecord(
        roles={
            "X": getattr(x_agent, "__name__", "x"),
            "O": getattr(o_agent, "__name__", "o"),
        }
    )
    to_move = "X"
    while not board.is_terminal():
        agent = x_agent if to_move == "X" else o_agent
        try:
            cell = agent(board, to_move)
        except ForfeitError as e:
            record.terminal = "forfeit"
            record.forfeit_side = to_move
            record.forfeit_reason = str(e)
            record.winner = "O" if to_move == "X" else "X"
            return record
        if cell not in board.legal_moves():
            record.terminal = "forfeit"
            record.forfeit_side = to_move
            record.forfeit_reason = f"illegal cell {cell}"
            record.winner = "O" if to_move == "X" else "X"
            return record
        board.play(cell, to_move)
        record.moves.append(
            MoveRecord(
                symbol=to_move,
                cell=cell,
                raw=str(getattr(agent, "last_raw", ""))[:200],
                retries=int(getattr(agent, "last_retries", 0)),
                board_after=board.ascii_state(),
            )
        )
        to_move = "O" if to_move == "X" else "X"

    w = board.winner()
    if w is None:
        record.terminal = "draw"
    else:
        record.terminal = "win"
        record.winner = w
    return record
