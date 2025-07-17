# src/agents/components/Radio.py

class Radio:
    def __init__(self, model, agent_id=None):
        self.model = model
        self.agent_id = agent_id
        self.inbox = []

    # --- Blackboard writes ---
    def publish_blackboard_palms_target(self, position, confidence):
        self.model.update_blackboard_palms_targets(position, confidence)

    def publish_blackboard_drones_position(self, position):
        if self.agent_id is not None:
            self.model.update_blackboard_drone_positions(self.agent_id, position)

    # --- Blackboard reads (now via model) ---
    def read_blackboard_charging_stations_positions(self):
        return self.model.get_blackboard_charging_stations_positions()
    
    def read_blackboard_palms_targets(self):
        return self.model.get_blackboard_palms_targets()

    def read_blackboard_drones_positions(self):
        return self.model.get_blackboard_drones_positions()

    def report_palm_cured(self, position, confidence = 0):
        self.model.report_palm_cured(position, confidence)