from mesa import Agent

class ChargingStationAgent(Agent):
    """
    ChargingStationAgent represents a static recharging station
    placed at the edge of the grid. Each drone is assigned to a
    unique charging station.

    Attributes:
    - pos (tuple): grid position
    - assigned_drone_id (int): the drone ID this station serves (optional)
    """

    def __init__(self, unique_id, model, pos, assigned_drone_id=None):
        super().__init__(unique_id, model)
        self.pos = pos
        self.assigned_drone_id = assigned_drone_id

    def step(self):
        # Charging stations are static and do not act during the simulation step
        pass
