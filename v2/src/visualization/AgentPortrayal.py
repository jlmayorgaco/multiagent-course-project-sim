# ---------------------------------------------------------------- #
# -- Imports Agents y Models ------------------------------------- #
# ---------------------------------------------------------------- #

# Agents
from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent

# Models
from src.models.model import PalmerasModel
# ---------------------------------------------------------------- #

def AgentPortrayal(agent):
    x, y = agent.pos if agent else (0, 0)
    portrayal = {
        "Layer": 0, 
        "w": 1, 
        "h": 1, 
        "Filled": "true",
        "text": f"({x},{y})",
        "text_color": "gray"
    }
    

    if isinstance(agent, PalmAgent):
        if agent.estado == "verde":
            portrayal["Shape"] = "images/palm_green.png"
        elif agent.estado == "infectada":
            portrayal["Shape"] = "images/palm_brown.png"

    elif isinstance(agent, DroneAgent):
        # Set up base portrayal
        portrayal = {
            "Layer": 1,
            "w": 3,
            "h": 3,
            "id": str(agent.unique_id),
            '(x,y)': str(agent.pos),
            "text_color": "black"
        }

        # Log base state
        print(f"[Drone {agent.unique_id}] Position: {agent.pos}, Next move: {agent.next_move}, State: {agent.state}")

        # Determine direction and image
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
            image_path = f"images/drone_arrow_{direction_name}.png"
            portrayal["Shape"] = image_path

            # Detailed debug output
            print(f"[Drone {agent.unique_id}] Direction: {direction}, Arrow image: {image_path}")
        else:
            portrayal["Shape"] = "images/drone.png"
            print(f"[Drone {agent.unique_id}] Staying in place. Default image: images/drone.png")

        # Log final portrayal
        print(f"[Drone {agent.unique_id}] Portrayal: {portrayal}")

    return portrayal
