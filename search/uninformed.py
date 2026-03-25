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
    frontier_nodes: int
    max_frontier_nodes: int


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
    max_frontier_nodes = 1

    while frontier:
        max_frontier_nodes = max(max_frontier_nodes, len(frontier))
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
                frontier_nodes=len(frontier),
                max_frontier_nodes=max_frontier_nodes,
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
        frontier_nodes=len(frontier),
        max_frontier_nodes=max_frontier_nodes,
    )


def solve_dfs(
    problem: SearchProblem[StateT, ActionT],
    depth_limit: int = 10_000,
) -> SearchResult[StateT, ActionT]:
    _validate_non_negative(depth_limit, "depth_limit")
    result, _, _, _, _ = _run_depth_limited_iteration(
        problem=problem,
        depth_limit=depth_limit,
        algorithm_name="dfs",
    )
    return result


def solve_dls(
    problem: SearchProblem[StateT, ActionT],
    depth_limit: int,
) -> SearchResult[StateT, ActionT]:
    _validate_non_negative(depth_limit, "depth_limit")
    result, _, _, _, _ = _run_depth_limited_iteration(
        problem=problem,
        depth_limit=depth_limit,
        algorithm_name="dls",
    )
    return result


def solve_iddfs(
    problem: SearchProblem[StateT, ActionT],
    max_depth: int = 10_000,
) -> SearchResult[StateT, ActionT]:
    _validate_non_negative(max_depth, "max_depth")

    total_expanded_nodes = 0
    total_generated_nodes = 0
    visited_states: set[StateT] = {problem.initial_state}
    overall_max_frontier = 0

    for depth_limit in range(max_depth + 1):
        partial_result, cutoff, partial_visited, frontier_nodes, iter_max_frontier = _run_depth_limited_iteration(
            problem=problem,
            depth_limit=depth_limit,
            algorithm_name="iddfs",
            allow_shallower_revisit=True,
        )
        total_expanded_nodes += partial_result.expanded_nodes
        total_generated_nodes += partial_result.generated_nodes
        visited_states.update(partial_visited)
        overall_max_frontier = max(overall_max_frontier, iter_max_frontier)

        if partial_result.found:
            return SearchResult(
                algorithm="iddfs",
                found=True,
                path_states=partial_result.path_states,
                actions=partial_result.actions,
                expanded_nodes=total_expanded_nodes,
                generated_nodes=total_generated_nodes,
                visited_nodes=len(visited_states),
                frontier_nodes=frontier_nodes,
                max_frontier_nodes=overall_max_frontier,
            )

        if not cutoff:
            break

    return SearchResult(
        algorithm="iddfs",
        found=False,
        path_states=(problem.initial_state,),
        actions=tuple(),
        expanded_nodes=total_expanded_nodes,
        generated_nodes=total_generated_nodes,
        visited_nodes=len(visited_states),
        frontier_nodes=0,
        max_frontier_nodes=overall_max_frontier,
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


def _run_depth_limited_iteration(
    problem: SearchProblem[StateT, ActionT],
    depth_limit: int,
    algorithm_name: str,
    allow_shallower_revisit: bool = False,
) -> tuple[SearchResult[StateT, ActionT], bool, set[StateT], int, int]:
    initial_state = problem.initial_state
    frontier: list[_Node[StateT, ActionT]] = [_Node(state=initial_state, parent=None, action=None, depth=0)]
    visited_states: set[StateT] = {initial_state}
    min_depth_seen: dict[StateT, int] | None = {initial_state: 0} if allow_shallower_revisit else None
    expanded_nodes = 0
    generated_nodes = 0
    reached_depth_limit = False
    max_frontier_nodes = 1

    while frontier:
        max_frontier_nodes = max(max_frontier_nodes, len(frontier))
        current = frontier.pop()
        expanded_nodes += 1

        if problem.is_goal(current.state):
            path_states, actions = _reconstruct_path(current)
            return (
                SearchResult(
                    algorithm=algorithm_name,
                    found=True,
                    path_states=path_states,
                    actions=actions,
                    expanded_nodes=expanded_nodes,
                    generated_nodes=generated_nodes,
                    visited_nodes=len(visited_states),
                    frontier_nodes=len(frontier),
                    max_frontier_nodes=max_frontier_nodes,
                ),
                reached_depth_limit,
                visited_states,
                len(frontier),
                max_frontier_nodes,
            )

        if current.depth >= depth_limit:
            reached_depth_limit = True
            continue

        next_depth = current.depth + 1
        next_nodes: list[_Node[StateT, ActionT]] = []
        for action, next_state in problem.successors(current.state):
            generated_nodes += 1

            if min_depth_seen is not None:
                prev_depth = min_depth_seen.get(next_state)
                if prev_depth is not None and prev_depth <= next_depth:
                    continue
                min_depth_seen[next_state] = next_depth
            elif next_state in visited_states:
                continue

            visited_states.add(next_state)
            next_nodes.append(
                _Node(
                    state=next_state,
                    parent=current,
                    action=action,
                    depth=next_depth,
                )
            )

        frontier.extend(reversed(next_nodes))

    return (
        SearchResult(
            algorithm=algorithm_name,
            found=False,
            path_states=(initial_state,),
            actions=tuple(),
            expanded_nodes=expanded_nodes,
            generated_nodes=generated_nodes,
            visited_nodes=len(visited_states),
            frontier_nodes=len(frontier),
            max_frontier_nodes=max_frontier_nodes,
        ),
        reached_depth_limit,
        visited_states,
        len(frontier),
        max_frontier_nodes,
    )


def _validate_non_negative(value: int, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
