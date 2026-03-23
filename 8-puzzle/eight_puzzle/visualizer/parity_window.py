from __future__ import annotations

import arcade

from ..config import AppConfig
from ..models.state import CANONICAL_BOARD, State
from .window import EightPuzzleWindow


class ParityPuzzleWindow(EightPuzzleWindow):
    _KEY_TO_DELTA: dict[int, tuple[int, int]] = {
        arcade.key.UP: (1, 0),
        arcade.key.DOWN: (-1, 0),
        arcade.key.LEFT: (0, 1),
        arcade.key.RIGHT: (0, -1),
    }

    def __init__(self, config: AppConfig) -> None:
        self._initial_state = State(board=CANONICAL_BOARD)
        self._move_count = 0
        super().__init__(config=config, state=self._initial_state, overlay_lines=())
        self.set_overlay_lines(self._build_parity_overlay_lines())

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.R:
            self._reset()
            return

        delta = self._KEY_TO_DELTA.get(symbol)
        if delta is None:
            return

        next_state = self.state.move_blank(*delta)
        if next_state is None:
            return

        self._move_count += 1
        self.set_state(next_state)
        self.set_overlay_lines(self._build_parity_overlay_lines())

    def _reset(self) -> None:
        self._move_count = 0
        self.set_state(self._initial_state)
        self.set_overlay_lines(self._build_parity_overlay_lines())

    def _build_parity_overlay_lines(self) -> tuple[str, ...]:
        current_inversions = self.state.inversion_count()
        current_parity = self.state.inversion_parity()
        initial_parity = self._initial_state.inversion_parity()

        return (
            "Modo: control manual",
            "Flechas invertidas: mueven al reves",
            "R: reinicia al canonico",
            f"Aplanado: {self._format_flat_board(self.state.board)}",
            f"Inversiones (sin 0): {current_inversions}",
            f"Paridad actual: {self._parity_label(current_parity)}",
            f"Paridad inicial: {self._parity_label(initial_parity)}",
            f"Invariante: {'si' if current_parity == initial_parity else 'no'}",
        )

    def _progress_label(self) -> str:
        return f"Movimientos: {self._move_count}"

    def _progress_badge_bounds(self) -> tuple[float, float, float, float]:
        badge_width = min(200, self._panel_width() - 48)
        badge_height = 38
        left = self._panel_left() + self._panel_padding_x
        bottom = self._panel_bottom() + 20
        return left, bottom, badge_width, badge_height

    @staticmethod
    def _format_flat_board(board: tuple[int, ...]) -> str:
        return "[" + ",".join("_" if tile == 0 else str(tile) for tile in board) + "]"

    @staticmethod
    def _parity_label(parity: int) -> str:
        return "par" if parity == 0 else "impar"


def run_parity_visualizer(config: AppConfig) -> None:
    _window = ParityPuzzleWindow(config=config)
    arcade.run()
