# src/agents/components/Controller.py
import random

class Controller:
    def __init__(self):
        pass

    def choose_best_target(self, targets, current_pos):
        """
        Choose the closest infected palm (or highest confidence) as target.
        Assumes targets is a list of dicts: [{"location": (x, y), "confidence": float}]
        """
        print("\n--- choose_best_target DEBUG ---")
        print(f"[Input] Current drone position: {current_pos}")
        print(f"[Input] Targets (raw): {targets}")

        if not targets:
            print("[Info] No targets provided. Returning None.")
            return None

        try:
            # Normalize the location field (convert strings to tuples)
            normalized_targets = []
            for t in targets:
                loc = t["location"]
                if isinstance(loc, str):
                    try:
                        loc = eval(loc)
                    except Exception as e:
                        print(f"[Error] Could not parse location string: {loc}, error: {e}")
                        continue
                normalized_targets.append({
                    "location": loc,
                    "confidence": t["confidence"]
                })

            # Sort by Manhattan distance
            sorted_targets = sorted(
                normalized_targets,
                key=lambda t: self.manhattan_distance(current_pos, t["location"])
            )

            print("[Debug] Sorted targets by distance:")
            for i, t in enumerate(sorted_targets):
                dist = self.manhattan_distance(current_pos, t["location"])
                print(f"  {i+1}. Location: {t['location']}, Confidence: {t['confidence']:.4f}, Distance: {dist}")

            selected = sorted_targets[0]["location"]
            print(f"[Output] Selected target: {selected}")
            print("--- END choose_best_target DEBUG ---\n")
            return selected

        except Exception as e:
            print("[Fatal Error] Exception while choosing best target:", str(e))
            return None




    def explore(self, current_pos, known_drones):
        """
        Randomly pick a safe nearby position to explore (avoid collisions).
        """
        possible_moves = self.get_neighborhood(current_pos)
        safe_moves = [
            move for move in possible_moves
            if move not in known_drones.values()  # avoid collision
        ]
        return random.choice(safe_moves) if safe_moves else current_pos

    def move_towards(self, current, goal, known_drones):
        """
        Move one step toward goal, avoiding other drones.
        """
        dx = goal[0] - current[0]
        dy = goal[1] - current[1]

        step_x = current[0] + (1 if dx > 0 else -1 if dx < 0 else 0)
        step_y = current[1] + (1 if dy > 0 else -1 if dy < 0 else 0)

        next_pos = (step_x, step_y)

        # Avoid collision if possible
        if next_pos in known_drones.values():
            alternatives = self.get_neighborhood(current)
            for alt in alternatives:
                if alt not in known_drones.values():
                    return alt
            return current  # stay if blocked

        return next_pos

    def get_nearest_station(self, current_pos):
        """
        Returns the hardcoded location of the nearest charging station.
        For now, assume (0, 0) is always the station.
        """
        return (0, 0)

    def get_neighborhood(self, pos):
        """
        Return Moore neighborhood (8 adjacent cells).
        """
        x, y = pos
        return [
            (x + dx, y + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]

    def manhattan_distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
