from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models.board import Board
from .models.position import Position
from .models.state import State


@dataclass(frozen=True, slots=True)
class RenderConfig:
    cell_size: int
    margin: int
    draw_grid: bool
    color_background: tuple[int, int, int]
    color_floor: tuple[int, int, int]
    color_grid: tuple[int, int, int]
    color_wall: tuple[int, int, int]
    color_goal: tuple[int, int, int]
    color_box: tuple[int, int, int]
    color_player: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class WindowConfig:
    title: str
    fps: int


@dataclass(frozen=True, slots=True)
class SearchConfig:
    algorithm: str
    dfs_depth_limit: int
    animation_step_seconds: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    window: WindowConfig
    render: RenderConfig
    search: SearchConfig
    board: Board
    initial_state: State

    @property
    def window_width(self) -> int:
        return self.render.margin * 2 + self.board.cols * self.render.cell_size

    @property
    def window_height(self) -> int:
        return self.render.margin * 2 + self.board.rows * self.render.cell_size


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    board_data = data.get("board", {})
    state_data = data.get("state", {})
    render_data = data.get("render", {})
    colors_data = render_data.get("colors", {})
    window_data = data.get("window", {})
    search_data = data.get("search", {})

    goals_data = board_data.get("goals", state_data.get("goals", []))

    board = Board.from_iterables(
        rows=int(board_data["rows"]),
        cols=int(board_data["cols"]),
        walls=[_position_from_list(item) for item in board_data.get("walls", [])],
        goals=[_position_from_list(item) for item in goals_data],
    )

    initial_state = State.from_iterables(
        player=_position_from_list(state_data["player"]),
        boxes=[_position_from_list(item) for item in state_data.get("boxes", [])],
    )

    _validate_entities_inside_board(board, initial_state)

    render = RenderConfig(
        cell_size=int(render_data.get("cell_size", 64)),
        margin=int(render_data.get("margin", 20)),
        draw_grid=bool(render_data.get("draw_grid", True)),
        color_background=_hex_to_rgb(colors_data.get("background", "#0f172a")),
        color_floor=_hex_to_rgb(colors_data.get("floor", "#1f2937")),
        color_grid=_hex_to_rgb(colors_data.get("grid", "#334155")),
        color_wall=_hex_to_rgb(colors_data.get("wall", "#64748b")),
        color_goal=_hex_to_rgb(colors_data.get("goal", "#facc15")),
        color_box=_hex_to_rgb(colors_data.get("box", "#f97316")),
        color_player=_hex_to_rgb(colors_data.get("player", "#22c55e")),
    )

    window = WindowConfig(
        title=str(window_data.get("title", "Sokoban Visualizer")),
        fps=int(window_data.get("fps", 60)),
    )

    search = SearchConfig(
        algorithm=_normalize_algorithm(search_data.get("algorithm", "bfs")),
        dfs_depth_limit=int(search_data.get("dfs_depth_limit", 10_000)),
        animation_step_seconds=float(search_data.get("animation_step_seconds", 0.2)),
    )

    return AppConfig(
        window=window,
        render=render,
        search=search,
        board=board,
        initial_state=initial_state,
    )


def _position_from_list(raw: Any) -> Position:
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError(f"Posicion invalida: {raw}")
    row, col = raw
    return Position(row=int(row), col=int(col))


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Color invalido: {hex_color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _validate_entities_inside_board(board: Board, state: State) -> None:
    if not board.contains(state.player):
        raise ValueError("El jugador esta fuera del tablero.")
    if state.player in board.walls:
        raise ValueError("El jugador no puede iniciar sobre una pared.")
    if state.player in state.boxes:
        raise ValueError("El jugador no puede iniciar sobre una caja.")

    for box in state.boxes:
        if not board.contains(box):
            raise ValueError(f"Caja fuera del tablero: {box}")
        if box in board.walls:
            raise ValueError(f"Caja sobre pared: {box}")

    if len(board.goals) != len(state.boxes):
        raise ValueError("La cantidad de metas debe coincidir con la cantidad de cajas.")


def _normalize_algorithm(raw: str) -> str:
    value = str(raw).strip().lower()
    if value not in {"bfs", "dfs"}:
        raise ValueError(f"Algoritmo invalido en config: {raw}")
    return value
