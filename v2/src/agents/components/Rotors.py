class Rotors:
    def __init__(self, model):
        self.model = model

    def move(self, drone, next_pos):
        if self.in_bounds(next_pos):
            self.model.grid.move_agent(drone, next_pos)
            drone.gps.set_position(*next_pos)
            drone.battery.consume(1)
        else:
            print(f"[WARNING] Drone {drone.unique_id} attempted invalid move to {next_pos}")

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height
