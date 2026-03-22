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

from ..models.state import BOARD_SIZE, State

DIRECTIONS: tuple[tuple[str, int, int], ...] = (
    ("U", -1, 0),
    ("D", 1, 0),
    ("L", 0, -1),
    ("R", 0, 1),
)


@dataclass(slots=True)
class _EightPuzzleProblem:
    initial_state: State

    def is_goal(self, state: State) -> bool:
        return state.is_goal_state()

    def successors(self, state: State) -> Iterable[tuple[str, State]]:
        board = list(state.board)
        blank_cell = state.blank_cell
        blank_row, blank_col = divmod(blank_cell, BOARD_SIZE)

        for action, d_row, d_col in DIRECTIONS:
            next_row = blank_row + d_row
            next_col = blank_col + d_col
            if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
                continue

            swapped_cell = next_row * BOARD_SIZE + next_col
            next_board = list(board)
            next_board[blank_cell], next_board[swapped_cell] = (
                next_board[swapped_cell],
                next_board[blank_cell],
            )
            yield action, State(board=tuple(next_board))


def solve_bfs(initial_state: State) -> SearchResult[State, str]:
    return solve_generic_bfs(_EightPuzzleProblem(initial_state=initial_state))


def solve_dfs(
    initial_state: State,
    depth_limit: int = 10_000,
) -> SearchResult[State, str]:
    return solve_generic_dfs(
        _EightPuzzleProblem(initial_state=initial_state),
        depth_limit=depth_limit,
    )


def solve_dls(
    initial_state: State,
    depth_limit: int,
) -> SearchResult[State, str]:
    return solve_generic_dls(
        _EightPuzzleProblem(initial_state=initial_state),
        depth_limit=depth_limit,
    )


def solve_iddfs(
    initial_state: State,
    max_depth: int = 10_000,
) -> SearchResult[State, str]:
    return solve_generic_iddfs(
        _EightPuzzleProblem(initial_state=initial_state),
        max_depth=max_depth,
    )
