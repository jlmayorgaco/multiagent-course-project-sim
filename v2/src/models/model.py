import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent
from src.agents.GridCellAgent import GridCellAgent  # ← NEW


class PalmerasModel(Model):
    def __init__(self, width, height, densidad, n_drones, tasa_propagacion, tasa_cura):
        self.width = width
        self.height = height
        self.densidad = densidad
        self.n_drones = n_drones
        self.tasa_propagacion = tasa_propagacion
        self.tasa_cura = tasa_cura
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.running = True
        self.current_id = 0

        self.highlighted_cells = set()

        self.blackboard = {
            "palms_targets": {},       # Dict { (x, y): confidence }
            "drones_positions": {}     # Dict { drone_id: (x, y) }
        }

        # 🟫 GridCellAgents
        for x in range(width):
            for y in range(height):
                cell_agent = GridCellAgent(self.next_id(), (x, y), self)
                self.grid.place_agent(cell_agent, (x, y))

        # 🌴 PalmAgents
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.densidad:
                estado_inicial = "infectada" if random.random() < 0.1 else "verde"
                palm = PalmAgent(self.next_id(), (x, y), self, estado_inicial)
                self.grid.place_agent(palm, (x, y))
                self.schedule.add(palm)

        # 🚁 DroneAgents
        for _ in range(self.n_drones):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            drone = DroneAgent(self.next_id(), (x, y), self)
            self.grid.place_agent(drone, (x, y))
            self.schedule.add(drone)
            print(f"[INFO] Drone #{drone.unique_id} created at position ({x}, {y})")

    def update_blackboard_drone_positions(self, agent_id, position):
        """Update drone position and recompute visibility overlays."""
        print(f"[DEBUG] Updating drone #{agent_id} position to {position}")
        self.blackboard["drones_positions"][agent_id] = position

        self.reset_grid_cells()
        self.set_grid_cells()

    def reset_grid_cells(self):
        print("[DEBUG] Resetting all grid cell visibility...")
        for agent in self.schedule.agents:
            if isinstance(agent, GridCellAgent):
                agent.reset_visibility()

    def set_grid_cells(self):
        print("[DEBUG] Recomputing visible grid cells from drone positions...")
        for drone_id, drone_pos in self.blackboard["drones_positions"].items():
            x, y = drone_pos
            print(f"[DEBUG] Drone #{drone_id} field of view from ({x},{y}):")
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                        print(f"   → Marking cell ({nx},{ny}) as visible")
                        for agent in self.grid.get_cell_list_contents((nx, ny)):
                            if isinstance(agent, GridCellAgent):
                                agent.mark_visible()

    def update_blackboard_palms_targets(self, position, confidence):
        current = self.blackboard["palms_targets"].get(position, 0.0)
        self.blackboard["palms_targets"][position] = max(current, confidence)

        print(f"[DEBUG] Updating infected palm target at {position} with confidence {confidence}")

        for agent in self.schedule.agents:
            if isinstance(agent, GridCellAgent):
                agent.reset_target()

        for pos in self.blackboard["palms_targets"]:
            print(f"[DEBUG] Marking cell {pos} as palm target")
            for agent in self.grid.get_cell_list_contents(pos):
                if isinstance(agent, GridCellAgent):
                    agent.mark_as_target()

    def get_blackboard_palms_targets(self):
        raw_targets = self.blackboard.get("palms_targets", {})
        return [
            {"location": pos, "confidence": conf}
            for pos, conf in raw_targets.items()
        ]

    def get_blackboard_drones_positions(self):
        return self.blackboard.get("drones_positions", {})

    def step(self):
        print("\n[MODEL STEP] ---------")
        self.schedule.step()
