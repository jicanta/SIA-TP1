from __future__ import annotations

import argparse
from pathlib import Path

from eight_puzzle.config import (
    DEFAULT_PUZZLE_NAME,
    list_puzzle_names,
    load_config,
    load_puzzle_config,
    resolve_puzzle_path,
)


def main() -> None:
    args = _parse_args()
    if args.list_puzzles:
        _print_available_puzzles()
        return

    try:
        from eight_puzzle.visualizer import run_visualizer
    except ModuleNotFoundError as exc:
        if exc.name == "arcade":
            raise SystemExit("Falta la dependencia 'arcade'. Instala con: pip install arcade") from exc
        raise

    if args.config:
        config = load_config(Path(args.config))
    else:
        puzzle_name = args.puzzle or DEFAULT_PUZZLE_NAME
        config = load_puzzle_config(resolve_puzzle_path(puzzle_name))
    run_visualizer(config)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualizador del estado inicial para el 8-puzzle.")
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
    return parser.parse_args()


def _print_available_puzzles() -> None:
    puzzle_names = list_puzzle_names()
    if not puzzle_names:
        print("No hay puzzles disponibles.")
        return

    print("puzzles disponibles:")
    for puzzle_name in puzzle_names:
        print(f"- {puzzle_name}")


if __name__ == "__main__":
    main()
