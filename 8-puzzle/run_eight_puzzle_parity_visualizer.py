from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    target = Path(__file__).resolve().parent / "run_eight_puzzle_visualizer.py"
    target_dir = str(target.parent)
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
    original_argv = sys.argv[:]
    sys.argv = [str(target), "--parity-demo", *sys.argv[1:]]
    try:
        runpy.run_path(str(target), run_name="__main__")
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
