from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from eight_puzzle.config import AppConfig, DEFAULT_PUZZLE_NAME, load_puzzle_config
from eight_puzzle.models.state import CANONICAL_BOARD, State

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eight_puzzle.runner import (
    SUPPORTED_ALGORITHMS,
    build_initial_overlay_lines,
    build_overlay_lines,
    load_requested_config,
    print_available_puzzles,
    print_summary,
    run_search,
)


def main() -> None:
    args = _parse_args()
    if args.list_puzzles and not args.parity_demo:
        print_available_puzzles()
        return
    _maybe_restart_for_visualizer()

    try:
        from eight_puzzle.visualizer import run_parity_visualizer, run_visualizer
    except ModuleNotFoundError as exc:
        if exc.name == "arcade":
            raise SystemExit("Falta la dependencia 'arcade'. Instala con: pip install arcade") from exc
        raise

    if args.parity_demo:
        run_parity_visualizer(_build_parity_config())
        return

    config, puzzle_label = load_requested_config(args.config, args.puzzle)

    if args.initial_only:
        run_visualizer(
            config=config,
            overlay_lines=build_initial_overlay_lines(config, puzzle_label),
        )
        return

    algorithm = args.algorithm or config.search.algorithm
    result = run_search(config, algorithm)
    print_summary(result, puzzle_label)
    run_visualizer(
        config=config,
        state_sequence=result.path_states,
        overlay_lines=build_overlay_lines(result, puzzle_label),
        step_seconds=config.search.animation_step_seconds,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Busca y visualiza soluciones para el 8-puzzle.")
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--config",
        type=str,
        help="Ruta a un archivo JSON de configuracion completo.",
    )
    source_group.add_argument(
        "--puzzle",
        type=str,
        help="Nombre del puzzle a cargar desde 8-puzzle/eight_puzzle/puzzles (ej: puzzle_03_short).",
    )
    parser.add_argument(
        "--list-puzzles",
        action="store_true",
        help="Lista los puzzles disponibles y termina.",
    )
    parser.add_argument(
        "--algorithm",
        choices=SUPPORTED_ALGORITHMS,
        help="Algoritmo a usar. Si se omite, se usa el configurado en el JSON.",
    )
    parser.add_argument(
        "--initial-only",
        action="store_true",
        help="Abre solo el tablero inicial sin ejecutar busqueda.",
    )
    parser.add_argument(
        "--parity-demo",
        action="store_true",
        help="Abre un visualizador manual para explorar la paridad de inversiones desde el tablero canonico.",
    )
    return parser.parse_args()


def _build_parity_config() -> AppConfig:
    base_config = load_puzzle_config(DEFAULT_PUZZLE_NAME)
    return replace(
        base_config,
        window=replace(base_config.window, title="8 Puzzle - Paridad de Inversiones"),
        render=replace(base_config.render, panel_width=max(base_config.render.panel_width, 430)),
        initial_state=State(board=CANONICAL_BOARD),
    )


def _maybe_restart_for_visualizer() -> None:
    if importlib.util.find_spec("arcade") is not None:
        return
    if os.environ.get("EIGHT_PUZZLE_REEXEC") == "1":
        return

    alternate_python = _find_python_with_arcade()
    if alternate_python is None:
        return

    env = os.environ.copy()
    env["EIGHT_PUZZLE_REEXEC"] = "1"
    print(f"Usando {alternate_python.parent.parent.name} para abrir el visualizador.")
    completed = subprocess.run(
        [str(alternate_python), str(Path(__file__).resolve()), *sys.argv[1:]],
        env=env,
        cwd=PROJECT_ROOT,
    )
    raise SystemExit(completed.returncode)


def _find_python_with_arcade() -> Path | None:
    candidates = (
        PROJECT_ROOT / ".venv-win" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
    )
    current_python = Path(sys.executable).resolve()

    for candidate in candidates:
        if not candidate.exists():
            continue
        if candidate.resolve() == current_python:
            continue
        if _python_has_arcade(candidate):
            return candidate
    return None


def _python_has_arcade(python_path: Path) -> bool:
    result = subprocess.run(
        [str(python_path), "-c", "import arcade"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


if __name__ == "__main__":
    main()
