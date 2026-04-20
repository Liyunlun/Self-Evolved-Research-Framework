"""Pure Tic-Tac-Toe board logic. No I/O, no LLM calls.

Cells are 1-9 (keypad layout):
    1 | 2 | 3
   -----------
    4 | 5 | 6
   -----------
    7 | 8 | 9
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

WINNING_LINES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3), (4, 5, 6), (7, 8, 9),   # rows
    (1, 4, 7), (2, 5, 8), (3, 6, 9),   # columns
    (1, 5, 9), (3, 5, 7),              # diagonals
)

EMPTY = "."
PLAYERS: Tuple[str, str] = ("X", "O")


@dataclass
class Board:
    cells: List[str] = field(default_factory=lambda: [EMPTY] * 9)

    def copy(self) -> "Board":
        return Board(cells=list(self.cells))

    def legal_moves(self) -> List[int]:
        return [i + 1 for i, c in enumerate(self.cells) if c == EMPTY]

    def play(self, cell: int, symbol: str) -> None:
        if cell not in range(1, 10):
            raise ValueError(f"cell out of range: {cell}")
        if symbol not in PLAYERS:
            raise ValueError(f"invalid symbol: {symbol}")
        if self.cells[cell - 1] != EMPTY:
            raise ValueError(f"cell {cell} not empty: {self.cells[cell - 1]}")
        self.cells[cell - 1] = symbol

    def winner(self) -> Optional[str]:
        for a, b, c in WINNING_LINES:
            va, vb, vc = self.cells[a - 1], self.cells[b - 1], self.cells[c - 1]
            if va != EMPTY and va == vb == vc:
                return va
        return None

    def is_full(self) -> bool:
        return EMPTY not in self.cells

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_full()

    def render(self) -> str:
        def cell(i: int) -> str:
            c = self.cells[i]
            return c if c != EMPTY else str(i + 1)
        rows = []
        for r in range(3):
            rows.append(" " + " | ".join(cell(r * 3 + k) for k in range(3)))
            if r < 2:
                rows.append("-----------")
        return "\n".join(rows)

    def ascii_state(self) -> str:
        """Compact single-line state useful for G2 evidence."""
        return "".join(self.cells)
