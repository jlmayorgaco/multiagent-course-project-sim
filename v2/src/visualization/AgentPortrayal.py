# ---------------------------------------------------------------- #
# -- Imports Agents y Models ------------------------------------- #
# ---------------------------------------------------------------- #

from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent
from src.agents.ChargingStationAgent import ChargingStationAgent
from src.visualization.GridCellAgent import GridCellAgent

from src.models.model import PalmerasModel
# ---------------------------------------------------------------- #


# ---------------------- Individual Portrayals ------------------- #

def GridCellAgentPortrayal(agent):
    x, y = agent.pos
    text_color = "gray"
    shape= "rect"

    # Color logic based on visibility and targeting
    if agent.IsPalmTargeted:
        color = "#FF5733"  # Reddish tone for infected palm target
        alpha = 0.6
    elif agent.IsVisibleByDrones:
        color = "#a4b490"  # Black for drone vision
        text_color= "black"
        alpha = 0.3
    else:
        if agent.cell_type == 0:
            shape= "images/Field/BG_1.png"
        elif agent.cell_type == 1:
            shape= "images/Field/BG_2.png"
        elif agent.cell_type == 2:
            shape= "images/Field/BG_3.png"
        elif agent.cell_type == 3:
            shape= "images/Field/BG_4.png"
        elif agent.cell_type == 4:
            shape= "images/Field/BG_5.png"
        elif agent.cell_type == 5:
            shape= "images/Field/BG_6.png"
        elif agent.cell_type == 6:
            shape= "images/Field/BG_7.png"
        color = "#85a75b"  # Default background
        text_color= "white"
        alpha = 1.0

    return {
        "Layer": 0,
        "Shape": shape,
        "Color": color,
        "alpha": alpha,
        "w": 1,
        "h": 1,
        "Filled": "true",
        "text": f"({x},{y})",
        "text_color": text_color
    }

def ChargingStationAgentPortrayal(agent):
    return {
        "Layer": 0,
        "Shape": "images/ChargingStation/ChargingStation_0.png", 
        "Color": "#FFF700",
        "Filled": "true",
        "w": 1,
        "h": 1,
        "text": "⚡",
        "text_color": "black"
    }


def PalmAgentPortrayal(agent):
    shapes = {
        "muerta": "images/Palms/Palm_4.png",
        "verde": "images/Palms/Palm_0.png",
        "infectada_0": "images/Palms/Palm_1.png",
        "infectada_1": "images/Palms/Palm_2.png",
        "infectada_2": "images/Palms/Palm_3.png"
    }

    if agent.estado != "infectada":
        key = agent.estado
    else:
        if agent.health_level > 90:
            level = 0
        elif agent.health_level > 50:
            level = 1
        else:
            level = 2
        key = f"{agent.estado}_{level}"

    shape = shapes.get(key, "images/Palms/Palm_1.png")

    return {
        "Layer": 1,
        "Shape": shape,
        "w": 1,
        "h": 1
    }



def DroneAgentPortrayal(agent):
    x, y = agent.pos
    shapes = {
        "exploring": "images/Drone/Drone_0.png",
        "charging": "images/Drone/Drone_1.png",
        "curing": "images/Drone/Drone_2.png",
        "dead": "images/Drone/Drone_3.png",
    }

    # Default shape based on state
    shape = shapes.get(agent.state, "images/Drone/Drone_0.png")

    # Base portrayal
    portrayal = {
        "Layer": 2,
        "w": 3,
        "h": 3,
        "id": str(agent.unique_id),
        "(x,y)": str(agent.pos),
        "text": str(agent.unique_id),
        "text_color": "black",
        "Shape": shape,
    }

    # Debug logs
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

        direction_name = direction_map.get(direction, "unknown")
    else:
        print(f"[Drone {agent.unique_id}] Staying in place.")
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
    
    elif isinstance(agent, ChargingStationAgent):
        return ChargingStationAgentPortrayal(agent)

    return None
