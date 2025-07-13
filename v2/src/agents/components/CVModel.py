import random

class CVModel:
    def analyze(self, photo_data):
        # Simulated ML inference on the image
        # Return a dictionary with prediction info
        return {
            "infected": random.random() < 0.3,  # 30% chance of infection
            "confidence": round(random.uniform(0.6, 0.99), 2)
        }

    def get_camera_value_by_photo(self, photo_data):
        return self.analyze(photo_data)
