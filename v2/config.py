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
        # Base layer for the drone position
        portrayal = {
            "Layer": 1,
            "w": 1,
            "h": 1,
        }

        # Use arrow based on direction if there's a next move
        if agent.next_move and agent.next_move != agent.pos:
            dx = agent.next_move[0] - agent.pos[0]
            dy = agent.next_move[1] - agent.pos[1]
            direction = (dx, dy)

            direction_map = {
                (0, 1): "up",
                (0, -1): "down",
                (1, 0): "right",
                (-1, 0): "left",
                (1, 1): "up_right",
                (-1, 1): "up_left",
                (1, -1): "down_right",
                (-1, -1): "down_left",
            }

            direction_name = direction_map.get(direction, "up")
            portrayal["Shape"] = f"images/drone_arrow_{direction_name}.png"
        else:
            portrayal["Shape"] = "images/drone.png"

    return portrayal
