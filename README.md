# SIA-TP1 - Sokoban y 8-Puzzle

Implementación de Sokoban en Python con:

- búsqueda desinformada: `BFS`, `DFS`, `DLS`, `IDDFS`
- búsqueda informada: `A*` y `Greedy`
- visualización de soluciones
- generación de resultados y gráficos

Incluye además una implementación del 8-puzzle usando el mismo motor genérico de búsqueda.

## Requisitos

- Python 3.12 recomendado

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
.\venv\Scripts\activate       # Windows
pip install arcade pandas matplotlib
```

## Sokoban

### Buscar y visualizar una solución

```bash
python3 run_visualizer.py --level LEVEL --algorithm ALGORITHM
```

Busca usando el algoritmo indicado y anima la solución en la ventana gráfica.
Agregá `--initial-only` si solo querés ver el estado inicial sin buscar.

### Buscar sin visualización (solo consola)

```bash
python3 run_search.py --level LEVEL --algorithm ALGORITHM --no-visualizer
```

Muestra por consola el resumen con todas las métricas al finalizar:

- `encontrada`: si/no
- `movimientos`: costo de la solución (largo del camino)
- `acciones`: secuencia de movimientos (U/D/L/R)
- `expandidos`: nodos expandidos
- `generados`: sucesores generados en total
- `visitados`: estados únicos visitados
- `frontera`: tamaño de la frontera al finalizar la búsqueda
- `frontera_max`: tamaño máximo que alcanzó la frontera durante la búsqueda

### Ejecutar todos los niveles y algoritmos

```bash
python3 run_all.py
```

Corre todas las combinaciones de niveles y algoritmos y guarda los resultados en `output/results.csv`.

### Generar gráficos

```bash
python3 plot_results.py
```

Genera gráficos a partir de `output/results.csv` y los guarda en `output/graphs/`.

### Niveles disponibles

`level_1` hasta `level_11`

### Algoritmos disponibles

**Desinformados:** `bfs`, `dfs`, `dls`, `iddfs`

**A\* (admisibles — garantizan solución óptima):**

| Algoritmo | Heurística |
|-----------|-----------|
| `astar_h1` | H1: suma de distancias Manhattan mínimas caja→meta |
| `astar_h2` | H2: asignación óptima cajas→metas (más informada que H1) |
| `astar_h1_player` | H3 = H1 + distancia del jugador a la caja más cercana |
| `astar_h2_player` | H4 = H2 + distancia del jugador a la caja más cercana |
| `astar_h2_deadlock` | H2 + detección de posiciones de deadlock |
| `astar_h2_player_deadlock` | H4 + detección de posiciones de deadlock |

**Greedy (admisibles — no garantizan solución óptima):**

| Algoritmo | Heurística |
|-----------|-----------|
| `greedy_h1` | H1 |
| `greedy_h2` | H2 |
| `greedy_h1_player` | H3 |
| `greedy_h2_player` | H4 |
| `greedy_h2_deadlock` | H2 + deadlock |
| `greedy_h2_player_deadlock` | H4 + deadlock |

---

## 8-Puzzle

### Buscar y visualizar una solución

```bash
python3 8-puzzle/run_eight_puzzle_visualizer.py --puzzle PUZZLE
```

### Buscar sin visualización

```bash
python3 8-puzzle/run_eight_puzzle.py --puzzle PUZZLE --algorithm ALGORITHM --no-visualizer
```

Ver puzzles disponibles:

```bash
python3 8-puzzle/run_eight_puzzle.py --list-puzzles
```

**Algoritmos disponibles:**

- Desinformados: `bfs`, `dfs`, `dls`, `iddfs`
- Informados: `astar_h1`, `astar_h2`, `greedy_h1`, `greedy_h2`

El estado objetivo del 8-puzzle no es una única disposición fija: se considera resuelto cualquier tablero que preserve las adyacencias del tablero canónico `1 2 3 / 4 5 6 / 7 8 ?`, tal como se define en `Ejercicio1.md`.

### Archivos relevantes

- `8-puzzle/eight_puzzle/configs/default.json`: configuración compartida de ventana, render y búsqueda
- `8-puzzle/eight_puzzle/puzzles/*.json`: tableros disponibles
- `8-puzzle/run_eight_puzzle.py`: ejecuta la búsqueda
- `8-puzzle/run_eight_puzzle_visualizer.py`: busca y visualiza la solución
