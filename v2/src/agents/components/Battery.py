class Battery:
    def __init__(self, model,  drone_id, capacity=100):
        self.drone_id = drone_id
        self.model = model
        self.capacity = capacity  # max capacity
        self.level = capacity     # current level


    def get_level(self):
        return self.level

    def consume(self, amount):
        self.level = max(0, self.level - amount)

    def recharge(self, amount = 33):
        # if drone by drone_id is in position over some of the stations. then recharge, if not not.
        self.level = min(self.capacity, self.level + amount)

    def is_low(self, threshold=20):
        return self.level <= threshold
