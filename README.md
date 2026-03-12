# SIA-TP1 - Sokoban (BFS/DFS/DLS/IDDFS + Visualizador)

Implementacion base de Sokoban en Python con:
- Representacion de estado/tablero
- Busqueda desinformada: `BFS`, `DFS`, `DLS` e `IDDFS`
- Visualizacion con `arcade`

## Requisitos
- Windows + PowerShell
- Python 3.12 (recomendado)

## Instalacion
```powershell
cd c:\Users\ignac\OneDrive\Escritorio\SIA\SIA-TP1
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install --upgrade pip
.\.venv-win\Scripts\python.exe -m pip install arcade
```

## Ejecutar
### 1) Solo visualizador del estado inicial
```powershell
.\.venv-win\Scripts\python.exe run_visualizer.py
```

### 2) Busqueda + visualizacion de solucion
```powershell
.\.venv-win\Scripts\python.exe run_search.py --algorithm bfs
.\.venv-win\Scripts\python.exe run_search.py --algorithm dfs
.\.venv-win\Scripts\python.exe run_search.py --algorithm dls
.\.venv-win\Scripts\python.exe run_search.py --algorithm iddfs
```

### 3) Busqueda sin abrir ventana (solo consola)
```powershell
.\.venv-win\Scripts\python.exe run_search.py --algorithm bfs --no-visualizer
.\.venv-win\Scripts\python.exe run_search.py --algorithm dfs --no-visualizer
.\.venv-win\Scripts\python.exe run_search.py --algorithm dls --no-visualizer
.\.venv-win\Scripts\python.exe run_search.py --algorithm iddfs --no-visualizer
```

## Configuracion
El archivo `config.json` controla:
- tablero (`board`: incluye paredes y metas fijas)
- estado inicial (`state`: jugador y cajas)
- render (`render`)
- busqueda (`search`: algoritmo por defecto, limite DFS y velocidad de animacion)
