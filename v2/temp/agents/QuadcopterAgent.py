from mesa import Agent
import random

class QuadcopterAgent(Agent):
    """
    A drone that moves through the forest to detect diseased palm trees.
    """

    def __init__(self, model, pos, vision_range=1):
        super().__init__(model)
        self.unique_id = self.model.next_id()
        self.pos = pos
        self.vision_range = vision_range
        self.detected = []  # List of positions of detected diseased palms

    def step(self):
        """
        The drone scans for diseased palms in its vision range, stores them, and moves randomly.
        """
        self.scan_surroundings()
        self.move_randomly()

    def scan_surroundings(self):
        """
        Look for diseased palms within vision_range and record their positions.
        """
        x, y = self.pos
        for dx in range(-self.vision_range, self.vision_range + 1):
            for dy in range(-self.vision_range, self.vision_range + 1):
                nx, ny = x + dx, y + dy
                if not self.model.grid.out_of_bounds((nx, ny)):
                    neighbors = self.model.grid.get_cell_list_contents((nx, ny))
                    for agent in neighbors:
                        if hasattr(agent, "is_diseased") and agent.is_diseased():
                            if (nx, ny) not in self.detected:
                                self.detected.append((nx, ny))

    def move_randomly(self):
        """
        Move to a random neighboring empty cell.
        """
        possible_moves = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        valid_moves = [pos for pos in possible_moves if self.model.grid.is_cell_empty(pos)]
        if valid_moves:
            new_position = random.choice(valid_moves)
            self.model.grid.move_agent(self, new_position)
            self.pos = new_position
