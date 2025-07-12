class GPS:
    def __init__(self, latitude=0.0, longitude=0.0):
        self.latitude = latitude
        self.longitude = longitude

    def get_position(self):
        return (self.latitude, self.longitude)

    def set_position(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
