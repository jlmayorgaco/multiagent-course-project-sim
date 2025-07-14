from mesa import Agent

class GridCellAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos  # (x, y)
        self.state = "empty"  # Can be "empty", "palm", "burned", etc.

        self._visible_by_drones_count = 0
        self._targeted_palm_by_drones_count = 0

    # --- Properties ---
    @property
    def IsVisibleByDrones(self):
        return self._visible_by_drones_count > 0

    @property
    def IsPalmTargeted(self):
        return self._targeted_palm_by_drones_count > 0

    # --- Methods to modify counters ---
    def mark_visible(self):
        self._visible_by_drones_count += 1

    def unmark_visible(self):
        self._visible_by_drones_count = max(0, self._visible_by_drones_count - 1)

    def mark_as_target(self):
        self._targeted_palm_by_drones_count += 1

    def unmark_as_target(self):
        self._targeted_palm_by_drones_count = max(0, self._targeted_palm_by_drones_count - 1)

    def reset_visibility(self):
        self._visible_by_drones_count = 0

    def reset_target(self):
        self._targeted_palm_by_drones_count = 0

    def step(self):
        pass  # Static unless you want animation or tick-based effects

    # --- Visualization in Mesa ---
    def get_portrayal(self):
        x, y = self.pos
        color = "white"
        alpha = 1.0

        if self.IsVisibleByDrones:
            color = "black"
            alpha = 0.5

        if self.IsPalmTargeted:
            color = "red"
            alpha = 0.8

        portrayal = {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "Color": color,
            "Layer": 0,
            "alpha": alpha,
            "text": f"({x},{y})",
            "text_color": "gray"
        }

        return portrayal
