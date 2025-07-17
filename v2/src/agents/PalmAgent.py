# --------------------------------------------------------- #
# --- Imports --------------------------------------------- #
# --------------------------------------------------------- #
import random
from mesa import Agent
# --------------------------------------------------------- #

# --------------------------------------------------------- #
# --- Agent : PalmAgent.py -------------------------------- #
# --------------------------------------------------------- #
# Description:
# Represents a palm tree in the simulation. It can transition
# between healthy, infected, and dead states depending on 
# its neighbors and internal health level. It can also randomly
# auto-infect after being cured, simulating environmental risks.
#
# Attributes:
# - pos (tuple): grid position
# - estado (str): "verde", "infectada", or "muerta"
# - health_level (float): remaining health (0–100)
#
# Methods:
# - step(): determines infection and health degradation
# - apply_medicine(): adds health and adjusts state
# --------------------------------------------------------- #

class PalmAgent(Agent):
    """
    PalmAgent represents a palm tree in the simulation grid.

    The agent can be in one of three states:
    - "verde": healthy
    - "infectada": infected and degrading in health
    - "muerta": dead

    It interacts with its neighbors to potentially get infected and
    degrades health over time if infected. If health drops to zero, it dies.
    It can also become auto-infected based on probability.
    """

    # Constants
    HEALTH_UMBRAL_MAX = 95
    HEALTH_UMBRAL_MIN = 5
    INFECTED_HEALTH_RATE = 1
    AUTO_INFECTED_PROBABILITY = 0.01 # 1% chance per step

    def __init__(self, unique_id, model, pos, estado="verde"):
        super().__init__(unique_id, model)

        # State
        self.pos = pos                     # Tuple (x, y)
        self.estado = estado              # 'verde', 'infectada', 'muerta'
        self.health_level = 100           # Range: 0–100

    def step(self):
        """Update palm health and infection state."""
        if self.estado == "verde":
            infected_by_neighbors = self._try_infection()

            if not infected_by_neighbors:
                self._maybe_auto_infect()

        elif self.estado == "infectada":
            self._degrade_health()
            self._check_death()

    def _try_infection(self):
        """Try to get infected based on neighboring palms."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, PalmAgent) and neighbor.estado == "infectada":
                if random.random() < self.model.tasa_propagacion:
                    self.estado = "infectada"
                    return True
        return False

    def _maybe_auto_infect(self):
        """Apply a small chance of random infection even without infected neighbors."""
        if random.random() < self.AUTO_INFECTED_PROBABILITY:
            self.estado = "infectada"
            print(f"[AUTO-INFECTED] Palm at {self.pos} became infected randomly.")

    def _degrade_health(self):
        """Reduce health level with some randomness."""
        variation = self.INFECTED_HEALTH_RATE * (random.random() - random.random())
        self.health_level -= self.INFECTED_HEALTH_RATE + variation

    def _check_death(self):
        """If health drops below threshold, mark as dead."""
        if self.health_level <= self.HEALTH_UMBRAL_MIN:
            self.health_level = self.HEALTH_UMBRAL_MIN
            self.estado = "muerta"

    def apply_medicine(self, amount):
        """
        Increases the palm's health by a specified amount and updates its state.

        Parameters:
        - amount (float): The amount of healing applied to this palm.
        """
        if self.estado == "infectada":
            self.health_level += amount

            # Clamp the health level between 0 and 100
            self.health_level = min(max(self.health_level, 0), 100)

            if self.health_level > self.HEALTH_UMBRAL_MAX:
                self.estado = "verde"
                self.health_level = 100

            elif self.health_level <= self.HEALTH_UMBRAL_MIN:
                self.health_level = 0
                self.estado = "muerta"
