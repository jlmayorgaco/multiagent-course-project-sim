#
import random

#
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

#
from src.agents.PalmAgent import PalmAgent
from src.agents.DroneAgent import DroneAgent


class PalmerasModel(Model):
    def __init__(self, width, height, densidad, n_drones, tasa_propagacion, tasa_cura):
        self.width = width
        self.height = height
        self.densidad = densidad
        self.n_drones = n_drones
        self.tasa_propagacion = tasa_propagacion
        self.tasa_cura = tasa_cura
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.running = True
        self.current_id = 0

        # Blackboard shared among agents
        self.blackboard = {
            "palms_targets": {},       # List of {"location": (x, y), "confidence": 0.9}
            "drones_positions": {}     # Dict of {drone_id: (x, y)}
        }

        # Crear palmeras
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.densidad:
                estado_inicial = "infectada" if random.random() < 0.1 else "verde"
                palmera = PalmAgent(self.next_id(), (x, y), self, estado_inicial)
                self.grid.place_agent(palmera, (x, y))
                self.schedule.add(palmera)

        # Crear drones
        for _ in range(self.n_drones):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            drone = DroneAgent(self.next_id(), (x, y), self)
            self.grid.place_agent(drone, (x, y))
            self.schedule.add(drone)

            # Logging drone creation
            print(f"[INFO] Drone #{drone.unique_id} created at position ({x}, {y})")
            #print(f"       - Initial battery: {drone.battery.get_level()}")
            #print(f"       - Initial medicine: {drone.medicine.get_level()}")
            #print(f"       - Initial state: {drone.state}")


    def step(self):
        self.schedule.step()

