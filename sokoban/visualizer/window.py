from __future__ import annotations

from collections.abc import Sequence

import arcade

from ..config import AppConfig
from ..models.position import Position
from ..models.state import State


class SokobanWindow(arcade.Window):

    def __init__(
        self,
        config: AppConfig,
        state: State | None = None,
        state_sequence: Sequence[State] | None = None,
        overlay_lines: Sequence[str] | None = None,
        step_seconds: float | None = None,
    ) -> None:
        self.app_config = config
        self.board = config.board
        self.render = config.render
        self.overlay_lines = tuple(overlay_lines or ())
        self.step_seconds = max(0.01, step_seconds or config.search.animation_step_seconds)
        self._elapsed_time = 0.0

        if state_sequence:
            self.state_sequence = tuple(state_sequence)
        else:
            self.state_sequence = (state or config.initial_state,)

        self.sequence_index = 0
        self.state = self.state_sequence[self.sequence_index]

        super().__init__(
            width=config.window_width,
            height=config.window_height,
            title=config.window.title,
            update_rate=1 / max(1, config.window.fps),
        )

        arcade.set_background_color(self.render.color_background)

    def on_draw(self) -> None:
        self.clear()
        self._draw_floor()
        if self.render.draw_grid:
            self._draw_grid_lines()
        self._draw_walls()
        self._draw_goals()
        self._draw_boxes()
        self._draw_player()
        self._draw_overlay()

    def on_update(self, delta_time: float) -> None:
        if len(self.state_sequence) <= 1:
            return
        if self.sequence_index >= len(self.state_sequence) - 1:
            return

        self._elapsed_time += delta_time
        if self._elapsed_time < self.step_seconds:
            return

        self._elapsed_time = 0.0
        self.sequence_index += 1
        self.state = self.state_sequence[self.sequence_index]

    def _draw_floor(self) -> None:
        width = self.board.cols * self.render.cell_size
        height = self.board.rows * self.render.cell_size
        arcade.draw_lbwh_rectangle_filled(
            self.render.margin,
            self.render.margin,
            width,
            height,
            self.render.color_floor,
        )

    def _draw_grid_lines(self) -> None:
        cs = self.render.cell_size
        left = self.render.margin
        bottom = self.render.margin
        right = left + self.board.cols * cs
        top = bottom + self.board.rows * cs

        for col in range(self.board.cols + 1):
            x = left + col * cs
            arcade.draw_line(x, bottom, x, top, self.render.color_grid, 1)

        for row in range(self.board.rows + 1):
            y = bottom + row * cs
            arcade.draw_line(left, y, right, y, self.render.color_grid, 1)

    def _draw_walls(self) -> None:
        for wall in self.board.walls:
            x, y = self._cell_center(wall)
            size = self.render.cell_size
            self._draw_square_centered(x, y, size, self.render.color_wall)

    def _draw_goals(self) -> None:
        radius = self.render.cell_size * 0.23
        for goal in self.state.goals:
            x, y = self._cell_center(goal)
            arcade.draw_circle_filled(x, y, radius, self.render.color_goal)

    def _draw_boxes(self) -> None:
        size = self.render.cell_size * 0.72
        for box in self.state.boxes:
            x, y = self._cell_center(box)
            self._draw_square_centered(x, y, size, self.render.color_box)

    def _draw_player(self) -> None:
        x, y = self._cell_center(self.state.player)
        radius = self.render.cell_size * 0.3
        arcade.draw_circle_filled(x, y, radius, self.render.color_player)

    def _cell_center(self, pos: Position) -> tuple[float, float]:
        cs = self.render.cell_size
        x = self.render.margin + pos.col * cs + cs / 2
        y = self.render.margin + (self.board.rows - 1 - pos.row) * cs + cs / 2
        return x, y

    @staticmethod
    def _draw_square_centered(
        center_x: float,
        center_y: float,
        size: float,
        color: tuple[int, int, int],
    ) -> None:
        arcade.draw_lbwh_rectangle_filled(
            center_x - size / 2,
            center_y - size / 2,
            size,
            size,
            color,
        )

    def _draw_overlay(self) -> None:
        top = self.height - 28
        color = (230, 230, 230)

        progress = f"Paso: {self.sequence_index}/{max(0, len(self.state_sequence) - 1)}"
        arcade.draw_text(progress, 14, top, color, 14)

        y = top - 20
        for line in self.overlay_lines:
            arcade.draw_text(line, 14, y, color, 13)
            y -= 18


def run_visualizer(
    config: AppConfig,
    state: State | None = None,
    state_sequence: Sequence[State] | None = None,
    overlay_lines: Sequence[str] | None = None,
    step_seconds: float | None = None,
) -> None:
    _window = SokobanWindow(
        config=config,
        state=state,
        state_sequence=state_sequence,
        overlay_lines=overlay_lines,
        step_seconds=step_seconds,
    )
    arcade.run()
