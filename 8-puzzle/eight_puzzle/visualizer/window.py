from __future__ import annotations

from collections.abc import Sequence

import arcade
from arcade import shape_list

from ..config import AppConfig
from ..models.state import BOARD_SIZE, State


class EightPuzzleWindow(arcade.Window):

    def __init__(
        self,
        config: AppConfig,
        state: State | None = None,
        state_sequence: Sequence[State] | None = None,
        overlay_lines: Sequence[str] | None = None,
        step_seconds: float | None = None,
    ) -> None:
        self.app_config = config
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

        self._board_size = BOARD_SIZE * self.render.cell_size
        self._window_width = config.window_width
        self._window_height = config.window_height
        self._panel_padding_x = 24
        self._panel_padding_y = 24
        self._line_spacing = 24

        super().__init__(
            width=self._window_width,
            height=self._window_height,
            title=config.window.title,
            update_rate=1 / max(1, config.window.fps),
        )

        arcade.set_background_color(self.render.color_background)
        self._static_shapes = self._build_static_shapes()
        self._title_text = self._build_title_text()
        self._overlay_texts = self._build_overlay_texts()
        self._progress_text = self._build_progress_text()
        self._blank_text = self._build_blank_text()
        self._tile_shadow_texts = self._build_tile_texts(
            color=self._with_alpha(self.render.color_shadow, 170),
            offset_x=2,
            offset_y=-3,
        )
        self._tile_texts = self._build_tile_texts(
            color=self.render.color_tile_text,
            offset_x=0,
            offset_y=0,
        )
        self._sync_dynamic_texts()

    def on_draw(self) -> None:
        self.clear()
        self._static_shapes.draw()
        self._draw_blank()
        self._draw_tiles()
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
        self._sync_dynamic_texts()

    def _build_static_shapes(self) -> shape_list.ShapeElementList:
        shapes = shape_list.ShapeElementList()
        for glow in self._build_background_shapes():
            shapes.append(glow)
        for panel_shape in self._build_panel_shapes():
            shapes.append(panel_shape)
        for board_shape in self._build_board_shapes():
            shapes.append(board_shape)
        if self.render.draw_grid:
            for line in self._build_grid_shapes():
                shapes.append(line)
        return shapes

    def _build_background_shapes(self) -> list[shape_list.Shape]:
        return [
            shape_list.create_ellipse_filled(
                self.width * 0.84,
                self.height * 0.8,
                self.width * 0.5,
                self.height * 0.5,
                self._with_alpha(self.render.color_title, 18),
            ),
            shape_list.create_ellipse_filled(
                self.width * 0.18,
                self.height * 0.2,
                self.width * 0.42,
                self.height * 0.32,
                self._with_alpha(self.render.color_tile_goal, 22),
            ),
        ]

    def _build_panel_shapes(self) -> list[shape_list.Shape]:
        center_x = self._panel_left() + self._panel_width() / 2
        center_y = self._panel_bottom() + self._panel_height() / 2
        width = self._panel_width()
        height = self._panel_height()

        return [
            shape_list.create_rectangle_filled(
                center_x + 8,
                center_y - 10,
                width,
                height,
                self._with_alpha(self.render.color_shadow, 120),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                center_y,
                width,
                height,
                self._to_rgba(self.render.color_panel_border),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                center_y,
                width - 6,
                height - 6,
                self._to_rgba(self.render.color_panel),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                self._panel_top() - 10,
                width - 20,
                6,
                self._with_alpha(self.render.color_title, 90),
            ),
        ]

    def _build_board_shapes(self) -> list[shape_list.Shape]:
        outer_size = self._board_size + self.render.cell_size * 0.18
        inner_size = self._board_size + self.render.cell_size * 0.06
        center_x = self._board_left() + self._board_size / 2
        center_y = self._board_bottom() + self._board_size / 2

        return [
            shape_list.create_rectangle_filled(
                center_x + 9,
                center_y - 11,
                outer_size,
                outer_size,
                self._with_alpha(self.render.color_shadow, 150),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                center_y,
                outer_size,
                outer_size,
                self._to_rgba(self.render.color_panel_border),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                center_y,
                inner_size,
                inner_size,
                self._to_rgba(self.render.color_panel),
            ),
            shape_list.create_rectangle_filled(
                center_x,
                center_y,
                self._board_size,
                self._board_size,
                self._to_rgba(self.render.color_board),
            ),
        ]

    def _build_grid_shapes(self) -> list[shape_list.Shape]:
        lines: list[shape_list.Shape] = []
        cs = self.render.cell_size
        left = self._board_left()
        bottom = self._board_bottom()
        right = left + self._board_size
        top = bottom + self._board_size

        for offset in range(BOARD_SIZE + 1):
            x = left + offset * cs
            y = bottom + offset * cs
            lines.append(shape_list.create_line(x, bottom, x, top, self._to_rgba(self.render.color_grid), 3))
            lines.append(shape_list.create_line(left, y, right, y, self._to_rgba(self.render.color_grid), 3))
        return lines

    def _build_title_text(self) -> arcade.Text:
        return arcade.Text(
            self.app_config.window.title,
            self._panel_left() + self._panel_padding_x,
            self._panel_top() - 40,
            self.render.color_title,
            30,
            font_name=self.render.font_name,
            bold=True,
            anchor_x="left",
            anchor_y="center",
        )

    def _build_overlay_texts(self) -> tuple[arcade.Text, ...]:
        start_y = self._panel_top() - 108
        return tuple(
            arcade.Text(
                line,
                self._panel_left() + self._panel_padding_x,
                start_y - index * self._line_spacing,
                self.render.color_overlay_text,
                16,
                font_name=self.render.font_name,
                anchor_x="left",
                anchor_y="center",
            )
            for index, line in enumerate(self.overlay_lines)
        )

    def _build_progress_text(self) -> arcade.Text:
        badge_left, badge_bottom, badge_width, badge_height = self._progress_badge_bounds()
        return arcade.Text(
            self._progress_label(),
            badge_left + badge_width / 2,
            badge_bottom + badge_height / 2,
            self.render.color_overlay_text,
            15,
            font_name=self.render.font_name,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    def _build_blank_text(self) -> arcade.Text:
        return arcade.Text(
            "?",
            0,
            0,
            self.render.color_blank_text,
            int(self.render.cell_size * 0.26),
            font_name=self.render.font_name,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    def _build_tile_texts(
        self,
        color: tuple[int, int, int] | tuple[int, int, int, int],
        offset_x: float,
        offset_y: float,
    ) -> dict[int, arcade.Text]:
        font_size = int(self.render.cell_size * 0.34)
        return {
            tile: arcade.Text(
                str(tile),
                offset_x,
                offset_y,
                color,
                font_size,
                font_name=self.render.font_name,
                bold=True,
                anchor_x="center",
                anchor_y="center",
            )
            for tile in range(1, 9)
        }

    def _sync_dynamic_texts(self) -> None:
        blank_center_x = self._cell_center_x(self.state.blank_cell)
        blank_center_y = self._cell_center_y(self.state.blank_cell)
        self._blank_text.x = blank_center_x
        self._blank_text.y = blank_center_y
        self._progress_text.text = self._progress_label()
        positions = self.state.positions

        for tile in range(1, 9):
            center_x = self._cell_center_x(positions[tile])
            center_y = self._cell_center_y(positions[tile])
            self._tile_texts[tile].x = center_x
            self._tile_texts[tile].y = center_y
            self._tile_shadow_texts[tile].x = center_x + 2
            self._tile_shadow_texts[tile].y = center_y - 3

    def _draw_blank(self) -> None:
        left, bottom = self._cell_left_bottom(self.state.blank_cell)
        outer_inset = self.render.cell_size * 0.08
        inner_inset = self.render.cell_size * 0.13
        width = self.render.cell_size - outer_inset * 2
        height = self.render.cell_size - outer_inset * 2
        arcade.draw_lbwh_rectangle_filled(
            left + outer_inset + 5,
            bottom + outer_inset - 5,
            width,
            height,
            self._with_alpha(self.render.color_shadow, 120),
        )
        arcade.draw_lbwh_rectangle_filled(
            left + outer_inset,
            bottom + outer_inset,
            width,
            height,
            self._mix(self.render.color_blank, self.render.color_panel_border, 0.22),
        )
        arcade.draw_lbwh_rectangle_filled(
            left + inner_inset,
            bottom + inner_inset,
            self.render.cell_size - inner_inset * 2,
            self.render.cell_size - inner_inset * 2,
            self.render.color_blank,
        )
        self._blank_text.draw()

    def _draw_tiles(self) -> None:
        inset = self.render.cell_size * 0.08
        solved = self.state.is_goal_state()
        tile_shadow_offset_x = self.render.cell_size * 0.05
        tile_shadow_offset_y = self.render.cell_size * 0.045
        tile_width = self.render.cell_size - inset * 2
        tile_height = self.render.cell_size - inset * 2
        positions = self.state.positions

        for tile in range(1, 9):
            tile_color = self._tile_color(tile, solved)
            left, bottom = self._cell_left_bottom(positions[tile])
            arcade.draw_lbwh_rectangle_filled(
                left + inset + tile_shadow_offset_x,
                bottom + inset - tile_shadow_offset_y,
                tile_width,
                tile_height,
                self._with_alpha(self.render.color_shadow, 135),
            )
            arcade.draw_lbwh_rectangle_filled(
                left + inset,
                bottom + inset,
                tile_width,
                tile_height,
                tile_color,
            )
            arcade.draw_lbwh_rectangle_filled(
                left + inset + 8,
                bottom + inset + tile_height - 16,
                tile_width - 16,
                8,
                self._mix(tile_color, self.render.color_title, 0.28),
            )
            self._tile_shadow_texts[tile].draw()
            self._tile_texts[tile].draw()

    def _draw_overlay(self) -> None:
        self._title_text.draw()
        self._draw_progress_badge()
        for text_line in self._overlay_texts:
            text_line.draw()

    def _draw_progress_badge(self) -> None:
        badge_left, badge_bottom, badge_width, badge_height = self._progress_badge_bounds()

        arcade.draw_lbwh_rectangle_filled(
            badge_left + 4,
            badge_bottom - 4,
            badge_width,
            badge_height,
            self._with_alpha(self.render.color_shadow, 120),
        )
        arcade.draw_lbwh_rectangle_filled(
            badge_left,
            badge_bottom,
            badge_width,
            badge_height,
            self._mix(self.render.color_panel_border, self.render.color_title, 0.12),
        )
        arcade.draw_lbwh_rectangle_filled(
            badge_left + 3,
            badge_bottom + 3,
            badge_width - 6,
            badge_height - 6,
            self.render.color_panel,
        )
        self._progress_text.draw()

    def _progress_label(self) -> str:
        return f"Paso: {self.sequence_index}/{max(0, len(self.state_sequence) - 1)}"

    def _progress_badge_bounds(self) -> tuple[float, float, float, float]:
        badge_width = min(160, self._panel_width() - 40)
        badge_height = 38
        left = self._panel_left() + self._panel_width() - badge_width - 20
        bottom = self._panel_top() - badge_height - 24
        return left, bottom, badge_width, badge_height

    def _board_left(self) -> float:
        return self.render.margin

    def _board_bottom(self) -> float:
        return self.render.margin

    def _panel_left(self) -> float:
        return self._board_left() + self._board_size + self.render.panel_gap

    def _panel_bottom(self) -> float:
        return self.render.margin

    def _panel_top(self) -> float:
        return self._panel_bottom() + self._panel_height()

    def _panel_width(self) -> float:
        return self.render.panel_width

    def _panel_height(self) -> float:
        return self._board_size

    def _cell_left_bottom(self, cell: int) -> tuple[float, float]:
        row, col = divmod(cell, BOARD_SIZE)
        left = self._board_left() + col * self.render.cell_size
        bottom = self._board_bottom() + (BOARD_SIZE - 1 - row) * self.render.cell_size
        return left, bottom

    def _cell_center_x(self, cell: int) -> float:
        left, _ = self._cell_left_bottom(cell)
        return left + self.render.cell_size / 2

    def _cell_center_y(self, cell: int) -> float:
        _, bottom = self._cell_left_bottom(cell)
        return bottom + self.render.cell_size / 2

    def _tile_color(self, tile: int, solved: bool) -> tuple[int, int, int]:
        if solved:
            return self._mix(self.render.color_tile_goal, self.render.color_title, 0.08)

        lift = 0.04 * ((tile - 1) % 4)
        return self._mix(self.render.color_tile, self.render.color_title, lift)

    @staticmethod
    def _to_rgba(color: tuple[int, int, int]) -> tuple[int, int, int, int]:
        return color[0], color[1], color[2], 255

    @staticmethod
    def _with_alpha(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
        return color[0], color[1], color[2], max(0, min(255, alpha))

    @staticmethod
    def _mix(
        color_a: tuple[int, int, int],
        color_b: tuple[int, int, int],
        ratio: float,
    ) -> tuple[int, int, int]:
        bounded_ratio = max(0.0, min(1.0, ratio))
        return tuple(
            round(color_a[index] * (1 - bounded_ratio) + color_b[index] * bounded_ratio)
            for index in range(3)
        )


def run_visualizer(
    config: AppConfig,
    state: State | None = None,
    state_sequence: Sequence[State] | None = None,
    overlay_lines: Sequence[str] | None = None,
    step_seconds: float | None = None,
) -> None:
    _window = EightPuzzleWindow(
        config=config,
        state=state,
        state_sequence=state_sequence,
        overlay_lines=overlay_lines,
        step_seconds=step_seconds,
    )
    arcade.run()
