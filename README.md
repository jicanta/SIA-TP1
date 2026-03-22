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

python3 -m venv venv
source venv/bin/activate      # Mac/Linux
.\venv\Scripts\activate       # Windows
pip install arcade pandas matplotlib

## Comandos principales

### Sokoban: buscar y visualizar una solución
python run_visualizer.py --level `LEVEL` --algorithm `ALGORITHM`

Busca usando el algoritmo configurado para ese nivel y anima la solución en la ventana.
Si solo querés abrir el estado inicial, agregá `--initial-only`.

### 8-puzzle: buscar y visualizar una solución
python run_eight_puzzle_visualizer.py --puzzle `PUZZLE`

Busca usando el algoritmo configurado para ese puzzle y anima la solución en la ventana.
Si solo querés abrir el tablero inicial, agregá `--initial-only`.

### 8-puzzle: ejecutar búsqueda con visualización
python 8-puzzle/run_eight_puzzle.py --puzzle `PUZZLE` --algorithm `ALGORITHM`

`PUZZLE`: usar `python 8-puzzle/run_eight_puzzle.py --list-puzzles` para ver los disponibles

`ALGORITHM`:

Desinformados: bfs, dfs, dls, iddfs

Informados: astar_h1, astar_h2, greedy_h1, greedy_h2

El estado objetivo del 8-puzzle no es una única disposición fija: se considera resuelto cualquier tablero que preserve las adyacencias del tablero canónico `1 2 3 / 4 5 6 / 7 8 ?`, tal como se define en `Ejercicio1.md`.

### 8-puzzle: ejecutar búsqueda sin visualización
python 8-puzzle/run_eight_puzzle.py --puzzle `PUZZLE` --algorithm `ALGORITHM` --no-visualizer

Sirve para correr el 8-puzzle y ver solo el resumen por consola.

La organización del 8-puzzle quedó así:

- `8-puzzle/eight_puzzle/configs/default.json`: configuración compartida de ventana, render y búsqueda
- `8-puzzle/eight_puzzle/puzzles/*.json`: tableros disponibles
- `8-puzzle/run_eight_puzzle.py`: ejecuta la búsqueda y permite elegir puzzle por nombre
- `8-puzzle/run_eight_puzzle_visualizer.py`: busca y visualiza una solución; con `--initial-only` muestra solo el estado inicial

### Ejecutar un nivel con visualización
python run_search.py --level `LEVEL` --algorithm `ALGORITHM`

`LEVEL`:level_1, level_2, level_3

`ALGORITHM`:

Desinformados: bfs, dfs, dls, iddfs

A*: astar_h1, astar_h1_player, astar_h2, astar_h2_player, astar_h2_deadlock, astar_h2_player_deadlock

Greedy: greedy_h1, greedy_h1_player, greedy_h2, greedy_h2_player, greedy_h2_deadlock, greedy_h2_player_deadlock

Sirve para correr un nivel y ver la solución en la ventana gráfica.

### Ejecutar un nivel sin visualización
python run_search.py --level `LEVEL` --algorithm `ALGORITHM` --no-visualizer

`LEVEL`: level_1, level_2, level_3

`ALGORITHM`:

Desinformados: bfs, dfs, dls, iddfs

A*: astar_h1, astar_h1_player, astar_h2, astar_h2_player, astar_h2_deadlock, astar_h2_player_deadlock

Greedy: greedy_h1, greedy_h1_player, greedy_h2, greedy_h2_player, greedy_h2_deadlock, greedy_h2_player_deadlock

Sirve para correr un nivel y ver solo el resumen por consola.

### Ejecutar todas las corridas
python run_all.py

Sirve para correr todos los niveles y algoritmos configurados y guardar los resultados en output/results.csv.

### Generar gráficos
python plot_results.py

Sirve para generar gráficos a partir de output/results.csv y guardarlos en output/graphs/.
