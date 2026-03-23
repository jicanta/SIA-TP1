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


def _normalize_board(board_values: Iterable[int] | Iterable[Iterable[int]]) -> tuple[int, ...]:
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
        normalized = tuple(flat)
    else:
        normalized = tuple(int(tile) for tile in raw_values)

    if len(normalized) != CELL_COUNT:
        raise ValueError(f"El tablero debe tener {CELL_COUNT} celdas, se recibieron {len(normalized)}.")
    if tuple(sorted(normalized)) != TILES:
        raise ValueError("El tablero debe contener exactamente una vez cada numero entre 0 y 8.")
    return normalized


def _board_to_positions(board_values: tuple[int, ...]) -> tuple[int, ...]:
    positions = [0] * CELL_COUNT
    for cell, tile in enumerate(board_values):
        positions[tile] = cell
    return tuple(positions)


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


def _build_goal_boards() -> tuple[tuple[int, ...], ...]:
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

    unique_boards: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for transform in transforms:
        transformed_board = [0] * CELL_COUNT
        for cell, tile in enumerate(CANONICAL_BOARD):
            row, col = cell_to_coords(cell)
            next_row, next_col = transform(row, col)
            transformed_board[next_row * BOARD_SIZE + next_col] = tile
        board = tuple(transformed_board)
        if board not in seen:
            seen.add(board)
            unique_boards.append(board)
    return tuple(unique_boards)


GOAL_BOARDS = _build_goal_boards()
GOAL_BOARD_SET = frozenset(GOAL_BOARDS)
GOAL_POSITIONS = tuple(_board_to_positions(goal_board) for goal_board in GOAL_BOARDS)


@dataclass(frozen=True, slots=True)
class State:
    board: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "board", _normalize_board(self.board))

    @classmethod
    def from_board(cls, board_values: Iterable[int] | Iterable[Iterable[int]]) -> "State":
        return cls(board=_normalize_board(board_values))

    @classmethod
    def from_positions(cls, positions: Iterable[int]) -> "State":
        normalized_positions = tuple(int(cell) for cell in positions)
        if len(normalized_positions) != CELL_COUNT:
            raise ValueError(f"El vector de posiciones debe tener largo {CELL_COUNT}.")
        if tuple(sorted(normalized_positions)) != TILES:
            raise ValueError("El vector de posiciones debe ser una permutacion de 0..8.")

        board = [0] * CELL_COUNT
        for tile, cell in enumerate(normalized_positions):
            board[cell] = tile
        return cls(board=tuple(board))

    @property
    def blank_cell(self) -> int:
        return self.board.index(0)

    @property
    def positions(self) -> tuple[int, ...]:
        return _board_to_positions(self.board)

    def position_of(self, tile: int) -> int:
        if tile not in TILES:
            raise ValueError(f"Ficha invalida: {tile}")
        return self.board.index(tile)

    def as_matrix(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(self.board[row * BOARD_SIZE : (row + 1) * BOARD_SIZE])
            for row in range(BOARD_SIZE)
        )

    def neighbor_tiles(self, tile: int) -> frozenset[int]:
        if tile not in TILES:
            raise ValueError(f"Ficha invalida: {tile}")
        cell = self.position_of(tile)
        return frozenset(self.board[neighbor_cell] for neighbor_cell in ORTHOGONAL_NEIGHBORS[cell])

    def move_blank(self, d_row: int, d_col: int) -> "State | None":
        blank_row, blank_col = cell_to_coords(self.blank_cell)
        next_row = blank_row + d_row
        next_col = blank_col + d_col
        if not (0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE):
            return None

        next_cell = next_row * BOARD_SIZE + next_col
        next_board = list(self.board)
        blank_cell = self.blank_cell
        next_board[blank_cell], next_board[next_cell] = next_board[next_cell], next_board[blank_cell]
        return State(board=tuple(next_board))

    def flattened_without_blank(self) -> tuple[int, ...]:
        return tuple(tile for tile in self.board if tile != 0)

    def inversion_count(self) -> int:
        flattened = self.flattened_without_blank()
        inversions = 0
        for index, tile in enumerate(flattened[:-1]):
            inversions += sum(1 for other in flattened[index + 1 :] if tile > other)
        return inversions

    def inversion_parity(self) -> int:
        return self.inversion_count() % 2

    def is_goal_state(self) -> bool:
        return all(self.neighbor_tiles(tile) == CANONICAL_NEIGHBORS[tile] for tile in TILES)
