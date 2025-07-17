# ---------------------------------------------------------------- #
# -- Imports Utils ------------------------------------------------ #
# ---------------------------------------------------------------- #
import os
import sys
import atexit
sys.path.append(os.path.abspath("src"))

# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# -- Imports MESA ------------------------------------------------ #
# ---------------------------------------------------------------- #

from mesa.visualization.UserParam import Slider
from mesa.visualization.modules import CanvasGrid
from mesa.datacollection import DataCollector
from mesa.visualization.ModularVisualization import ModularServer

# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# -- Imports Agents y Models ------------------------------------- #
# ---------------------------------------------------------------- #

# Agents
from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent

# Models
from src.models.model import PalmerasModel


# ---------------------------------------------------------------- #

# Grid Config
from src.visualization.AgentPortrayal import AgentPortrayal
from src.visualization.BlackboardText import BlackboardText

grid = CanvasGrid(AgentPortrayal, 12, 12, 600, 600)
blackboard_text = BlackboardText()


model_params = {

    "width": 12,
    "height": 12,

    "densidad": Slider("Densidad de palmeras", 0.1, 0.25, 1.0, 0.1),
    "n_drones": Slider("Número de drones", 3, 1, 10, 1),

    "tasa_propagacion": Slider("Tasa de propagación", 0.01, 0.0, 1.0, 0.05),
    "tasa_cura": Slider("Tasa de curación por drones", 1.0, 0.0, 1.0, 0.05),
}

server = ModularServer(
    PalmerasModel,
    [grid, blackboard_text],
    "Simulación de Palmeras y Drones",
    model_params
)

def save_data():
    try:
        if hasattr(server, "model") and server.model is not None:
            model_df = server.model.datacollector.get_model_vars_dataframe()
            agents_df = server.model.datacollector.get_agent_vars_dataframe()

            model_df.to_csv("resultados_modelo.csv", index=True)
            agents_df.to_csv("resultados_agentes.csv", index=True)

            print("✅ Datos guardados en 'resultados_modelo.csv' y 'resultados_agentes.csv'")
        else:
            print("⚠️ No hay modelo activo para guardar datos.")
    except Exception as e:
        print("❌ Error al guardar datos:", e)
atexit.register(save_data)

server.port = 8560
server.launch()
