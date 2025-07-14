from mesa.visualization.modules import TextElement

class BlackboardText(TextElement):
    def render(self, model):
        # Retrieve blackboard data
        targets = model.blackboard.get("palms_targets", {})
        drones = model.blackboard.get("drones_positions", {})

        # Infected Palm Targets
        target_lines = ["<b>🟫 Infected Palm Targets</b>"]
        if targets:
            for i, (location_str, confidence) in enumerate(targets.items()):
                target_lines.append(f"{i+1}. {location_str} (conf: {confidence:.2f})")
        else:
            target_lines.append("None")

        # Drone Positions
        drone_lines = ["<br><b>📍 Drone Positions</b>"]
        if drones:
            for drone_id, position in drones.items():
                drone_lines.append(f"Drone {drone_id}: {position}")
        else:
            drone_lines.append("None")

        # Combine output
        return "<br>".join(target_lines + drone_lines)
