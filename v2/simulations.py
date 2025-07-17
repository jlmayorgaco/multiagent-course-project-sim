# simulation.py

import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add the src/ folder to import your own modules
sys.path.append(os.path.abspath("src"))

# MESA imports
from mesa.batchrunner import BatchRunner
from src.models.model import PalmerasModel

# --- Parameters (can be modified manually or passed via CLI in the future) --- #
params = {
    "width": 12,
    "height": 12,
    "densidad": 0.2,
    "n_drones": 3,
    "tasa_propagacion": 0.1,
    "tasa_cura": 0.8,
    "max_steps": 1000
}

# --- Initialize and Run Simulation --- #
model = PalmerasModel(
    width=params["width"],
    height=params["height"],
    densidad=params["densidad"],
    n_drones=params["n_drones"],
    tasa_propagacion=params["tasa_propagacion"],
    tasa_cura=params["tasa_cura"]
)

for step in range(params["max_steps"]):
    model.step()

# --- Collect Data --- #
model_df = model.datacollector.get_model_vars_dataframe()
agents_df = model.datacollector.get_agent_vars_dataframe()

# --- Save Results with Timestamp --- #
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"results/simulation_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

model_df.to_csv(os.path.join(output_dir, "model_data.csv"))
agents_df.to_csv(os.path.join(output_dir, "agents_data.csv"))

# --- Save Params Used --- #
with open(os.path.join(output_dir, "params.json"), "w") as f:
    json.dump(params, f, indent=4)

print(f"✅ Simulation completed and saved to: {output_dir}")
