from mesa import Agent
from .PalmAgent import PalmAgent

import random

class DroneAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Intentar curar palmeras infectadas cercanas
        vecinos = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for vecino in vecinos:
            if isinstance(vecino, PalmAgent) and vecino.estado == "infectada":
                if random.random() < self.model.tasa_cura:
                    vecino.estado = "verde"

        # Moverse a una celda vecina aleatoria
        posibles_movimientos = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        nueva_pos = random.choice(posibles_movimientos)
        self.model.grid.move_agent(self, nueva_pos)

