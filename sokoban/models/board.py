from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Iterable

from .position import Position


@dataclass(frozen=True, slots=True)
class Board:
    rows: int
    cols: int
    walls: FrozenSet[Position]
    goals: FrozenSet[Position] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("rows y cols deben ser mayores a 0.")
        for wall in self.walls:
            if not self.contains(wall):
                raise ValueError(f"Pared fuera de rango: {wall}")

        for goal in self.goals:
            if not self.contains(goal):
                raise ValueError(f"Meta fuera de rango: {goal}")
            if goal in self.walls:
                raise ValueError(f"Meta sobre pared: {goal}")

    @classmethod
    def from_iterables(
        cls,
        rows: int,
        cols: int,
        walls: Iterable[Position],
        goals: Iterable[Position] = (),
    ) -> "Board":
        return cls(rows=rows, cols=cols, walls=frozenset(walls), goals=frozenset(goals))

    def contains(self, pos: Position) -> bool:
        return 0 <= pos.row < self.rows and 0 <= pos.col < self.cols
