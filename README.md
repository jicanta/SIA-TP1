# SIA-TP1 - Sokoban

Implementación de Sokoban en Python con:

- búsqueda desinformada: `BFS`, `DFS`, `DLS`, `IDDFS`
- búsqueda informada: `A*` y `Greedy`
- visualización de soluciones
- generación de resultados y gráficos

## Requisitos

- Python 3.12 recomendado

## Instalación

python3 -m venv venv
source venv/bin/activate      # Mac/Linux
.\venv\Scripts\activate       # Windows
pip install arcade pandas matplotlib

## Comandos principales

### Solo visualizador del estado inicial
python run_visualizer.py

Sirve para abrir la ventana y mostrar el estado inicial configurado.

### Ejecutar un nivel con visualización
python run_search.py --level <LEVEL> --algorithm <ALGORITHM>

<LEVEL>: level_1, level_2, level_3, level_4

<ALGORITHM>:

Desinformados: bfs, dfs, dls, iddfs

A*: astar_h1, astar_h1_player, astar_h2, astar_h2_player, astar_h2_deadlock, astar_h2_player_deadlock

Greedy: greedy_h1, greedy_h1_player, greedy_h2, greedy_h2_player, greedy_h2_deadlock, greedy_h2_player_deadlock

Sirve para correr un nivel y ver la solución en la ventana gráfica.

### Ejecutar un nivel sin visualización
python run_search.py --level <LEVEL> --algorithm <ALGORITHM> --no-visualizer

<LEVEL>: level_1, level_2, level_3, level_4

<ALGORITHM>:

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