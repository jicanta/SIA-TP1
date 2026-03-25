from __future__ import annotations

from pathlib import Path

from .config import AppConfig, load_config
from .search import (
    SearchResult,
    solve_astar_h1,
    solve_astar_h1_player,
    solve_astar_h2,
    solve_astar_h2_deadlock,
    solve_astar_h2_player,
    solve_astar_h2_player_deadlock,
    solve_bfs,
    solve_dfs,
    solve_dls,
    solve_greedy_h1,
    solve_greedy_h1_player,
    solve_greedy_h2,
    solve_greedy_h2_deadlock,
    solve_greedy_h2_player,
    solve_greedy_h2_player_deadlock,
    solve_iddfs,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEVELS_DIR = PROJECT_ROOT / "levels"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"

SUPPORTED_ALGORITHMS = (
    "bfs",
    "dfs",
    "dls",
    "iddfs",
    "astar_h1",
    "astar_h1_player",
    "astar_h2",
    "astar_h2_player",
    "astar_h2_deadlock",
    "astar_h2_player_deadlock",
    "greedy_h1",
    "greedy_h1_player",
    "greedy_h2",
    "greedy_h2_player",
    "greedy_h2_deadlock",
    "greedy_h2_player_deadlock",
)


def load_requested_config(level: str | None = None) -> tuple[AppConfig, str]:
    if level:
        level_name = level if level.endswith(".json") else f"{level}.json"
        config_path = LEVELS_DIR / level_name
        if not config_path.exists():
            config_path = PROJECT_ROOT / level_name
    else:
        config_path = DEFAULT_CONFIG_PATH

    return load_config(config_path), config_path.stem


def run_search(config: AppConfig, algorithm: str) -> SearchResult:
    algorithm_name = algorithm.strip().lower()

    if algorithm_name == "bfs":
        return solve_bfs(config.initial_state, config.board)
    if algorithm_name == "dfs":
        return solve_dfs(
            config.initial_state,
            config.board,
            depth_limit=config.search.dfs_depth_limit,
        )
    if algorithm_name == "dls":
        return solve_dls(
            config.initial_state,
            config.board,
            depth_limit=config.search.dfs_depth_limit,
        )
    if algorithm_name == "iddfs":
        return solve_iddfs(
            config.initial_state,
            config.board,
            max_depth=config.search.dfs_depth_limit,
        )
    if algorithm_name == "astar_h1":
        return solve_astar_h1(config.initial_state, config.board)
    if algorithm_name == "astar_h1_player":
        return solve_astar_h1_player(config.initial_state, config.board)
    if algorithm_name == "astar_h2":
        return solve_astar_h2(config.initial_state, config.board)
    if algorithm_name == "astar_h2_player":
        return solve_astar_h2_player(config.initial_state, config.board)
    if algorithm_name == "astar_h2_deadlock":
        return solve_astar_h2_deadlock(config.initial_state, config.board)
    if algorithm_name == "greedy_h1":
        return solve_greedy_h1(config.initial_state, config.board)
    if algorithm_name == "greedy_h1_player":
        return solve_greedy_h1_player(config.initial_state, config.board)
    if algorithm_name == "greedy_h2":
        return solve_greedy_h2(config.initial_state, config.board)
    if algorithm_name == "greedy_h2_player":
        return solve_greedy_h2_player(config.initial_state, config.board)
    if algorithm_name == "greedy_h2_deadlock":
        return solve_greedy_h2_deadlock(config.initial_state, config.board)
    if algorithm_name == "astar_h2_player_deadlock":
        return solve_astar_h2_player_deadlock(config.initial_state, config.board)
    if algorithm_name == "greedy_h2_player_deadlock":
        return solve_greedy_h2_player_deadlock(config.initial_state, config.board)

    raise ValueError(f"Algoritmo no soportado: {algorithm}")


def print_summary(result: SearchResult, label: str | None = None) -> None:
    if label:
        print(f"nivel: {label}")
    print(f"algoritmo: {result.algorithm}")
    print(f"encontrada: {'si' if result.found else 'no'}")
    print(f"movimientos: {len(result.actions)}")
    if len(result.actions) <= 120:
        print(f"acciones: {' '.join(result.actions)}")
    else:
        preview = " ".join(result.actions[:120])
        print(f"acciones (primeras 120): {preview} ...")
    print(f"expandidos: {result.expanded_nodes}")
    print(f"generados: {result.generated_nodes}")
    print(f"visitados: {result.visited_nodes}")
    print(f"frontera: {result.frontier_nodes}")
    print(f"frontera_max: {result.max_frontier_nodes}")


def build_overlay_lines(result: SearchResult, label: str) -> tuple[str, ...]:
    return (
        f"Nivel: {label}",
        f"Algoritmo: {result.algorithm.upper()}",
        f"Encontrada: {'si' if result.found else 'no'}",
        f"Movimientos: {len(result.actions)}",
        f"Expandidos: {result.expanded_nodes}",
        f"Generados: {result.generated_nodes}",
        f"Visitados: {result.visited_nodes}",
        f"Frontera: {result.frontier_nodes}",
        f"Frontera max: {result.max_frontier_nodes}",
    )


def build_initial_overlay_lines(config: AppConfig, label: str) -> tuple[str, ...]:
    return (
        f"Nivel: {label}",
        "Modo: estado inicial",
        f"Algoritmo configurado: {config.search.algorithm.upper()}",
        "Usa run_visualizer.py sin --initial-only para animar la solucion.",
    )
