from mesa.visualization.modules import TextElement

# Direction emoji map
DIRECTION_EMOJI = {
    (-1, 0): "←", (1, 0): "→",
    (0, -1): "↓", (0, 1): "↑",
    (-1, -1): "↙", (1, -1): "↘",
    (-1, 1): "↖", (1, 1): "↗",
    (1, 1): "↗", (0, 0): "•"
}

class BlackboardText(TextElement):
    def render(self, model):
        # --- 🟫 Infected Palm Targets Table ---
        targets = model.blackboard.get("palms_targets", {})
        target_rows = ""
        for i, (pos, confidence) in enumerate(targets.items()):
            # Try to get state and health
            estado, health = "?", None
            for agent in model.grid.get_cell_list_contents([pos]):
                if hasattr(agent, "estado"):
                    estado = agent.estado
                    health = getattr(agent, "health_level", None)
                    break
            health_str = f"{health:.0f}%" if health is not None else "?"
            target_rows += f"<tr><td>{i+1}</td><td>{pos}</td><td>{confidence:.2f}</td><td>{estado}</td><td>{health_str}</td></tr>"

        target_table = f"""
        <br>
        <br>
        <h4>🟫 Infected Palm Targets</h4>
        <table border="1" cellpadding="3" cellspacing="0">
            <thead>
                <tr><th>#</th><th>Position</th><th>Confidence</th><th>Status</th><th>Health</th></tr>
            </thead>
            <tbody>
                {target_rows if target_rows else '<tr><td colspan="5">None</td></tr>'}
            </tbody>
        </table>
        """

        # --- 📍 Drone Info Table ---
        drones = model.blackboard.get("drones_positions", {})
        drone_rows = ""
        for drone_id, position in drones.items():
            agent = next(
                (a for a in model.grid.get_cell_list_contents([position])
                 if hasattr(a, "state") and a.unique_id == drone_id),
                None
            )
            if agent:
                # Direction emoji
                next_pos = getattr(agent, "next_move", position)
                dx = next_pos[0] - position[0]
                dy = next_pos[1] - position[1]
                direction = DIRECTION_EMOJI.get((dx, dy), "•")

                # Info
                state = getattr(agent, "state", "?")
                target = getattr(agent, "target", "–")
                battery = getattr(agent, "battery_level", "?")
                med = agent.medicine.get_level() if hasattr(agent, "medicine") else "?"

                drone_rows += f"<tr><td>{drone_id}</td><td>{position}</td><td>{direction}</td><td>{state}</td><td>{target}</td><td>{battery}%</td><td>{med}</td></tr>"
            else:
                drone_rows += f"<tr><td>{drone_id}</td><td>{position}</td><td colspan='5'>info unavailable</td></tr>"

        drone_table = f"""
        <h4>📍 Drone Status</h4>
        <table border="1" cellpadding="3" cellspacing="0">
            <thead>
                <tr><th>ID</th><th>Position</th><th>Dir</th><th>State</th><th>Target</th><th>🔋</th><th>💊</th></tr>
            </thead>
            <tbody>
                {drone_rows if drone_rows else '<tr><td colspan="7">None</td></tr>'}
            </tbody>
        </table>
        """

        # Combine both tables
        return target_table + "<br>" + drone_table
