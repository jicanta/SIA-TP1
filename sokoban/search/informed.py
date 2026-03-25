from __future__ import annotations

from collections import deque
from itertools import permutations
from typing import FrozenSet

from search import SearchResult
from search.informed import solve_astar as _solve_astar, solve_greedy as _solve_greedy

from ..models.board import Board
from ..models.position import Position
from ..models.state import State
from .uninformed import _SokobanProblem


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _manhattan(a: Position, b: Position) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


# A partir de aca se pueden implementar distintas heurísticas y funciones de resolución informada (A* y Greedy).

def h1_min_manhattan(state: State, goals: FrozenSet[Position]) -> int:
    """H1 [Admisible]: suma de distancias Manhattan mínimas de cada caja no ubicada a la meta libre más cercana.

    Es admisible porque la distancia Manhattan ignora paredes y otros obstáculos,
    por lo tanto nunca sobreestima el costo real de empujar cada caja a su meta.
    """
    unplaced = state.boxes - goals
    if not unplaced:
        return 0
    free_goals = goals - state.boxes
    return sum(min(_manhattan(box, goal) for goal in free_goals) for box in unplaced)


def h2_optimal_matching(state: State, goals: FrozenSet[Position]) -> int:
    """H2 [Admisible]: asignación óptima cajas a metas minimizando la distancia Manhattan total.

    Es admisible porque considera la mejor asignación posible de cajas a metas
    usando distancias Manhattan, que siguen siendo cotas inferiores del costo real.
    Es más informada que H1 porque evita contar la misma meta dos veces.
    """
    unplaced = list(state.boxes - goals)
    if not unplaced:
        return 0
    free_goals = list(goals - state.boxes)
    min_cost = float("inf")
    for perm in permutations(free_goals):
        cost = sum(_manhattan(b, g) for b, g in zip(unplaced, perm))
        if cost < min_cost:
            min_cost = cost
    return int(min_cost)


def _precompute_deadlock_positions(board: Board) -> FrozenSet[Position]:
    """Calcula estaticamente las posiciones donde una caja nunca podrá llegar a ninguna meta.

    Usa BFS hacia atras desde las metas: una posicion es alcanzable si existe alguna
    secuencia de empujes que lleve la caja hasta una meta. Cualquier posicion no alcanzable
    es un deadlock simple.
    """
    DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

    reachable: set[Position] = set(board.goals)
    queue: deque[Position] = deque(board.goals)

    while queue:
        pos = queue.popleft()
        for dr, dc in DIRECTIONS:
            prev = pos.move(-dr, -dc)
            if not board.contains(prev) or prev in board.walls or prev in reachable:
                continue
            reachable.add(prev)
            queue.append(prev)

    # Todo lo que no sea pared ni alcanzable es deadlock
    all_positions = frozenset(
        Position(r, c)
        for r in range(board.rows)
        for c in range(board.cols)
        if Position(r, c) not in board.walls
    )
    return all_positions - reachable


def _player_addend(state: State, goals: FrozenSet[Position]) -> int:
    """[Admisible] Cota inferior de pasos extra del jugador para alcanzar la caja no ubicada más cercana.

    El jugador debe recorrer al menos dist(jugador→caja) pasos para llegar a la caja,
    pero el último paso ya es un empuje (contado en H1/H2), por eso se resta 1.
    Como H1/H2 cuentan empujes y este término cuenta caminatas sin empujar,
    ambos componentes son independientes y la suma sigue siendo admisible.
    """
    unplaced = state.boxes - goals
    if not unplaced:
        return 0
    return max(0, min(_manhattan(state.player, box) for box in unplaced) - 1)


# Funciones de resolucion — A*

def solve_astar_h1(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H1 [Admisible]. Garantiza solución óptima."""
    goals = board.goals
    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h1_min_manhattan(s, goals),
        algorithm_name="astar_h1",
    )


def solve_astar_h2(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H2 [Admisible]. Garantiza solución óptima. Más informada que H1."""
    goals = board.goals
    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h2_optimal_matching(s, goals),
        algorithm_name="astar_h2",
    )


