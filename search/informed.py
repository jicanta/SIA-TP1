from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count
from typing import Callable, Generic, Hashable, TypeVar

from .uninformed import SearchProblem, SearchResult

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT")


@dataclass(slots=True)
class _Node(Generic[StateT, ActionT]):
    state: StateT
    parent: _Node[StateT, ActionT] | None
    action: ActionT | None
    g_cost: float


def _reconstruct_path(
    goal_node: _Node[StateT, ActionT],
) -> tuple[tuple[StateT, ...], tuple[ActionT, ...]]:
    states: list[StateT] = []
    actions: list[ActionT] = []
    cursor: _Node[StateT, ActionT] | None = goal_node
    while cursor is not None:
        states.append(cursor.state)
        if cursor.action is not None:
            actions.append(cursor.action)
        cursor = cursor.parent
    states.reverse()
    actions.reverse()
    return tuple(states), tuple(actions)


def solve_astar(
    problem: SearchProblem[StateT, ActionT],
    heuristic: Callable[[StateT], float],
    algorithm_name: str = "astar",
) -> SearchResult[StateT, ActionT]:
    initial_state = problem.initial_state
    start_node: _Node[StateT, ActionT] = _Node(
        state=initial_state, parent=None, action=None, g_cost=0.0
    )
    tiebreak = count()
    frontier: list[tuple[float, int, _Node[StateT, ActionT]]] = [
        (heuristic(initial_state), next(tiebreak), start_node)
    ]
    best_g: dict[StateT, float] = {initial_state: 0.0}
    closed: set[StateT] = set()
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.state in closed:
            continue
        closed.add(current.state)
        expanded_nodes += 1

        if problem.is_goal(current.state):
            path_states, actions = _reconstruct_path(current)
            return SearchResult(
                algorithm=algorithm_name,
                found=True,
                path_states=path_states,
                actions=actions,
                expanded_nodes=expanded_nodes,
                generated_nodes=generated_nodes,
                visited_nodes=len(closed),
            )

        for action, next_state in problem.successors(current.state):
            generated_nodes += 1
            if next_state in closed:
                continue
            new_g = current.g_cost + 1.0
            if new_g >= best_g.get(next_state, float("inf")):
                continue
            best_g[next_state] = new_g
            next_node: _Node[StateT, ActionT] = _Node(
                state=next_state, parent=current, action=action, g_cost=new_g
            )
            heapq.heappush(
                frontier, (new_g + heuristic(next_state), next(tiebreak), next_node)
            )

    return SearchResult(
        algorithm=algorithm_name,
        found=False,
        path_states=(initial_state,),
        actions=tuple(),
        expanded_nodes=expanded_nodes,
        generated_nodes=generated_nodes,
        visited_nodes=len(closed),
    )


def solve_greedy(
    problem: SearchProblem[StateT, ActionT],
    heuristic: Callable[[StateT], float],
    algorithm_name: str = "greedy",
) -> SearchResult[StateT, ActionT]:
    initial_state = problem.initial_state
    start_node: _Node[StateT, ActionT] = _Node(
        state=initial_state, parent=None, action=None, g_cost=0.0
    )
    tiebreak = count()
    frontier: list[tuple[float, int, _Node[StateT, ActionT]]] = [
        (heuristic(initial_state), next(tiebreak), start_node)
    ]
    visited: set[StateT] = set()
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.state in visited:
            continue
        visited.add(current.state)
        expanded_nodes += 1

        if problem.is_goal(current.state):
            path_states, actions = _reconstruct_path(current)
            return SearchResult(
                algorithm=algorithm_name,
                found=True,
                path_states=path_states,
                actions=actions,
                expanded_nodes=expanded_nodes,
                generated_nodes=generated_nodes,
                visited_nodes=len(visited),
            )

        for action, next_state in problem.successors(current.state):
            generated_nodes += 1
            if next_state in visited:
                continue
            next_node: _Node[StateT, ActionT] = _Node(
                state=next_state,
                parent=current,
                action=action,
                g_cost=current.g_cost + 1.0,
            )
            heapq.heappush(
                frontier, (heuristic(next_state), next(tiebreak), next_node)
            )

    return SearchResult(
        algorithm=algorithm_name,
        found=False,
        path_states=(initial_state,),
        actions=tuple(),
        expanded_nodes=expanded_nodes,
        generated_nodes=generated_nodes,
        visited_nodes=len(visited),
    )
