from __future__ import annotations

from pathlib import Path

from sokoban.config import load_config


def main() -> None:
    try:
        from sokoban.visualizer import run_visualizer
    except ModuleNotFoundError as exc:
        if exc.name == "arcade":
            raise SystemExit("Falta la dependencia 'arcade'. Instala con: pip install arcade") from exc
        raise

    config_path = Path(__file__).with_name("config.json")
    config = load_config(config_path)
    run_visualizer(config)


if __name__ == "__main__":
    main()
