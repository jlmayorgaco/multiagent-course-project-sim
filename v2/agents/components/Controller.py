class Controller:
    def get_affected_palms(self, cam_analysis, position):
        # Dummy: return fake coordinates if "infected" detected
        if cam_analysis.get("infected", False):
            return [position]
        return []

    def build_message(self, detected_coords, position):
        return {
            "type": "alert",
            "infected_coords": detected_coords,
            "origin": position
        }

    def plan_path(self):
        # Placeholder path planning algorithm
        return ["N", "N", "E", "E", "S"]

    def execute_actions(self):
        # Placeholder for motor/actuator logic
        pass
