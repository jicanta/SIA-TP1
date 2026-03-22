from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models.state import State

PACKAGE_DIR = Path(__file__).resolve().parent
CONFIGS_DIR = PACKAGE_DIR / "configs"
PUZZLES_DIR = PACKAGE_DIR / "puzzles"
DEFAULT_CONFIG_PATH = CONFIGS_DIR / "default.json"
DEFAULT_PUZZLE_NAME = "puzzle_01_intro"


@dataclass(frozen=True, slots=True)
class RenderConfig:
    cell_size: int
    margin: int
    panel_width: int
    panel_gap: int
    draw_grid: bool
    font_name: str
    color_background: tuple[int, int, int]
    color_panel: tuple[int, int, int]
    color_panel_border: tuple[int, int, int]
    color_board: tuple[int, int, int]
    color_blank: tuple[int, int, int]
    color_blank_text: tuple[int, int, int]
    color_grid: tuple[int, int, int]
    color_shadow: tuple[int, int, int]
    color_tile: tuple[int, int, int]
    color_tile_goal: tuple[int, int, int]
    color_tile_text: tuple[int, int, int]
    color_overlay_text: tuple[int, int, int]
    color_title: tuple[int, int, int]


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
    initial_state: State

    @property
    def window_width(self) -> int:
        return self.render.margin * 2 + self.render.cell_size * 3 + self.render.panel_gap + self.render.panel_width

    @property
    def window_height(self) -> int:
        return self.render.margin * 2 + self.render.cell_size * 3


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    return _build_app_config(_load_json(config_path))


def load_puzzle_config(
    puzzle: str | Path,
    defaults_path: str | Path = DEFAULT_CONFIG_PATH,
) -> AppConfig:
    base_data = _load_json(Path(defaults_path))
    puzzle_path = resolve_puzzle_path(puzzle)
    puzzle_data = _load_json(puzzle_path)
    merged_data = _deep_merge(base_data, puzzle_data)
    return _build_app_config(merged_data)


def resolve_puzzle_path(puzzle: str | Path) -> Path:
    puzzle_path = Path(puzzle)
    if puzzle_path.exists():
        return puzzle_path

    if puzzle_path.suffix:
        candidate = PUZZLES_DIR / puzzle_path.name
    else:
        candidate = PUZZLES_DIR / f"{puzzle_path.name}.json"

    if candidate.exists():
        return candidate

    raise FileNotFoundError(f"No se encontro el puzzle '{puzzle}'.")


def list_puzzle_names() -> tuple[str, ...]:
    if not PUZZLES_DIR.exists():
        return tuple()
    return tuple(sorted(path.stem for path in PUZZLES_DIR.glob("*.json")))


def _build_app_config(data: dict[str, Any]) -> AppConfig:

    window_data = data.get("window", {})
    search_data = data.get("search", {})
    render_data = data.get("render", {})
    colors_data = render_data.get("colors", {})
    state_data = data.get("state", {})

    initial_state = _load_state(state_data)

    render = RenderConfig(
        cell_size=int(render_data.get("cell_size", 160)),
        margin=int(render_data.get("margin", 32)),
        panel_width=int(render_data.get("panel_width", 360)),
        panel_gap=int(render_data.get("panel_gap", 28)),
        draw_grid=bool(render_data.get("draw_grid", True)),
        font_name=str(render_data.get("font_name", "Trebuchet MS")),
        color_background=_hex_to_rgb(colors_data.get("background", "#0b1218")),
        color_panel=_hex_to_rgb(colors_data.get("panel", "#12202c")),
        color_panel_border=_hex_to_rgb(colors_data.get("panel_border", "#315170")),
        color_board=_hex_to_rgb(colors_data.get("board", "#172431")),
        color_blank=_hex_to_rgb(colors_data.get("blank", "#233548")),
        color_blank_text=_hex_to_rgb(colors_data.get("blank_text", "#8ec5ff")),
        color_grid=_hex_to_rgb(colors_data.get("grid", "#476580")),
        color_shadow=_hex_to_rgb(colors_data.get("shadow", "#071018")),
        color_tile=_hex_to_rgb(colors_data.get("tile", "#f3b95f")),
        color_tile_goal=_hex_to_rgb(colors_data.get("tile_goal", "#73c996")),
        color_tile_text=_hex_to_rgb(colors_data.get("tile_text", "#17202a")),
        color_overlay_text=_hex_to_rgb(colors_data.get("overlay_text", "#d9e4ef")),
        color_title=_hex_to_rgb(colors_data.get("title", "#f6ead5")),
    )

    window = WindowConfig(
        title=str(window_data.get("title", "8 Puzzle Visualizer")),
        fps=int(window_data.get("fps", 60)),
    )

    search = SearchConfig(
        algorithm=_normalize_algorithm(search_data.get("algorithm", "astar_h2")),
        dfs_depth_limit=int(search_data.get("dfs_depth_limit", 40)),
        animation_step_seconds=float(search_data.get("animation_step_seconds", 0.45)),
    )

    return AppConfig(
        window=window,
        render=render,
        search=search,
        initial_state=initial_state,
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    if not isinstance(loaded, dict):
        raise ValueError(f"El archivo de configuracion debe contener un objeto JSON: {path}")
    return loaded


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(base_value, value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _load_state(state_data: dict[str, Any]) -> State:
    if "positions" in state_data:
        return State.from_positions(state_data["positions"])
    if "board" in state_data:
        return State.from_board(state_data["board"])
    raise ValueError("La configuracion del 8-puzzle debe incluir 'state.positions' o 'state.board'.")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Color invalido: {hex_color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _normalize_algorithm(raw: str) -> str:
    value = str(raw).strip().lower()
    supported = {
        "bfs",
        "dfs",
        "dls",
        "iddfs",
        "astar_h1",
        "astar_h2",
        "greedy_h1",
        "greedy_h2",
    }
    if value not in supported:
        raise ValueError(f"Algoritmo invalido en config: {raw}")
    return value
