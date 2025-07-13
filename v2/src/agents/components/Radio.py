# src/agents/components/Radio.py
# src/agents/components/Radio.py

class Radio:
    def __init__(self, model, agent_id=None):
        self.model = model
        self.agent_id = agent_id
        self.inbox = []

    # --- Blackboard writes ---
    def publish_blackboard_palms_target(self, target_info):
        """Publish a palm detection target to the blackboard."""
        self.model.blackboard["palms_targets"].append(target_info)

    def publish_blackboard_drones_position(self, position):
        """Update this drone's current position in the blackboard."""
        if self.agent_id is not None:
            self.model.blackboard["drones_positions"][self.agent_id] = position

    # --- Blackboard reads ---
    def read_blackboard_palms_targets(self):
        """Return all palm targets from blackboard."""
        return self.model.blackboard["palms_targets"]

    def read_blackboard_drones_positions(self):
        """Return positions of all drones."""
        return self.model.blackboard["drones_positions"]
