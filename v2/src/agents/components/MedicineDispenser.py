# src/agents/components/MedicineDispenser.py
# --------------------------------------------------------- #
# --- Component : MedicineDispenser.py -------------------- #
# --------------------------------------------------------- #
# Description:
# A component used to dispense medicine to infected palm trees.
#
# Attributes:
# - model: reference to the simulation model
# - capacity: total medicine capacity
# - level: current available medicine
#
# Methods:
# - dispense(position, amount): apply medicine to a palm agent
# - refill(): restore medicine to full capacity
# - get_level(): return current level
# - get_sensor_palm_health(position): return average palm health at position
# --------------------------------------------------------- #

from src.agents.PalmAgent import PalmAgent

class MedicineDispenser:
    """
    MedicineDispenser is a utility component used in the simulation
    to treat infected PalmAgents by dispensing a limited resource (medicine).

    It interacts with the grid to:
    - Apply healing to infected palms at a specific position
    - Track internal medicine usage and capacity
    - Provide sensing capability for average palm health at a location

    Attributes:
    - model: Reference to the simulation model
    - capacity (int): Maximum capacity of medicine
    - level (int): Current available medicine

    Methods:
    - dispense(position, amount): Attempts to treat infected palm
    - refill(): Refills medicine to max capacity
    - get_level(): Returns current level
    - get_sensor_palm_health(position): Reports average health at given grid cell
    """
    def __init__(self, model, unique_id, capacity=100):
        self.drone_id = unique_id
        self.model = model              # Model reference (used to access the grid)
        self.capacity = capacity        # Max storage of medicine
        self.level = capacity           # Current available medicine

    def dispense(self, position, amount=5):
        """
        Attempts to treat an infected palm at the given position.
        Reduces the medicine level if successful.
        """
        if self.level < amount:
            return False  # Not enough medicine

        agents = self.model.grid.get_cell_list_contents([position])
        for agent in agents:
            if isinstance(agent, PalmAgent) and agent.estado == "infectada":
                agent.apply_medicine(amount)
                self.level -= amount
                return True

        return False  # No infected palm found at position

    def refill(self):
        """Refill the dispenser to full capacity."""
        self.level = self.capacity

    def get_level(self):
        """Return the current medicine level."""
        return self.level
    
    def get_sensor_palm_health(self, position):
        """
        Returns the average health level of all palms at a given position.
        If no palms are found, returns None.
        """
        agents = self.model.grid.get_cell_list_contents([position])
        health_values = [
            agent.health_level for agent in agents
            if isinstance(agent, PalmAgent)
        ]

        return sum(health_values) / len(health_values) if health_values else None
