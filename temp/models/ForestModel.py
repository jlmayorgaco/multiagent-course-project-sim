from mesa import Model
from mesa.space import MultiGrid

from agents.PalmAgent import PalmAgent
from agents.QuadcopterAgent import QuadcopterAgent
from agents.PersonAgent import PersonAgent

import random

class ForestModel(Model):
    def __init__(self, width=10, height=10, num_palms=20, num_drones=2, num_people=1, seed=None):
        super().__init__(seed=seed)  # Mesa 3.x: obligatoriamente llamar con seed=seed

        self.grid = MultiGrid(width, height, torus=False)
        self.running = True
        self.width = width
        self.height = height

        # Añadir palmas
        for _ in range(num_palms):
            self._place_random_agent(PalmAgent)

        # Añadir drones
        for _ in range(num_drones):
            self._place_random_agent(QuadcopterAgent)

        # Añadir personas
        for _ in range(num_people):
            self._place_random_agent(PersonAgent)

    def _place_random_agent(self, AgentClass):
        """Coloca un agente en una celda vacía aleatoria."""
        while True:
            pos = (random.randrange(self.width), random.randrange(self.height))
            if self.grid.is_cell_empty(pos):
                agent = AgentClass(self, pos)
                self.grid.place_agent(agent, pos)
                break

    def step(self):
        """Ejecuta un paso de simulación usando la nueva API de AgentSet."""
        self.agents.shuffle_do("step")

    def next_id(self):
        if not hasattr(self, "_next_id_counter"):
            self._next_id_counter = 0
        self._next_id_counter += 1
        return self._next_id_counter