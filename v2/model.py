from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agents.PalmAgent import PalmAgent
from agents.DroneAgent import DroneAgent
import random

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

    def step(self):
        self.schedule.step()

