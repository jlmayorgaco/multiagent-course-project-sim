from mesa import Agent
import random

class PersonAgent(Agent):
    """
    A PersonAgent represents a human worker that moves through the grid
    to inspect or treat diseased palm trees reported by drones.
    """

    def __init__(self, model, pos):
        super().__init__(model)
        self.unique_id = self.model.next_id()
        self.pos = pos
        self.targets = []  # List of target palm positions to visit

    def step(self):
        """
        If there are targets, move toward the closest one. If on it, treat it.
        """
        if self.targets:
            self.move_toward_target()
            self.treat_palm()

    def add_target(self, position):
        """
        Add a palm position to the list of locations this worker should visit.
        """
        if position not in self.targets:
            self.targets.append(position)

    def move_toward_target(self):
        """
        Move one step toward the nearest target palm (Manhattan distance).
        """
        if not self.targets:
            return

        target = self.targets[0]
        x, y = self.pos
        tx, ty = target

        dx = tx - x
        dy = ty - y
        new_x = x + (1 if dx > 0 else -1 if dx < 0 else 0)
        new_y = y + (1 if dy > 0 else -1 if dy < 0 else 0)

        new_pos = (new_x, new_y)
        if self.model.grid.is_cell_empty(new_pos) or new_pos == target:
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos

    def treat_palm(self):
        """
        If standing on a target and it's a diseased palm, treat it.
        """
        if not self.targets:
            return

        if self.pos == self.targets[0]:
            agents_here = self.model.grid.get_cell_list_contents([self.pos])
            for agent in agents_here:
                if hasattr(agent, "is_diseased") and agent.is_diseased():
                    agent.set_natural()
                    print(f"Person {self.unique_id} treated palm at {self.pos}")
                    break
            self.targets.pop(0)
