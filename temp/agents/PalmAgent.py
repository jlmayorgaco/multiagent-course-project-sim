from mesa import Agent

class PalmAgent(Agent):
    """
    A PalmAgent represents a wax palm in the forest grid.
    States: natural, diseased, burned, empty
    """

    def __init__(self, model, pos, state="natural"):
        super().__init__(model)
        self.unique_id = self.model.next_id()
        self.pos = pos
        self.state = state

    def step(self):
        """
        Palms are passive unless disease spread or fire is simulated.
        """
        pass

    # --- State Query Methods ---
    def is_natural(self):
        return self.state == "natural"

    def is_diseased(self):
        return self.state == "diseased"

    def is_burned(self):
        return self.state == "burned"

    def is_empty(self):
        return self.state == "empty"

    # --- State Setter Methods ---
    def set_natural(self):
        self.state = "natural"

    def set_diseased(self):
        self.state = "diseased"

    def set_burned(self):
        self.state = "burned"

    def set_empty(self):
        self.state = "empty"
