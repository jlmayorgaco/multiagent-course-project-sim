# src/agents/components/MedicineDispenser.py

class MedicineDispenser:
    def __init__(self, model, capacity=100):
        self.model = model
        self.capacity = capacity
        self.level = capacity

    def dispense(self, position, amount=10):
        """
        Attempts to cure an infected palm at the given position.
        If successful, reduces internal medicine level and updates the palm state.
        """
        if self.level < amount:
            return False  # Not enough medicine

        # Get all agents at the same position
        agents = self.model.grid.get_cell_list_contents([position])
        for agent in agents:
            if hasattr(agent, 'estado') and agent.estado == "infectada":
                agent.estado = "verde"
                self.level -= amount
                return True

        return False  # No infected palm found at position

    def refill(self):
        self.level = self.capacity

    def get_level(self):
        return self.level
