"""Perfect-play Tic-Tac-Toe oracle via minimax with memoization.

Used ONLY for evaluation (measuring skill-under-test win rate against
optimal play). Never used to generate training signal, so it does not
contaminate the learned spec.

API:
    best_move(board, to_move) -> int        # cell 1-9
    score(board, to_move) -> int            # +1 win-for-to-move, 0 draw, -1 loss

Uses negamax framing: score is from the perspective of `to_move`.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

from .game import Board, EMPTY, WINNING_LINES, PLAYERS


def _key(cells: Tuple[str, ...], to_move: str) -> Tuple[Tuple[str, ...], str]:
    return (cells, to_move)


@lru_cache(maxsize=None)
def _negamax(cells: Tuple[str, ...], to_move: str) -> Tuple[int, int]:
    """Returns (score, best_cell). score is from `to_move`'s perspective.
    best_cell is the move achieving that score (0 if terminal)."""
    # check terminal
    for a, b, c in WINNING_LINES:
        va, vb, vc = cells[a - 1], cells[b - 1], cells[c - 1]
        if va != EMPTY and va == vb == vc:
            # previous mover already won, so `to_move` has lost
            return (-1, 0)
    if EMPTY not in cells:
        return (0, 0)

    other = "O" if to_move == "X" else "X"
    best_score = -2
    best_cell = 0
    for i, c in enumerate(cells):
        if c != EMPTY:
            continue
        new_cells = cells[:i] + (to_move,) + cells[i + 1 :]
        opp_score, _ = _negamax(new_cells, other)
        score = -opp_score
        if score > best_score:
            best_score = score
            best_cell = i + 1
            if best_score == 1:
                break  # can't do better
    return (best_score, best_cell)


def best_move(board: Board, to_move: str) -> int:
    if to_move not in PLAYERS:
        raise ValueError(f"invalid to_move: {to_move}")
    _, cell = _negamax(tuple(board.cells), to_move)
    if cell == 0:
        raise ValueError("no legal move - board is terminal")
    return cell


def score(board: Board, to_move: str) -> int:
    s, _ = _negamax(tuple(board.cells), to_move)
    return s


def optimal_moves(board: Board, to_move: str) -> List[int]:
    """Return all cells tied for maximum minimax score from this position.
    A move is 'optimal' iff it appears in this list. Used to grade
    arbitrary play against perfect play (for training-signal generation)."""
    if to_move not in PLAYERS:
        raise ValueError(f"invalid to_move: {to_move}")
    best_score, _ = _negamax(tuple(board.cells), to_move)
    other = "O" if to_move == "X" else "X"
    cells = tuple(board.cells)
    tied: List[int] = []
    for i, c in enumerate(cells):
        if c != EMPTY:
            continue
        new_cells = cells[:i] + (to_move,) + cells[i + 1 :]
        opp_score, _ = _negamax(new_cells, other)
        if -opp_score == best_score:
            tied.append(i + 1)
    return tied
