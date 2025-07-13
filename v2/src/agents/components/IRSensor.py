import random

class IRSensor:
    def __init__(self, threshold=5.0):
        self.threshold = threshold

    def get_value(self):
        # Simulated sensor value (e.g., distance in meters)
        return round(random.uniform(0.0, 10.0), 2)

    def is_obstacle_detected(self):
        return self.get_value() < self.threshold
