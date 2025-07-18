import os
import json
import pandas as pd
from datetime import datetime
from src.models.model import PalmerasModel

def run_simulation(params: dict):
    model = PalmerasModel(
        width=params["width"],
        height=params["height"],
        densidad=params["densidad"],
        n_drones=params["n_drones"],
        tasa_propagacion=params["tasa_propagacion"],
        tasa_cura=params["tasa_cura"]
    )
    for _ in range(params["max_steps"]):
        model.step()
    return model.datacollector.get_model_vars_dataframe()

def safe_div(n, d):
    return n / d if d > 0 else 0

def compute_score(row):
    palmas_totales = row["PalmasTotales"]
    infectadas = row["PalmasInfectadas"]
    cured_rate = safe_div(row["PalmasSanas"], palmas_totales)
    burned_rate = safe_div(row["PalmasQuemadas"], palmas_totales)
    detection_rate = safe_div(row["PalmasDetectadas"], infectadas)
    return 0.4 * cured_rate + 0.3 * (1 - burned_rate) + 0.3 * detection_rate

# --------------------------
# Configuración
# --------------------------
output_dir = "results_per_drone"
os.makedirs(output_dir, exist_ok=True)

base_params = {
    "width": 12,
    "height": 12,
    "densidad": 0.2,
    "tasa_propagacion": 0.1,
    "tasa_cura": 0.8,
    "max_steps": 100
}

n_drones = int(input("Número de drones a simular (ej. 1, 2, 3...): "))
n_runs = 10
results = []

print(f"🚀 Simulando {n_runs} corridas con {n_drones} drones...")

for run in range(n_runs):
    params = base_params.copy()
    params["n_drones"] = n_drones

    df = run_simulation(params)
    df["PerformanceScore"] = df.apply(compute_score, axis=1)
    final_score = df["PerformanceScore"].iloc[-1]

    results.append({
        "run": run + 1,
        "n_drones": n_drones,
        "final_score": final_score
    })

df_result = pd.DataFrame(results)
output_path = os.path.join(output_dir, f"drones_{n_drones}.csv")
df_result.to_csv(output_path, index=False)
print(f"✅ Resultados guardados en {output_path}")
