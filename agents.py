from mesa import Agent
import random

class PalmeraAgent(Agent):
    def __init__(self, unique_id, pos, model, estado="verde"):
        super().__init__(unique_id, model)
        self.pos = pos
        self.estado = estado

    def step(self):
        if self.estado == "verde":
            vecinos = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for vecino in vecinos:
                if isinstance(vecino, PalmeraAgent) and vecino.estado == "infectada":
                    if random.random() < self.model.tasa_propagacion:
                        self.estado = "infectada"
                        break


class DronAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Intentar curar palmeras infectadas cercanas
        vecinos = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for vecino in vecinos:
            if isinstance(vecino, PalmeraAgent) and vecino.estado == "infectada":
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

