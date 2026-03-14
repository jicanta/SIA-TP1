import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def bar_chart(ax, algorithms, values, color, ylabel, title):
    ax.bar(algorithms, values, color=color)
    ax.set_xticks(range(len(algorithms)))
    ax.set_xticklabels(algorithms, rotation=45, ha="right")
    ax.set_title(title, fontsize=13, pad=12)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Algoritmo")
    ax.grid(axis="y", linestyle="--", alpha=0.7)


def save_fig(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def plot_per_level(level_df, level, output_dir):
    level_label = str(level).removesuffix(".json")
    algorithms = level_df["algoritmo"].tolist()

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        algorithms,
        level_df["expandidos"],
        "skyblue",
        "Cantidad de Nodos",
        f"Nodos Expandidos por Algoritmo - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_nodos_expandidos.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        algorithms,
        level_df["tiempo_segundos"],
        "coral",
        "Tiempo (segundos)",
        f"Tiempo de Ejecución por Algoritmo - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_tiempo.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        algorithms,
        level_df["movimientos"],
        "lightgreen",
        "Cantidad de Movimientos",
        f"Largo de la Solución (Movimientos) - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_movimientos.png")

    df_no_iddfs = level_df[~level_df["algoritmo"].str.lower().eq("iddfs")]

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        df_no_iddfs["algoritmo"].tolist(),
        df_no_iddfs["tiempo_segundos"],
        "coral",
        "Tiempo (segundos)",
        f"Tiempo de Ejecución (sin IDDFS) - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_tiempo_sin_iddfs.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        df_no_iddfs["algoritmo"].tolist(),
        df_no_iddfs["expandidos"],
        "skyblue",
        "Cantidad de Nodos",
        f"Nodos Expandidos (sin IDDFS) - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_nodos_expandidos_sin_iddfs.png")

    df_no_dfs_dls = level_df[~level_df["algoritmo"].str.lower().isin(["dfs", "dls"])]

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        df_no_dfs_dls["algoritmo"].tolist(),
        df_no_dfs_dls["movimientos"],
        "lightgreen",
        "Cantidad de Movimientos",
        f"Movimientos (sin DFS/DLS) - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_movimientos_sin_dfs_dls.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_chart(
        ax,
        algorithms,
        level_df["visitados"],
        "mediumpurple",
        "Cantidad de Nodos",
        f"Nodos Visitados por Algoritmo - {level_label}",
    )
    save_fig(fig, output_dir / f"{level}_visitados.png")


def main():
    base_dir = Path(__file__).parent
    output_base_dir = base_dir / "output"
    results_file = output_base_dir / "results.csv"
    output_dir = output_base_dir / "graphs"

    if not results_file.exists():
        print(f"❌ No se encontró el archivo: {results_file}")
        return

    print("📊 Leyendo resultados y generando gráficos...")

    output_dir.mkdir(exist_ok=True)

    try:
        df = pd.read_csv(results_file)

        successful_df = df[df["encontrada"] == "si"].copy()
        numeric_columns = ["movimientos", "expandidos", "generados", "visitados", "tiempo_segundos"]

        for column in numeric_columns:
            successful_df[column] = pd.to_numeric(successful_df[column], errors="coerce")

        levels = successful_df["nivel"].unique()

        for level in levels:
            print(f"\nGenerando gráficos para {level}...")
            level_df = successful_df[successful_df["nivel"] == level]
            plot_per_level(level_df, level, output_dir)

        print("\n✅ ¡Listo! Todos los gráficos se guardaron en output/graphs/")

    except Exception as e:
        print(f"⚠️ Error al generar los gráficos: {e}")
        raise


if __name__ == "__main__":
    main()