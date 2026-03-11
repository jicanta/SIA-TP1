from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Iterable

from .position import Position


@dataclass(frozen=True, slots=True)
class State:
    player: Position
    boxes: FrozenSet[Position]
    goals: FrozenSet[Position] = field(default_factory=frozenset)

    # Asumimos que tiene que haber al menos una caja, e igual cantidad de cajas y 'metas'
    # A su vez, asumimos que no hay más de una caja o meta en la misma posición

    def __post_init__(self) -> None:
        if not self.boxes:
            raise ValueError("El estado debe tener al menos una caja.")
        if len(self.boxes) != len(set(self.boxes)):
            raise ValueError("No puede haber cajas repetidas.")
        if len(self.goals) != len(set(self.goals)):
            raise ValueError("No puede haber metas repetidas.")
        if len(self.goals) and len(self.boxes) != len(self.goals):
            raise ValueError("La cantidad de cajas y metas debe coincidir.")

    @classmethod
    def from_iterables(
        cls,
        player: Position,
        boxes: Iterable[Position],
        goals: Iterable[Position],
    ) -> "State":
        return cls(player=player, boxes=frozenset(boxes), goals=frozenset(goals))

    def is_goal_state(self) -> bool:
        return self.boxes == self.goals
