from __future__ import annotations

import argparse
from pathlib import Path

from eight_puzzle.config import (
    AppConfig,
    DEFAULT_PUZZLE_NAME,
    list_puzzle_names,
    load_config,
    load_puzzle_config,
    resolve_puzzle_path,
)
from eight_puzzle.search import (
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


def main() -> None:
    args = _parse_args()
    if args.list_puzzles:
        _print_available_puzzles()
        return

    config, puzzle_label = _load_requested_config(args)

    algorithm = args.algorithm or config.search.algorithm
    result = _run_search(config, algorithm)

    _print_summary(result, puzzle_label)

    if args.no_visualizer:
        return

    try:
        from eight_puzzle.visualizer import run_visualizer
    except ModuleNotFoundError as exc:
        if exc.name == "arcade":
            raise SystemExit("Falta la dependencia 'arcade'. Instala con: pip install arcade") from exc
        raise

    overlay = (
        f"Puzzle: {puzzle_label}",
        f"Algoritmo: {result.algorithm.upper()}",
        "Objetivo: preservar vecinos canonicos",
        f"Encontrada: {'si' if result.found else 'no'}",
        f"Movimientos: {len(result.actions)}",
        f"Expandidos: {result.expanded_nodes}",
        f"Generados: {result.generated_nodes}",
        f"Visitados: {result.visited_nodes}",
    )

    run_visualizer(
        config=config,
        state_sequence=result.path_states,
        overlay_lines=overlay,
        step_seconds=config.search.animation_step_seconds,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Busqueda y visualizacion para el 8-puzzle.")
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--config",
        type=str,
        help="Ruta a un archivo JSON de configuracion completo.",
    )
    source_group.add_argument(
        "--puzzle",
        type=str,
        help="Nombre del puzzle a cargar desde eight_puzzle/puzzles (ej: puzzle_03_short).",
    )
    parser.add_argument(
        "--list-puzzles",
        action="store_true",
        help="Lista los puzzles disponibles y termina.",
    )
    parser.add_argument(
        "--algorithm",
        choices=[
            "bfs",
            "dfs",
            "dls",
            "iddfs",
            "astar_h1",
            "astar_h2",
            "greedy_h1",
            "greedy_h2",
        ],
        help="Algoritmo a usar. Si se omite, se usa el configurado en el JSON.",
    )
    parser.add_argument(
        "--no-visualizer",
        action="store_true",
        help="Ejecuta la busqueda y muestra resultados por consola sin abrir ventana.",
    )
    return parser.parse_args()


def _load_requested_config(args: argparse.Namespace) -> tuple[AppConfig, str]:
    if args.config:
        config_path = Path(args.config)
        return load_config(config_path), config_path.stem

    puzzle_name = args.puzzle or DEFAULT_PUZZLE_NAME
    puzzle_path = resolve_puzzle_path(puzzle_name)
    return load_puzzle_config(puzzle_path), puzzle_path.stem


def _print_available_puzzles() -> None:
    puzzle_names = list_puzzle_names()
    if not puzzle_names:
        print("No hay puzzles disponibles.")
        return

    print("puzzles disponibles:")
    for puzzle_name in puzzle_names:
        print(f"- {puzzle_name}")


def _run_search(config: AppConfig, algorithm: str) -> SearchResult:
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


def _print_summary(result: SearchResult, puzzle_label: str) -> None:
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


if __name__ == "__main__":
    main()
