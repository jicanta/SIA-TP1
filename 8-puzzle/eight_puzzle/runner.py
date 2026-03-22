from __future__ import annotations

from pathlib import Path

from .config import (
    AppConfig,
    DEFAULT_PUZZLE_NAME,
    list_puzzle_names,
    load_config,
    load_puzzle_config,
    resolve_puzzle_path,
)
from .search import (
    SearchResult,
    solve_astar_h1,
    solve_astar_h2,
    solve_bfs,
    solve_dfs,
    solve_dls,
    solve_greedy_h1,
    solve_greedy_h2,
    solve_iddfs,
)

SUPPORTED_ALGORITHMS = (
    "bfs",
    "dfs",
    "dls",
    "iddfs",
    "astar_h1",
    "astar_h2",
    "greedy_h1",
    "greedy_h2",
)


def load_requested_config(
    config_path: str | None = None,
    puzzle_name: str | None = None,
) -> tuple[AppConfig, str]:
    if config_path:
        path = Path(config_path)
        return load_config(path), path.stem

    selected_puzzle = puzzle_name or DEFAULT_PUZZLE_NAME
    puzzle_path = resolve_puzzle_path(selected_puzzle)
    return load_puzzle_config(puzzle_path), puzzle_path.stem


def print_available_puzzles() -> None:
    puzzle_names = list_puzzle_names()
    if not puzzle_names:
        print("No hay puzzles disponibles.")
        return

    print("puzzles disponibles:")
    for puzzle_name in puzzle_names:
        print(f"- {puzzle_name}")


def run_search(config: AppConfig, algorithm: str) -> SearchResult:
    algorithm_name = algorithm.strip().lower()
    initial_state = config.initial_state

    if algorithm_name == "bfs":
        return solve_bfs(initial_state)
    if algorithm_name == "dfs":
        return solve_dfs(initial_state, depth_limit=config.search.dfs_depth_limit)
    if algorithm_name == "dls":
        return solve_dls(initial_state, depth_limit=config.search.dfs_depth_limit)
    if algorithm_name == "iddfs":
        return solve_iddfs(initial_state, max_depth=config.search.dfs_depth_limit)
    if algorithm_name == "astar_h1":
        return solve_astar_h1(initial_state)
    if algorithm_name == "astar_h2":
        return solve_astar_h2(initial_state)
    if algorithm_name == "greedy_h1":
        return solve_greedy_h1(initial_state)
    if algorithm_name == "greedy_h2":
        return solve_greedy_h2(initial_state)

    raise ValueError(f"Algoritmo no soportado: {algorithm}")


def print_summary(result: SearchResult, puzzle_label: str) -> None:
    print(f"puzzle: {puzzle_label}")
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


def build_overlay_lines(result: SearchResult, puzzle_label: str) -> tuple[str, ...]:
    return (
        f"Puzzle: {puzzle_label}",
        f"Algoritmo: {result.algorithm.upper()}",
        "Objetivo: preservar vecinos canonicos",
        f"Encontrada: {'si' if result.found else 'no'}",
        f"Movimientos: {len(result.actions)}",
        f"Expandidos: {result.expanded_nodes}",
        f"Generados: {result.generated_nodes}",
        f"Visitados: {result.visited_nodes}",
    )


def build_initial_overlay_lines(config: AppConfig, puzzle_label: str) -> tuple[str, ...]:
    return (
        f"Puzzle: {puzzle_label}",
        "Modo: estado inicial",
        f"Algoritmo configurado: {config.search.algorithm.upper()}",
        "Objetivo: preservar vecinos canonicos",
        "Usa run_eight_puzzle.py para buscar y animar la solucion.",
    )
