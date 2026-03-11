from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    row: int
    col: int

    def move(self, d_row: int, d_col: int) -> "Position":
        return Position(self.row + d_row, self.col + d_col)
