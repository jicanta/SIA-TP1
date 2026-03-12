# SIA-TP1 - Sokoban (BFS/DFS + Visualizador)

Implementación base de Sokoban en Python con:
- Representación de estado/tablero
- Búsqueda desinformada: `BFS` y `DFS`
- Visualización con `arcade`

## Requisitos
- Windows + PowerShell
- Python 3.12 (recomendado)

## Instalación
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

### 2) Búsqueda + visualización de solución
```powershell
.\.venv-win\Scripts\python.exe run_search.py --algorithm bfs
.\.venv-win\Scripts\python.exe run_search.py --algorithm dfs
```

### 3) Búsqueda sin abrir ventana (solo consola)
```powershell
.\.venv-win\Scripts\python.exe run_search.py --algorithm bfs --no-visualizer
.\.venv-win\Scripts\python.exe run_search.py --algorithm dfs --no-visualizer
```

## Configuración
El archivo `config.json` controla:
- tablero (`board`: incluye paredes y metas fijas)
- estado inicial (`state`: jugador y cajas)
- render (`render`)
- búsqueda (`search`: algoritmo por defecto, límite DFS y velocidad de animación)
