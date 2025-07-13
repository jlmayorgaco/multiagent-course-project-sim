class Battery:
    def __init__(self, capacity=100):
        self.capacity = capacity  # max capacity
        self.level = capacity     # current level

    def get_level(self):
        return self.level

    def consume(self, amount):
        self.level = max(0, self.level - amount)

    def recharge(self, amount):
        self.level = min(self.capacity, self.level + amount)

    def is_low(self, threshold=20):
        return self.level <= threshold
