# --------------------------------------------------------- #
# --- Imports --------------------------------------------- #
# --------------------------------------------------------- #
import random
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
# --------------------------------------------------------- #

# --------------------------------------------------------- #
# --- Imports Agents -------------------------------------- #
# --------------------------------------------------------- #
# Real Agents
from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent
from src.agents.ChargingStationAgent import ChargingStationAgent

# Visualization Angets
from src.visualization.GridCellAgent import GridCellAgent
# --------------------------------------------------------- #

class PalmerasModel(Model):
    """
    Multi-agent simulation model for monitoring and controlling disease spread 
    in wax palm trees using drones.

    This class initializes a grid-based environment using the MESA framework,
    where each cell can contain palm trees, drones, or ground sensors.
    Drones move around to detect infected palms, update a shared blackboard,
    and coordinate actions to maximize forest health.
    """
    def __init__(self, width, height, densidad, n_drones, tasa_propagacion, tasa_cura):
        
        # Model (Mesa) Parameters
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.running = True
        self.current_id = 0

        # Model (Control & Logs) Parameters
        self.highlighted_cells = set()
        self.datacollector = DataCollector(
            model_reporters={
                # Simulación
                "Step": lambda m: m.schedule.time,

                # Palmas
                "PalmasTotales": lambda m: sum(isinstance(a, PalmAgent) for a in m.schedule.agents),
                "PalmasInfectadas": self.count_palmas_infectadas,
                "PalmasSanas": self.count_palmas_curadas,
                "PalmasQuemadas": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, PalmAgent) and a.estado == "quemada"
                ),
                "PalmasDetectadas": lambda m: len(m.blackboard["palms_targets"]),

                # Drones
                "DronesTotales": lambda m: m.n_drones,
                "DronesActivos": lambda m: sum(
                    isinstance(a, DroneAgent) and not a.is_charging for a in m.schedule.agents
                ),
                "DronesCargando": lambda m: sum(
                    isinstance(a, DroneAgent) and a.is_charging for a in m.schedule.agents
                ),

                # Infraestructura
                "EstacionesCarga": lambda m: len(m.blackboard["charging_stations_positions"]),

                # Métricas de desempeño
                "Cobertura": self.compute_cobertura,  # % del grid visible
                "ObjetivosCompartidos": lambda m: len(m.blackboard["palms_targets"]),
            },
            agent_reporters = {

                # Posición
                "pos": lambda a: a.pos if hasattr(a, "pos") else None,
                "x": lambda a: a.pos[0] if hasattr(a, "pos") else None,
                "y": lambda a: a.pos[1] if hasattr(a, "pos") else None,

                # Tipo de agente
                "agent_type": lambda a: type(a).__name__,

                # Estado interno general
                "agent_state": lambda a: a.estado if isinstance(a, PalmAgent) else (
                    a.state if isinstance(a, DroneAgent) else None
                ),

                # Estado específico de palm (solo si tiene health_level)
                "palm_health": lambda a: a.health_level if isinstance(a, PalmAgent) and hasattr(a, "health_level") else None,

                # Estado específico de drone
                "drone_battery_level": lambda a: a.battery.get_level() if isinstance(a, DroneAgent) and hasattr(a.battery, "get_level") else None,
                "drone_position_target": lambda a: a.target if isinstance(a, DroneAgent) else None,

                # Acciones (solo para DroneAgent)
                "drone_on_mission": lambda a: a.on_mission if isinstance(a, DroneAgent) else None,
                "drone_is_charging": lambda a: a.is_charging if isinstance(a, DroneAgent) else None,
                "drone_is_curing": lambda a: a.is_curing if isinstance(a, DroneAgent) else None,
            }
        )


        # Model (Environment) Parameters
        self.width = width
        self.height = height
        self.densidad = densidad

        # Model (Simulation) Parameters
        self.n_drones = n_drones
        self.tasa_propagacion = tasa_propagacion
        self.tasa_cura = tasa_cura

        # Model (Blackboard) Parameters
        self.blackboard = {
            "palms_targets": {},       # Dict { (x, y): confidence }
            "drones_positions": {},     # Dict { drone_id: (x, y) }
            "charging_stations_positions": {}  # Dict { (x, y): is_busy }
        }

        # Init Population of Agents in Grid
        self._init_model_blackboard()
        self._init_model_cells_agents()
        self._init_model_drones_and_stations()
        self._init_model_palms_agents()

    def _generate_charging_positions(self):
        """
        Generate spaced random positions on the grid edges for charging stations.
        Ensures positions are only on the border (edges) of the grid and are unique.
        """
        edge_positions = set()

        # Bottom and top rows
        for x in range(self.width):
            edge_positions.add((x, 0))                      # bottom edge
            edge_positions.add((x, self.height - 1))        # top edge

        # Left and right columns (excluding corners to avoid duplicates)
        for y in range(1, self.height - 1):
            edge_positions.add((0, y))                      # left edge
            edge_positions.add((self.width - 1, y))         # right edge

        # Shuffle and choose `n_drones` unique edge positions
        edge_positions = list(edge_positions)
        random.shuffle(edge_positions)

        return edge_positions[:self.n_drones]


    def _init_model_blackboard(self):
        self.blackboard = {
            "palms_targets": {},
            "drones_positions": {},
            "charging_stations_positions": {}
        }

    def _init_model_cells_agents(self):
        for x in range(self.width):
            for y in range(self.height):
                cell_agent = GridCellAgent(self.next_id(), self, (x, y))
                self.grid.place_agent(cell_agent, (x, y))
                self.schedule.add(cell_agent)

    def _generate_charging_positions(self):
        # Only border cells (top, bottom, left, right)
        positions = []
        for x in range(self.width):
            positions.append((x, 0))  # Top edge
            positions.append((x, self.height - 1))  # Bottom edge
        for y in range(1, self.height - 1):  # Avoid corners again
            positions.append((0, y))  # Left edge
            positions.append((self.width - 1, y))  # Right edge
        return positions


    def _init_model_palms_agents(self):
        for (contents, x, y) in self.grid.coord_iter():
            # Skip if already occupied by charging station or drone
            has_occupied = any(isinstance(a, (ChargingStationAgent, DroneAgent)) for a in contents)
            if has_occupied:
                continue

            # Find the GridCellAgent at this position
            cell_agents = [a for a in contents if isinstance(a, GridCellAgent)]
            if not cell_agents or not cell_agents[0].can_have_palm:
                continue  # No cell agent or cannot host palm

            if random.random() < self.densidad:
                estado_inicial = "infectada" if random.random() < 0.1 else "verde"
                palm = PalmAgent(self.next_id(), self, (x, y), estado_inicial)
                self.grid.place_agent(palm, (x, y))
                self.schedule.add(palm)


    def _init_model_drones_and_stations(self):
        all_positions = self._generate_charging_positions()
        random.shuffle(all_positions)  # Randomize edges

        self.charging_stations = []

        if len(all_positions) < self.n_drones:
            raise ValueError("Not enough edge positions for all drones.")

        for i in range(self.n_drones):
            pos = all_positions[i]

            # Place Charging Station
            station = ChargingStationAgent(self.next_id(), self, pos, assigned_drone_id=i)
            self.grid.place_agent(station, pos)
            self.schedule.add(station)
            self.charging_stations.append(station)

            # Add to blackboard
            self.blackboard["charging_stations_positions"][pos] = i

            # Place Drone at same position
            drone = DroneAgent(self.next_id(), self, pos)
            self.grid.place_agent(drone, pos)
            self.schedule.add(drone)

        print(' ')
        print(' self.blackboard["charging_stations_positions"] ')
        print(' ')
        print(self.blackboard["charging_stations_positions"])
        print(' ')
        print(' ')



    def update_blackboard_drone_positions(self, agent_id, position):
   
        self.blackboard["drones_positions"][agent_id] = position
        self.reset_grid_cells()
        self.set_grid_cells()

        for y in range(self.grid.height - 1, -1, -1):
            row = ""
            for x in range(self.grid.width):
                agents = self.grid.get_cell_list_contents((x, y))
                cell_agent = next((a for a in agents if isinstance(a, GridCellAgent)), None)
                if cell_agent:
                    row += cell_agent.get_status_char(self.blackboard["drones_positions"]) + " "
                else:
                    row += "? "

        visible_cells = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )
        total_cells = self.grid.width * self.grid.height
        

    def reset_grid_cells(self):
        total_cells = self.grid.width * self.grid.height

        visible_before = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )
        for agent in self.schedule.agents:
            if isinstance(agent, GridCellAgent):
                agent.reset_visibility()

        visible_after = sum(
            1 for agent in self.schedule.agents
            if isinstance(agent, GridCellAgent) and agent._visible_by_drones_count > 0
        )

    def set_grid_cells(self):
        for drone_id, drone_pos in self.blackboard["drones_positions"].items():
            x, y = drone_pos
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                        for agent in self.grid.get_cell_list_contents((nx, ny)):
                            if isinstance(agent, GridCellAgent):
                                agent.mark_visible()

    def update_blackboard_palms_targets(self, position, confidence):
        current = self.blackboard["palms_targets"].get(position, 0.0)
        self.blackboard["palms_targets"][position] = max(current, confidence)

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
    
    def get_blackboard_charging_stations_positions(self):
        return self.blackboard["charging_stations_positions"]

    def get_blackboard_drones_positions(self):
        return self.blackboard.get("drones_positions", {})
    
    def report_palm_cured(self, position, confidence=0):
        """
        Called by a drone to notify the model that a palm at the given
        position has been cured. If confidence is high enough, removes
        the target from the blackboard and updates GridCellAgent visuals.
        """

        if position in self.blackboard["palms_targets"]:
            if abs(confidence) > 0.5:
                del self.blackboard["palms_targets"][position]

        # Update GridCellAgent visuals
        for agent in self.grid.get_cell_list_contents([position]):
            if isinstance(agent, GridCellAgent):
                agent.reset_target()



    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


    def count_palmas_infectadas(self):
        return sum(1 for a in self.schedule.agents if isinstance(a, PalmAgent) and a.estado == "infectada")

    def count_palmas_curadas(self):
        return sum(1 for a in self.schedule.agents if isinstance(a, PalmAgent) and a.estado == "verde")

    def compute_cobertura(self):
        total = self.grid.width * self.grid.height
        visibles = sum(1 for a in self.schedule.agents if isinstance(a, GridCellAgent) and a.IsVisibleByDrones)
        return visibles / total if total > 0 else 0

    