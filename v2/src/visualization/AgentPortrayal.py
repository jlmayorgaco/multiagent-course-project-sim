# ---------------------------------------------------------------- #
# -- Imports Agents y Models ------------------------------------- #
# ---------------------------------------------------------------- #

from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent
from src.agents.GridCellAgent import GridCellAgent

from src.models.model import PalmerasModel
# ---------------------------------------------------------------- #


# ---------------------- Individual Portrayals ------------------- #

def GridCellAgentPortrayal(agent):
    x, y = agent.pos
    text_color = "gray"

    # Color logic based on visibility and targeting
    if agent.IsPalmTargeted:
        color = "#FF5733"  # Reddish tone for infected palm target
        alpha = 0.6
    elif agent.IsVisibleByDrones:
        color = "#EBB682"  # Black for drone vision
        text_color= "black"
        alpha = 0.3
    else:
        color = "#B56E28"  # Default background
        text_color= "white"
        alpha = 1.0

    return {
        "Layer": 0,
        "Shape": "rect",
        "Color": color,
        "alpha": alpha,
        "w": 1,
        "h": 1,
        "Filled": "true",
        "text": f"({x},{y})",
        "text_color": text_color
    }


def PalmAgentPortrayal(agent):
    shapes = {
        "verde": "images/palm_green.png",
        "infectada": "images/palm_brown.png"
    }

    shape = shapes.get(agent.estado, "images/palm_green.png")

    return {
        "Layer": 1,
        "Shape": shape,
        "w": 1,
        "h": 1
    }


def DroneAgentPortrayal(agent):
    x, y = agent.pos
    portrayal = {
        "Layer": 2,
        "w": 3,
        "h": 3,
        "id": str(agent.unique_id),
        "(x,y)": str(agent.pos),
        "text": str(agent.unique_id),
        "text_color": "black",
    }

    print(f"[Drone {agent.unique_id}] Position: {agent.pos}, Next move: {agent.next_move}, State: {agent.state}")

    if agent.next_move and agent.next_move != agent.pos:
        dx = agent.next_move[0] - x
        dy = agent.next_move[1] - y
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
        portrayal["Shape"] = "images/drone.png"
        print(f"[Drone {agent.unique_id}] Direction: {direction}, Arrow image: images/drone.png")
    else:
        portrayal["Shape"] = "images/drone.png"
        print(f"[Drone {agent.unique_id}] Staying in place. Default image: images/drone.png")

    print(f"[Drone {agent.unique_id}] Portrayal: {portrayal}")
    return portrayal


# ------------------------- Unified Entry ------------------------ #

def AgentPortrayal(agent):
    if not agent:
        return None

    if isinstance(agent, GridCellAgent):
        return GridCellAgentPortrayal(agent)

    elif isinstance(agent, PalmAgent):
        return PalmAgentPortrayal(agent)

    elif isinstance(agent, DroneAgent):
        return DroneAgentPortrayal(agent)

    return None
