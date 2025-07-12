from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider
from model import PalmerasModel
from agents import PalmeraAgent, DronAgent

def agent_portrayal(agent):
    portrayal = {"Layer": 0, "w": 1, "h": 1}
    
    if isinstance(agent, PalmeraAgent):
        if agent.estado == "verde":
            portrayal["Shape"] = "images/palmera_verde.png"
        elif agent.estado == "infectada":
            portrayal["Shape"] = "images/palmera_cafe.png"
    elif isinstance(agent, DronAgent):
        portrayal = {
            "Shape": "images/dron.png",
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



