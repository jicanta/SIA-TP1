from __future__ import annotations

from collections.abc import Sequence

import arcade
from arcade import shape_list

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
        self._static_shapes = self._build_static_shapes()
        self._progress_text, self._overlay_texts = self._build_overlay_texts()

    def on_draw(self) -> None:
        self.clear()
        self._static_shapes.draw()
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
        self._progress_text.text = self._progress_label()

    def _build_static_shapes(self) -> shape_list.ShapeElementList:
        shapes = shape_list.ShapeElementList()
        shapes.append(self._build_floor_shape())
        if self.render.draw_grid:
            for line in self._build_grid_shapes():
                shapes.append(line)
        for wall in self._build_wall_shapes():
            shapes.append(wall)
        for goal in self._build_goal_shapes():
            shapes.append(goal)
        return shapes

    def _build_floor_shape(self) -> shape_list.Shape:
        width = self.board.cols * self.render.cell_size
        height = self.board.rows * self.render.cell_size
        center_x = self.render.margin + width / 2
        center_y = self.render.margin + height / 2
        return shape_list.create_rectangle_filled(
            center_x,
            center_y,
            width,
            height,
            self._to_rgba(self.render.color_floor),
        )

    def _build_grid_shapes(self) -> list[shape_list.Shape]:
        lines: list[shape_list.Shape] = []
        cs = self.render.cell_size
        left = self.render.margin
        bottom = self.render.margin
        right = left + self.board.cols * cs
        top = bottom + self.board.rows * cs

        for col in range(self.board.cols + 1):
            x = left + col * cs
            lines.append(shape_list.create_line(x, bottom, x, top, self._to_rgba(self.render.color_grid), 1))

        for row in range(self.board.rows + 1):
            y = bottom + row * cs
            lines.append(shape_list.create_line(left, y, right, y, self._to_rgba(self.render.color_grid), 1))
        return lines

    def _build_wall_shapes(self) -> list[shape_list.Shape]:
        wall_shapes: list[shape_list.Shape] = []
        size = self.render.cell_size
        for wall in self.board.walls:
            x, y = self._cell_center(wall)
            wall_shapes.append(shape_list.create_rectangle_filled(x, y, size, size, self._to_rgba(self.render.color_wall)))
        return wall_shapes

    def _build_goal_shapes(self) -> list[shape_list.Shape]:
        goal_shapes: list[shape_list.Shape] = []
        radius = self.render.cell_size * 0.23
        for goal in self.board.goals:
            x, y = self._cell_center(goal)
            goal_shapes.append(
                shape_list.create_ellipse_filled(
                    x,
                    y,
                    radius * 2,
                    radius * 2,
                    self._to_rgba(self.render.color_goal),
                )
            )
        return goal_shapes

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

    def _build_overlay_texts(self) -> tuple[arcade.Text, tuple[arcade.Text, ...]]:
        top = self.height - 28
        color = (230, 230, 230)

        progress_text = arcade.Text(self._progress_label(), 14, top, color, 14)
        static_lines: list[arcade.Text] = []
        y = top - 20
        for line in self.overlay_lines:
            static_lines.append(arcade.Text(line, 14, y, color, 13))
            y -= 18

        return progress_text, tuple(static_lines)

    def _progress_label(self) -> str:
        total_steps = max(0, len(self.state_sequence) - 1)
        if total_steps == 0:
            return "Paso: sin animacion"
        if self.sequence_index == 0:
            return f"Paso: inicio/{total_steps}"
        return f"Paso: {self.sequence_index}/{total_steps}"

    def _draw_overlay(self) -> None:
        self._progress_text.draw()
        for text_line in self._overlay_texts:
            text_line.draw()

    @staticmethod
    def _to_rgba(color: tuple[int, int, int]) -> tuple[int, int, int, int]:
        return color[0], color[1], color[2], 255


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
