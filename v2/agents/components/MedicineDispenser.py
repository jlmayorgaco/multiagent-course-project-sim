class MedicineDispenser:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.level = capacity

    def dispense(self, amount=10):
        if self.level >= amount:
            self.level -= amount
            return True
        return False

    def refill(self):
        self.level = self.capacity

    def get_level(self):
        return self.level
