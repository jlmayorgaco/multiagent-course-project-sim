from mesa import Agent
import random

class PalmAgent(Agent):
    def __init__(self, unique_id, model, pos, estado="verde"):
        super().__init__(unique_id, model)
        self.pos = pos
        self.estado = estado

    def step(self):
        if self.estado == "verde":
            vecinos = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for vecino in vecinos:
                if isinstance(vecino, PalmAgent) and vecino.estado == "infectada":
                    if random.random() < self.model.tasa_propagacion:
                        self.estado = "infectada"
                        break