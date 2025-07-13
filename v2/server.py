# ---------------------------------------------------------------- #
# -- Imports Utils ------------------------------------------------ #
# ---------------------------------------------------------------- #
import sys
import os
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

def agent_portrayal(agent):
    portrayal = {"Layer": 0, "w": 1, "h": 1}
    
    if isinstance(agent, PalmAgent):
        if agent.estado == "verde":
            portrayal["Shape"] = "images/palm_green.png"
        elif agent.estado == "infectada":
            portrayal["Shape"] = "images/palm_brown.png"
    elif isinstance(agent, DroneAgent):
        portrayal = {
            "Shape": "images/drone.png",
            "Layer": 1,
            "w": 1,
            "h": 1,
        }
    
    return portrayal


grid = CanvasGrid(agent_portrayal, 20, 20, 600, 600)

model_params = {

    "width": 20,
    "height": 20,

    "densidad": Slider("Densidad de palmeras", 0.6, 0.1, 1.0, 0.1),
    "n_drones": Slider("Número de drones", 3, 1, 10, 1),

    "tasa_propagacion": Slider("Tasa de propagación", 0.2, 0.0, 1.0, 0.05),
    "tasa_cura": Slider("Tasa de curación por drones", 1.0, 0.0, 1.0, 0.05),
}

server = ModularServer(
    PalmerasModel,
    [grid],
    "Simulación de Palmeras y Drones",
    model_params
)
server.port = 8560
server.launch()
