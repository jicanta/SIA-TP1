from __future__ import annotations

import argparse
from pathlib import Path

from sokoban.config import AppConfig, load_config
from sokoban.search import (
    SearchResult,
    solve_bfs,
    solve_dfs,
    solve_dls,
    solve_iddfs,
    solve_astar_h1,
    solve_astar_h1_player,
    solve_astar_h2,
    solve_astar_h2_player,
    solve_astar_h2_deadlock,
    solve_greedy_h1,
    solve_greedy_h1_player,
    solve_greedy_h2,
    solve_greedy_h2_player,
    solve_greedy_h2_deadlock,
    solve_astar_h2_player_deadlock,
    solve_greedy_h2_player_deadlock,
)


def main() -> None:
    args = _parse_args()
    app_dir = Path(__file__).parent
    
    if args.level:
        level_name = args.level if args.level.endswith(".json") else f"{args.level}.json"
        config_path = app_dir / "levels" / level_name
        if not config_path.exists():
            config_path = app_dir / level_name
    else:
        config_path = app_dir / "config.json"
        
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
        "--level",
        type=str,
        help="Nombre del nivel a cargar desde la carpeta 'levels' (ej: 'nivel_1' o 'nivel_1.json').",
    )
    parser.add_argument(
        "--algorithm",
        choices=[
            "bfs", "dfs", "dls", "iddfs",
            "astar_h1", "astar_h1_player", "astar_h2", "astar_h2_player",
            "astar_h2_deadlock", "astar_h2_player_deadlock",
            "greedy_h1", "greedy_h1_player", "greedy_h2", "greedy_h2_player",
            "greedy_h2_deadlock", "greedy_h2_player_deadlock",
        ],
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
        return solve_astar_h1(
            config.initial_state,
            config.board
        )
    if algorithm_name == "astar_h1_player":
        return solve_astar_h1_player(
            config.initial_state,
            config.board
        )
    if algorithm_name == "astar_h2":
        return solve_astar_h2(
            config.initial_state,
            config.board
        )
    if algorithm_name == "astar_h2_player":
        return solve_astar_h2_player(
            config.initial_state,
            config.board
        )
    if algorithm_name == "astar_h2_deadlock":
        return solve_astar_h2_deadlock(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h1":
        return solve_greedy_h1(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h1_player":
        return solve_greedy_h1_player(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h2":
        return solve_greedy_h2(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h2_player":
        return solve_greedy_h2_player(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h2_deadlock":
        return solve_greedy_h2_deadlock(
            config.initial_state,
            config.board
        )
    if algorithm_name == "astar_h2_player_deadlock":
        return solve_astar_h2_player_deadlock(
            config.initial_state,
            config.board
        )
    if algorithm_name == "greedy_h2_player_deadlock":
        return solve_greedy_h2_player_deadlock(
            config.initial_state,
            config.board
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
