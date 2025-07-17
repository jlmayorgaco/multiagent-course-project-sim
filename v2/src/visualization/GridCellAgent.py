from mesa import Agent
import random

class GridCellAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self._initial_pos = pos
        self.state = "empty"

        # --- Type assignment ---
        self._type = self._assign_type()

        # --- Drone tracking ---
        self._visible_by_drones_count = 0
        self._targeted_palm_by_drones_count = 0

    def _assign_type(self):
        if random.random() < 0.95:
            return 0
        else:
            if random.random() < 0.95:
                return random.randint(0, 5)
            else :
                return random.randint(6, 7)
    
    @property
    def cell_type(self):
        return self._type

    @property
    def can_have_palm(self):
        return self._type == 0

    @property
    def IsVisibleByDrones(self):
        return self._visible_by_drones_count > 0

    @property
    def IsPalmTargeted(self):
        return self._targeted_palm_by_drones_count > 0

    # --- Methods to modify visibility and target counters ---
    def mark_visible(self):
        self._visible_by_drones_count += 1

    def unmark_visible(self):
        self._visible_by_drones_count = max(0, self._visible_by_drones_count - 1)

    def reset_visibility(self):
        self._visible_by_drones_count = 0

    def mark_as_target(self):
        self._targeted_palm_by_drones_count += 1

    def unmark_as_target(self):
        self._targeted_palm_by_drones_count = max(0, self._targeted_palm_by_drones_count - 1)

    def reset_target(self):
        self._targeted_palm_by_drones_count = 0

    # --- Debug and Visualization Helpers ---
    def get_status_char(self, drone_positions):
        if self.pos in drone_positions.values():
            return "D"
        elif self.IsVisibleByDrones:
            return "V"
        else:
            return "."

    def __repr__(self):
        return (f"<GridCellAgent at {self.pos}, state={self.state}, "
                f"visible={self.IsVisibleByDrones}, targeted={self.IsPalmTargeted}>")

    def step(self):
        # Static behavior unless extended for animation or dynamic simulation
        pass
