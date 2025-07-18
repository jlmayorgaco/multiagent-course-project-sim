import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 📁 Configuración de carpeta
DATA_DIR = Path("results_per_drone")

# 📥 Leer y combinar los 20 archivos
dfs = []
for i in range(1, 21):
    file_path = DATA_DIR / f"drones_{i}.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
        dfs.append(df)
    else:
        print(f"[WARNING] Archivo no encontrado: {file_path}")

# 🧪 Unir DataFrames
if not dfs:
    raise FileNotFoundError("No se encontraron archivos .csv en la ruta esperada.")

combined_df = pd.concat(dfs, ignore_index=True)

# 🎓 Estilo IEEE para gráficas
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.figsize": (3.5, 2.5),  # tamaño para una columna IEEE
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "axes.edgecolor": "black",
    "axes.linewidth": 0.8
})

# 📊 Graficar boxplot
fig, ax = plt.subplots()
sns.boxplot(data=combined_df, x="n_drones", y="final_score", ax=ax, palette="pastel", linewidth=0.7)
ax.set_title("Final Performance vs. Number of Drones")
ax.set_xlabel("Number of Drones")
ax.set_ylabel("Final Score")

# 💾 Guardar gráfico
plt.tight_layout()
plt.savefig("drone_score_boxplot_IEEE.png")
plt.savefig("drone_score_boxplot_IEEE.svg")
plt.savefig("drone_score_boxplot_IEEE.pdf")

# 📋 Mostrar y guardar estadísticos resumidos
summary = combined_df.groupby("n_drones")["final_score"].describe()
summary.to_csv("drone_score_summary.csv")
