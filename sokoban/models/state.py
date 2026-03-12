from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable

from .position import Position


@dataclass(frozen=True, slots=True)
class State:
    player: Position
    boxes: FrozenSet[Position]

    # Asumimos que tiene que haber al menos una caja y no mas de una caja en la misma posicion.

    def __post_init__(self) -> None:
        if not self.boxes:
            raise ValueError("El estado debe tener al menos una caja.")
        if len(self.boxes) != len(set(self.boxes)):
            raise ValueError("No puede haber cajas repetidas.")

    @classmethod
    def from_iterables(
        cls,
        player: Position,
        boxes: Iterable[Position],
    ) -> "State":
        return cls(player=player, boxes=frozenset(boxes))

    def is_goal_state(self, goals: FrozenSet[Position]) -> bool:
        return self.boxes == goals
