from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from ..models.board import Board
from ..models.state import State

DIRECTIONS: tuple[tuple[str, int, int], ...] = (
    ("U", -1, 0),
    ("D", 1, 0),
    ("L", 0, -1),
    ("R", 0, 1),
)


@dataclass(frozen=True, slots=True)
class SearchResult:
    algorithm: str
    found: bool
    path_states: tuple[State, ...]
    actions: tuple[str, ...]
    expanded_nodes: int
    generated_nodes: int
    visited_nodes: int


@dataclass(slots=True)
class _Node:
    state: State
    parent: _Node | None
    action: str | None
    depth: int


def solve_bfs(initial_state: State, board: Board) -> SearchResult:
    frontier: deque[_Node] = deque([_Node(state=initial_state, parent=None, action=None, depth=0)])
    visited: set[State] = {initial_state}
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        current = frontier.popleft()
        expanded_nodes += 1

        if current.state.is_goal_state(board.goals):
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

        for action, next_state in _successors(current.state, board):
            generated_nodes += 1
            if next_state in visited:
                continue
            visited.add(next_state)
            frontier.append(_Node(state=next_state, parent=current, action=action, depth=current.depth + 1))

    return SearchResult(
        algorithm="bfs",
        found=False,
        path_states=(initial_state,),
        actions=tuple(),
        expanded_nodes=expanded_nodes,
        generated_nodes=generated_nodes,
        visited_nodes=len(visited),
    )


def solve_dfs(initial_state: State, board: Board, depth_limit: int = 10_000) -> SearchResult:
    frontier: list[_Node] = [_Node(state=initial_state, parent=None, action=None, depth=0)]
    visited: set[State] = {initial_state}
    expanded_nodes = 0
    generated_nodes = 0

    while frontier:
        current = frontier.pop()
        expanded_nodes += 1

        if current.state.is_goal_state(board.goals):
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

        next_nodes: list[_Node] = []
        for action, next_state in _successors(current.state, board):
            generated_nodes += 1
            if next_state in visited:
                continue
            visited.add(next_state)
            next_nodes.append(_Node(state=next_state, parent=current, action=action, depth=current.depth + 1))

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


def _successors(state: State, board: Board) -> Iterable[tuple[str, State]]:
    for action, d_row, d_col in DIRECTIONS:
        next_player = state.player.move(d_row, d_col)
        if not board.contains(next_player) or next_player in board.walls:
            continue

        boxes = set(state.boxes)
        if next_player in boxes:
            next_box = next_player.move(d_row, d_col)
            if not board.contains(next_box):
                continue
            if next_box in board.walls or next_box in boxes:
                continue
            boxes.remove(next_player)
            boxes.add(next_box)

        yield action, State(player=next_player, boxes=frozenset(boxes))


def _reconstruct_path(goal_node: _Node) -> tuple[tuple[State, ...], tuple[str, ...]]:
    states: list[State] = []
    actions: list[str] = []
    cursor: _Node | None = goal_node

    while cursor is not None:
        states.append(cursor.state)
        if cursor.action is not None:
            actions.append(cursor.action)
        cursor = cursor.parent

    states.reverse()
    actions.reverse()
    return tuple(states), tuple(actions)
