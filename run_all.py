import csv
import subprocess
import time
from pathlib import Path

LEVELS = ["level_1.json","level_2.json", "level_3.json", "level_4.json", "level_5.json", "level_6.json", "level_7.json", "level_8.json", "level_9.json", "level_10.json", "level_11.json"]

ALGORITHMS = [
    "bfs", "dfs", "dls", "iddfs",
    "astar_h1", "astar_h2", "astar_h1_player", "astar_h2_player",
    "greedy_h1", "greedy_h2", "greedy_h1_player", "greedy_h2_player",
    "astar_h2_deadlock", "astar_h2_player_deadlock",
    "greedy_h2_deadlock", "greedy_h2_player_deadlock"
]


def main():
    base_dir = Path(__file__).parent
    output_base_dir = base_dir / "output"
    results_file = output_base_dir / "results.csv"

    with open(results_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "algoritmo",
            "nivel",
            "encontrada",
            "movimientos",
            "expandidos",
            "generados",
            "visitados",
            "frontera",
            "frontera_max",
            "tiempo_segundos",
        ])

        for level in LEVELS:
            level_path = base_dir / "levels" / level
            if not level_path.exists():
                print(f"\n⚠️  Nivel no encontrado: {level_path}. Saltando...")
                continue

            print(f"\n📂 Probando nivel: {level}")
            print("--------------------------------------------------")

            for algorithm in ALGORITHMS:
                print(f"Buscando {level} con {algorithm:<30} ... ", end="", flush=True)

                cmd = [
                    ".venv/bin/python",
                    "run_search.py",
                    "--level", f"{level}",
                    "--algorithm", algorithm,
                    "--no-visualizer",
                ]

                try:
                    start_time = time.time()

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=base_dir,
                        timeout=500,
                    )

                    elapsed_time = time.time() - start_time

                    if result.returncode == 0:
                        if "encontrada: si" in result.stdout:
                            lines = result.stdout.split("\n")

                            found = "si"
                            movements = next((line.split(": ")[1] for line in lines if line.startswith("movimientos:")), "")
                            expanded_nodes = next((line.split(": ")[1] for line in lines if line.startswith("expandidos:")), "")
                            generated_nodes = next((line.split(": ")[1] for line in lines if line.startswith("generados:")), "")
                            visited_nodes = next((line.split(": ")[1] for line in lines if line.startswith("visitados:")), "")
                            frontier_nodes = next((line.split(": ")[1] for line in lines if line.startswith("frontera:")), "")
                            max_frontier_nodes = next((line.split(": ")[1] for line in lines if line.startswith("frontera_max:")), "")

                            print(f"✅ Encontrada! ({elapsed_time:.2f}s, Movs: {movements})")

                            writer.writerow([
                                algorithm,
                                level,
                                found,
                                movements,
                                expanded_nodes,
                                generated_nodes,
                                visited_nodes,
                                frontier_nodes,
                                max_frontier_nodes,
                                f"{elapsed_time:.4f}",
                            ])
                        else:
                            print("❌ No encontró solución.")
                            writer.writerow([algorithm, level, "no", "", "", "", "", "", "", f"{elapsed_time:.4f}"])

                    else:
                        print(f"⚠️  Error ejecutando el script (Exit code: {result.returncode})")
                        writer.writerow([algorithm, level, "error", "", "", "", "", "", "", ""])

                except subprocess.TimeoutExpired:
                    print("⏰ Timeout (más de 500 segundos)")
                    writer.writerow([algorithm, level, "timeout", "", "", "", "", "", "", ">500"])
                except Exception as e:
                    print(f"⚠️  Error inesperado: {e}")
                    writer.writerow([algorithm, level, "error", "", "", "", "", "", "", ""])

    print("\n--------------------------------------------------")
    print(f"📁 Resultados guardados en: {results_file.name}")


if __name__ == "__main__":
    main()