def solve_astar_h1_player(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H3 = H1 + distancia del jugador a la caja más cercana [Admisible]. Garantiza solución óptima."""
    goals = board.goals
    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h1_min_manhattan(s, goals) + _player_addend(s, goals),
        algorithm_name="astar_h1_player",
    )


def solve_astar_h2_player(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H4 = H2 + distancia del jugador a la caja más cercana [Admisible]. Garantiza solución óptima."""
    goals = board.goals
    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h2_optimal_matching(s, goals) + _player_addend(s, goals),
        algorithm_name="astar_h2_player",
    )

# Funciones de resolucion — Greedy

def solve_greedy_h1(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H1 [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h1_min_manhattan(s, goals),
        algorithm_name="greedy_h1",
    )


def solve_greedy_h2(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H2 [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h2_optimal_matching(s, goals),
        algorithm_name="greedy_h2",
    )


def solve_greedy_h1_player(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H3 = H1 + distancia del jugador [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h1_min_manhattan(s, goals) + _player_addend(s, goals),
        algorithm_name="greedy_h1_player",
    )


def solve_greedy_h2_player(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H4 = H2 + distancia del jugador [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=lambda s: h2_optimal_matching(s, goals) + _player_addend(s, goals),
        algorithm_name="greedy_h2_player",
    )


# Funciones de resolución — deadlock (H2 + detección de posiciones sin salida)

def _deadlock_check(
    state: State,
    goals: FrozenSet[Position],
    deadlock_positions: FrozenSet[Position],
) -> bool:
    """Retorna True si alguna caja no ubicada está en una posición de deadlock simple.

    Las posiciones de deadlock se calculan sin falsos positivos: si una posición
    está marcada como deadlock, ninguna secuencia de empujes puede llevar la caja
    a una meta. Por lo tanto, retornar inf para esos estados es correcto (h* = inf).
    """
    return any(box in deadlock_positions for box in state.boxes - goals)


def solve_astar_h2_deadlock(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H2 + detección de deadlocks simples [Admisible]. Garantiza solución óptima.

    Retorna inf cuando hay una caja en posición de deadlock (estado realmente irresoluble),
    lo cual es correcto y mantiene la admisibilidad.
    """
    goals = board.goals
    deadlock_positions = _precompute_deadlock_positions(board)

    def heuristic(s: State) -> float:
        if _deadlock_check(s, goals, deadlock_positions):
            return float("inf")
        return h2_optimal_matching(s, goals)

    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=heuristic,
        algorithm_name="astar_h2_deadlock",
    )


def solve_astar_h2_player_deadlock(initial_state: State, board: Board) -> SearchResult[State, str]:
    """A* con H4 + detección de deadlocks simples [Admisible]. Garantiza solución óptima.

    Combina H4 (H2 + distancia del jugador) con poda de deadlocks simples.
    Es la heurística más informada del conjunto y mantiene admisibilidad.
    """
    goals = board.goals
    deadlock_positions = _precompute_deadlock_positions(board)

    def heuristic(s: State) -> float:
        if _deadlock_check(s, goals, deadlock_positions):
            return float("inf")
        return h2_optimal_matching(s, goals) + _player_addend(s, goals)

    return _solve_astar(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=heuristic,
        algorithm_name="astar_h2_player_deadlock",
    )


def solve_greedy_h2_deadlock(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H2 + detección de deadlocks simples [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    deadlock_positions = _precompute_deadlock_positions(board)

    def heuristic(s: State) -> float:
        if _deadlock_check(s, goals, deadlock_positions):
            return float("inf")
        return h2_optimal_matching(s, goals)

    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=heuristic,
        algorithm_name="greedy_h2_deadlock",
    )


def solve_greedy_h2_player_deadlock(initial_state: State, board: Board) -> SearchResult[State, str]:
    """Greedy con H4 + detección de deadlocks simples [Admisible]. No garantiza solución óptima."""
    goals = board.goals
    deadlock_positions = _precompute_deadlock_positions(board)

    def heuristic(s: State) -> float:
        if _deadlock_check(s, goals, deadlock_positions):
            return float("inf")
        return h2_optimal_matching(s, goals) + _player_addend(s, goals)

    return _solve_greedy(
        _SokobanProblem(initial_state=initial_state, board=board),
        heuristic=heuristic,
        algorithm_name="greedy_h2_player_deadlock",
    )
