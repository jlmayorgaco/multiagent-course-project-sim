# src/agents/components/Radio.py
# src/agents/components/Radio.py

class Radio:
    def __init__(self, model, agent_id=None):
        self.model = model
        self.agent_id = agent_id
        self.inbox = []

    # --- Blackboard writes ---
    def publish_blackboard_palms_target(self, position, confidence):
        """Publish or update the palm detection at a given position with confidence."""
        if "palms_targets" not in self.model.blackboard:
            self.model.blackboard["palms_targets"] = {}

        # Keep max confidence per (x, y)
        current_conf = self.model.blackboard["palms_targets"].get(position, 0.0)
        self.model.blackboard["palms_targets"][position] = max(confidence, current_conf)


    def publish_blackboard_drones_position(self, position):
        """Update this drone's current position in the blackboard."""
        if self.agent_id is not None:
            self.model.blackboard["drones_positions"][self.agent_id] = position

    # --- Blackboard reads ---
    def read_blackboard_palms_targets(self):
        """Return a list of detected palms with location and confidence."""
        raw_targets = self.model.blackboard.get("palms_targets", {})
        return [
            {"location": pos, "confidence": conf}
            for pos, conf in raw_targets.items()
        ]

    def read_blackboard_drones_positions(self):
        """Return positions of all drones."""
        return self.model.blackboard["drones_positions"]
