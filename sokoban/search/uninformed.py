from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from search import (
    SearchResult,
    solve_bfs as solve_generic_bfs,
    solve_dfs as solve_generic_dfs,
    solve_dls as solve_generic_dls,
    solve_iddfs as solve_generic_iddfs,
)

from ..models.board import Board
from ..models.state import State

DIRECTIONS: tuple[tuple[str, int, int], ...] = (
    ("U", -1, 0),
    ("D", 1, 0),
    ("L", 0, -1),
    ("R", 0, 1),
)


@dataclass(slots=True)
class _SokobanProblem:
    initial_state: State
    board: Board

    def is_goal(self, state: State) -> bool:
        return state.is_goal_state(self.board.goals)

    def successors(self, state: State) -> Iterable[tuple[str, State]]:
        for action, d_row, d_col in DIRECTIONS:
            next_player = state.player.move(d_row, d_col)
            if not self.board.contains(next_player) or next_player in self.board.walls:
                continue

            boxes = set(state.boxes)
            if next_player in boxes:
                next_box = next_player.move(d_row, d_col)
                if not self.board.contains(next_box):
                    continue
                if next_box in self.board.walls or next_box in boxes:
                    continue
                boxes.remove(next_player)
                boxes.add(next_box)

            yield action, State(player=next_player, boxes=frozenset(boxes))


def solve_bfs(initial_state: State, board: Board) -> SearchResult[State, str]:
    return solve_generic_bfs(_SokobanProblem(initial_state=initial_state, board=board))


def solve_dfs(
    initial_state: State,
    board: Board,
    depth_limit: int = 10_000,
) -> SearchResult[State, str]:
    return solve_generic_dfs(
        _SokobanProblem(initial_state=initial_state, board=board),
        depth_limit=depth_limit,
    )


def solve_dls(
    initial_state: State,
    board: Board,
    depth_limit: int,
) -> SearchResult[State, str]:
    return solve_generic_dls(
        _SokobanProblem(initial_state=initial_state, board=board),
        depth_limit=depth_limit,
    )


def solve_iddfs(
    initial_state: State,
    board: Board,
    max_depth: int = 10_000,
) -> SearchResult[State, str]:
    return solve_generic_iddfs(
        _SokobanProblem(initial_state=initial_state, board=board),
        max_depth=max_depth,
    )
