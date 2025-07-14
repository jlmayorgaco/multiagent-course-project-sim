from mesa import Agent

class GridCellAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self._initial_pos = pos  # Optional for debugging  # Internally store pos only once during initialization
        self.state = "empty"  # Could be "empty", "palm", "burned", etc.

        self._visible_by_drones_count = 0
        self._targeted_palm_by_drones_count = 0

    @property
    def IsVisibleByDrones(self):
        return self._visible_by_drones_count > 0

    @property
    def IsPalmTargeted(self):
        return self._targeted_palm_by_drones_count > 0

    # --- Methods to modify visibility and target counters ---
    def mark_visible(self):
        self._visible_by_drones_count += 1
        print(f"[DEBUG] → Cell at {self.pos} now visible by {self._visible_by_drones_count} drone(s)")

    def unmark_visible(self):
        self._visible_by_drones_count = max(0, self._visible_by_drones_count - 1)

    def reset_visibility(self):
        if self._visible_by_drones_count > 0:
            print(f"[DEBUG] → Resetting visibility for cell at {self.pos}")
        self._visible_by_drones_count = 0

    def mark_as_target(self):
        self._targeted_palm_by_drones_count += 1
        print(f"[DEBUG] → Cell at {self.pos} marked as a target")

    def unmark_as_target(self):
        self._targeted_palm_by_drones_count = max(0, self._targeted_palm_by_drones_count - 1)

    def reset_target(self):
        if self._targeted_palm_by_drones_count > 0:
            print(f"[DEBUG] → Resetting target for cell at {self.pos}")
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
