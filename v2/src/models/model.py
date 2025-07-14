import random
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent
from src.agents.GridCellAgent import GridCellAgent


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
                cell_agent = GridCellAgent(self.next_id(), self, (x, y))
                self.grid.place_agent(cell_agent, (x, y))
                self.schedule.add(cell_agent)

        # 🌴 PalmAgents
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.densidad:
                estado_inicial = "infectada" if random.random() < 0.1 else "verde"
                palm = PalmAgent(self.next_id(), self, (x, y), estado_inicial)
                self.grid.place_agent(palm, (x, y))
                self.schedule.add(palm)

        # 🚁 DroneAgents
        for _ in range(self.n_drones):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            drone = DroneAgent(self.next_id(), self, (x, y))
            self.grid.place_agent(drone, (x, y))
            self.schedule.add(drone)
            print(f"[INFO] Drone #{drone.unique_id} created at position ({x}, {y})")

    def update_blackboard_drone_positions(self, agent_id, position):
        print("\n" * 5)
        print(" =========================> BLACKBOARD UPDATE POSITION DEBUG <=========================\n")
        print(f"[DEBUG] Updating drone #{agent_id} position to {position}\n")

        self.blackboard["drones_positions"][agent_id] = position
        self.reset_grid_cells()
        self.set_grid_cells()

        print("\n =========================> GRID STATUS DEBUG <=========================\n")
        print("     " + " ".join(f"{x:02}" for x in range(self.grid.width)))

        for y in range(self.grid.height - 1, -1, -1):
            row = ""
            for x in range(self.grid.width):
                agents = self.grid.get_cell_list_contents((x, y))
                cell_agent = next((a for a in agents if isinstance(a, GridCellAgent)), None)
                if cell_agent:
                    row += cell_agent.get_status_char(self.blackboard["drones_positions"]) + " "
                else:
                    row += "? "
            print(f"Row {y:02}: {row}")

        visible_cells = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )
        total_cells = self.grid.width * self.grid.height
        print(f"\n[DEBUG] Visible cells: {visible_cells}/{total_cells} ({100 * visible_cells / total_cells:.2f}%)")
        print("\nLegend: D = Drone, V = Visible, . = Not visible, ? = Missing GridCellAgent\n")
        print("\n" * 3)

    def reset_grid_cells(self):
        total_cells = self.grid.width * self.grid.height

        visible_before = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )
        print(f"[DEBUG] Visible grid cells BEFORE reset: {visible_before}/{total_cells} ({(visible_before / total_cells) * 100:.2f}%)")

        print("[DEBUG] Resetting all grid cell visibility...")
        for agent in self.schedule.agents:
            if isinstance(agent, GridCellAgent):
                agent.reset_visibility()

        visible_after = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )
        print(f"[DEBUG] Visible grid cells AFTER reset: {visible_after}/{total_cells} ({(visible_after / total_cells) * 100:.2f}%)")

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
        return [{"location": pos, "confidence": conf} for pos, conf in raw_targets.items()]

    def get_blackboard_drones_positions(self):
        return self.blackboard.get("drones_positions", {})

    def step(self):
        print("\n[MODEL STEP] ---------")
        self.schedule.step()
