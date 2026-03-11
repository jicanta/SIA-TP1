from __future__ import annotations

import argparse
from pathlib import Path

from sokoban.config import AppConfig, load_config
from sokoban.search import SearchResult, solve_bfs, solve_dfs


def main() -> None:
    args = _parse_args()
    config_path = Path(__file__).with_name("config.json")
    config = load_config(config_path)

    algorithm = args.algorithm or config.search.algorithm
    result = _run_search(config, algorithm)

    _print_summary(result)

    if args.no_visualizer:
        return

    try:
        from sokoban.visualizer import run_visualizer
    except ModuleNotFoundError as exc:
        if exc.name == "arcade":
            raise SystemExit("Falta la dependencia 'arcade'. Instala con: pip install arcade") from exc
        raise

    overlay = (
        f"Algoritmo: {result.algorithm.upper()}",
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
    parser = argparse.ArgumentParser(description="Busqueda desinformada para Sokoban.")
    parser.add_argument(
        "--algorithm",
        choices=["bfs", "dfs"],
        help="Algoritmo a usar. Si se omite, se usa el de config.json",
    )
    parser.add_argument(
        "--no-visualizer",
        action="store_true",
        help="Ejecuta la busqueda y muestra resultados por consola sin abrir ventana.",
    )
    return parser.parse_args()


def _run_search(config: AppConfig, algorithm: str) -> SearchResult:
    algorithm_name = algorithm.strip().lower()

    if algorithm_name == "bfs":
        return solve_bfs(config.initial_state, config.board)
    if algorithm_name == "dfs":
        return solve_dfs(
            config.initial_state,
            config.board,
            depth_limit=config.search.dfs_depth_limit,
        )
    raise ValueError(f"Algoritmo no soportado: {algorithm}")


def _print_summary(result: SearchResult) -> None:
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
