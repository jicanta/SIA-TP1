from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Callable

BOARD_SIZE = 3
CELL_COUNT = BOARD_SIZE * BOARD_SIZE
TILES = tuple(range(CELL_COUNT))
CANONICAL_BOARD = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def cell_to_coords(cell: int) -> tuple[int, int]:
    return divmod(cell, BOARD_SIZE)


def manhattan_cells(cell_a: int, cell_b: int) -> int:
    row_a, col_a = cell_to_coords(cell_a)
    row_b, col_b = cell_to_coords(cell_b)
    return abs(row_a - row_b) + abs(col_a - col_b)


def _build_orthogonal_neighbors() -> tuple[tuple[int, ...], ...]:
    neighbors: list[tuple[int, ...]] = []
    for cell in range(CELL_COUNT):
        row, col = cell_to_coords(cell)
        cell_neighbors: list[int] = []
        if row > 0:
            cell_neighbors.append(cell - BOARD_SIZE)
        if row < BOARD_SIZE - 1:
            cell_neighbors.append(cell + BOARD_SIZE)
        if col > 0:
            cell_neighbors.append(cell - 1)
        if col < BOARD_SIZE - 1:
            cell_neighbors.append(cell + 1)
        neighbors.append(tuple(cell_neighbors))
    return tuple(neighbors)


ORTHOGONAL_NEIGHBORS = _build_orthogonal_neighbors()


def _board_to_positions(board_values: tuple[int, ...]) -> tuple[int, ...]:
    if len(board_values) != CELL_COUNT:
        raise ValueError(f"El tablero debe tener {CELL_COUNT} celdas, se recibieron {len(board_values)}.")

    normalized = tuple(int(tile) for tile in board_values)
    if tuple(sorted(normalized)) != TILES:
        raise ValueError("El tablero debe contener exactamente una vez cada numero entre 0 y 8.")

    positions = [0] * CELL_COUNT
    for cell, tile in enumerate(normalized):
        positions[tile] = cell
    return tuple(positions)


def _positions_to_board(positions: tuple[int, ...]) -> tuple[int, ...]:
    board = [0] * CELL_COUNT
    for tile, cell in enumerate(positions):
        board[cell] = tile
    return tuple(board)


CANONICAL_POSITIONS = _board_to_positions(CANONICAL_BOARD)


def _build_canonical_neighbors() -> tuple[frozenset[int], ...]:
    neighbors: list[frozenset[int]] = []
    for tile in TILES:
        cell = CANONICAL_POSITIONS[tile]
        neighbors.append(
            frozenset(CANONICAL_BOARD[neighbor_cell] for neighbor_cell in ORTHOGONAL_NEIGHBORS[cell])
        )
    return tuple(neighbors)


CANONICAL_NEIGHBORS = _build_canonical_neighbors()


def _identity(row: int, col: int) -> tuple[int, int]:
    return row, col


def _rotate_90(row: int, col: int) -> tuple[int, int]:
    return col, BOARD_SIZE - 1 - row


def _rotate_180(row: int, col: int) -> tuple[int, int]:
    return BOARD_SIZE - 1 - row, BOARD_SIZE - 1 - col


def _rotate_270(row: int, col: int) -> tuple[int, int]:
    return BOARD_SIZE - 1 - col, row


def _reflect_vertical(row: int, col: int) -> tuple[int, int]:
    return row, BOARD_SIZE - 1 - col


def _reflect_horizontal(row: int, col: int) -> tuple[int, int]:
    return BOARD_SIZE - 1 - row, col


def _reflect_main_diagonal(row: int, col: int) -> tuple[int, int]:
    return col, row


def _reflect_anti_diagonal(row: int, col: int) -> tuple[int, int]:
    return BOARD_SIZE - 1 - col, BOARD_SIZE - 1 - row


def _build_goal_position_tuples() -> tuple[tuple[int, ...], ...]:
    transforms: tuple[Callable[[int, int], tuple[int, int]], ...] = (
        _identity,
        _rotate_90,
        _rotate_180,
        _rotate_270,
        _reflect_vertical,
        _reflect_horizontal,
        _reflect_main_diagonal,
        _reflect_anti_diagonal,
    )

    unique_positions: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for transform in transforms:
        transformed_board = [0] * CELL_COUNT
        for cell, tile in enumerate(CANONICAL_BOARD):
            row, col = cell_to_coords(cell)
            next_row, next_col = transform(row, col)
            transformed_board[next_row * BOARD_SIZE + next_col] = tile
        positions = _board_to_positions(tuple(transformed_board))
        if positions not in seen:
            seen.add(positions)
            unique_positions.append(positions)
    return tuple(unique_positions)


GOAL_POSITION_TUPLES = _build_goal_position_tuples()


@dataclass(frozen=True, slots=True)
class State:
    positions: tuple[int, ...]

    def __post_init__(self) -> None:
        normalized = tuple(int(cell) for cell in self.positions)
        if len(normalized) != CELL_COUNT:
            raise ValueError(f"El vector de posiciones debe tener largo {CELL_COUNT}.")
        if tuple(sorted(normalized)) != TILES:
            raise ValueError("El vector de posiciones debe ser una permutacion de 0..8.")
        object.__setattr__(self, "positions", normalized)

    @classmethod
    def from_positions(cls, positions: Iterable[int]) -> "State":
        return cls(positions=tuple(int(cell) for cell in positions))

    @classmethod
    def from_board(cls, board_values: Iterable[int] | Iterable[Iterable[int]]) -> "State":
        flat_board = _flatten_board(board_values)
        return cls(positions=_board_to_positions(flat_board))

    @property
    def blank_cell(self) -> int:
        return self.positions[0]

    @property
    def board(self) -> tuple[int, ...]:
        return _positions_to_board(self.positions)

    def as_matrix(self) -> tuple[tuple[int, ...], ...]:
        board = self.board
        return tuple(
            tuple(board[row * BOARD_SIZE : (row + 1) * BOARD_SIZE])
            for row in range(BOARD_SIZE)
        )

    def neighbor_tiles(
        self,
        tile: int,
        board_values: tuple[int, ...] | None = None,
    ) -> frozenset[int]:
        if tile not in TILES:
            raise ValueError(f"Ficha invalida: {tile}")
        board = board_values or self.board
        cell = self.positions[tile]
        return frozenset(board[neighbor_cell] for neighbor_cell in ORTHOGONAL_NEIGHBORS[cell])

    def is_goal_state(self) -> bool:
        board = self.board
        return all(
            self.neighbor_tiles(tile, board) == CANONICAL_NEIGHBORS[tile]
            for tile in TILES
        )


def _flatten_board(board_values: Iterable[int] | Iterable[Iterable[int]]) -> tuple[int, ...]:
    raw_values = tuple(board_values)
    if not raw_values:
        raise ValueError("El tablero no puede estar vacio.")

    if all(isinstance(row, (list, tuple)) for row in raw_values):
        if len(raw_values) != BOARD_SIZE:
            raise ValueError(f"El tablero matricial debe tener {BOARD_SIZE} filas.")
        flat: list[int] = []
        for row in raw_values:
            if len(row) != BOARD_SIZE:
                raise ValueError(f"Cada fila del tablero debe tener {BOARD_SIZE} columnas.")
            flat.extend(int(tile) for tile in row)
        return tuple(flat)

    return tuple(int(tile) for tile in raw_values)
