from __future__ import annotations

from search import SearchResult
from search.informed import solve_astar as _solve_astar, solve_greedy as _solve_greedy

from ..models.state import GOAL_POSITION_TUPLES, State, manhattan_cells
from .uninformed import _EightPuzzleProblem


def h1_misplaced_tiles(state: State) -> int:
    return min(
        sum(
            1
            for tile in range(1, 9)
            if state.positions[tile] != goal_positions[tile]
        )
        for goal_positions in GOAL_POSITION_TUPLES
    )


def h2_manhattan(state: State) -> int:
    return min(
        sum(
            manhattan_cells(state.positions[tile], goal_positions[tile])
            for tile in range(1, 9)
        )
        for goal_positions in GOAL_POSITION_TUPLES
    )


def solve_astar_h1(initial_state: State) -> SearchResult[State, str]:
    return _solve_astar(
        _EightPuzzleProblem(initial_state=initial_state),
        heuristic=h1_misplaced_tiles,
        algorithm_name="astar_h1",
    )


def solve_astar_h2(initial_state: State) -> SearchResult[State, str]:
    return _solve_astar(
        _EightPuzzleProblem(initial_state=initial_state),
        heuristic=h2_manhattan,
        algorithm_name="astar_h2",
    )


def solve_greedy_h1(initial_state: State) -> SearchResult[State, str]:
    return _solve_greedy(
        _EightPuzzleProblem(initial_state=initial_state),
        heuristic=h1_misplaced_tiles,
        algorithm_name="greedy_h1",
    )


def solve_greedy_h2(initial_state: State) -> SearchResult[State, str]:
    return _solve_greedy(
        _EightPuzzleProblem(initial_state=initial_state),
        heuristic=h2_manhattan,
        algorithm_name="greedy_h2",
    )
