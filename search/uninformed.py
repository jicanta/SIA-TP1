from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Generic, Hashable, Iterable, Protocol, TypeVar

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT")


class SearchProblem(Protocol[StateT, ActionT]):
    initial_state: StateT

    def is_goal(self, state: StateT) -> bool: ...

    def successors(self, state: StateT) -> Iterable[tuple[ActionT, StateT]]: ...


@dataclass(frozen=True, slots=True)
class SearchResult(Generic[StateT, ActionT]):
    algorithm: str
    found: bool
    path_states: tuple[StateT, ...]
    actions: tuple[ActionT, ...]
    expanded_nodes: int
    generated_nodes: int
    visited_nodes: int


@dataclass(slots=True)
class _Node(Generic[StateT, ActionT]):
    state: StateT
    parent: _Node[StateT, ActionT] | None
    action: ActionT | None
    depth: int


def solve_bfs(problem: SearchProblem[StateT, ActionT]) -> SearchResult[StateT, ActionT]:
    initial_state = problem.initial_state
    frontier: deque[_Node[StateT, ActionT]] = deque(
        [_Node(state=initial_state, parent=None, action=None, depth=0)]
    )
    visited: set[StateT] = {initial_state}
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        current = frontier.popleft()
        expanded_nodes += 1

        if problem.is_goal(current.state):
            path_states, actions = _reconstruct_path(current)
            return SearchResult(
                algorithm="bfs",
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
            visited.add(next_state)
            frontier.append(
                _Node(
                    state=next_state,
                    parent=current,
                    action=action,
                    depth=current.depth + 1,
                )
            )

    return SearchResult(
        algorithm="bfs",
        found=False,
        path_states=(initial_state,),
        actions=tuple(),
        expanded_nodes=expanded_nodes,
        generated_nodes=generated_nodes,
        visited_nodes=len(visited),
    )


def solve_dfs(
    problem: SearchProblem[StateT, ActionT],
    depth_limit: int = 10_000,
) -> SearchResult[StateT, ActionT]:
    initial_state = problem.initial_state
    frontier: list[_Node[StateT, ActionT]] = [_Node(state=initial_state, parent=None, action=None, depth=0)]
    visited: set[StateT] = {initial_state}
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        current = frontier.pop()
        expanded_nodes += 1

        if problem.is_goal(current.state):
            path_states, actions = _reconstruct_path(current)
            return SearchResult(
                algorithm="dfs",
                found=True,
                path_states=path_states,
                actions=actions,
                expanded_nodes=expanded_nodes,
                generated_nodes=generated_nodes,
                visited_nodes=len(visited),
            )

        if current.depth >= depth_limit:
            continue

        next_nodes: list[_Node[StateT, ActionT]] = []
        for action, next_state in problem.successors(current.state):
            generated_nodes += 1
            if next_state in visited:
                continue
            visited.add(next_state)
            next_nodes.append(
                _Node(
                    state=next_state,
                    parent=current,
                    action=action,
                    depth=current.depth + 1,
                )
            )

        frontier.extend(reversed(next_nodes))

    return SearchResult(
        algorithm="dfs",
        found=False,
        path_states=(initial_state,),
        actions=tuple(),
        expanded_nodes=expanded_nodes,
        generated_nodes=generated_nodes,
        visited_nodes=len(visited),
    )


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
