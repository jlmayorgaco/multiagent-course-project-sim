
class GPS:
    def __init__(self, x, y, model):
        self.x = x
        self.y = y
        self.model = model
        self.last_vision_area = set()

    def get_position(self):
        return (self.x, self.y)

    def set_position(self, x, y):
        self.x = x
        self.y = y