# src/agents/components/Controller.py
import random

class Controller:
    def __init__(self):
        pass

    def choose_best_target(self, targets, current_pos):
        """
        Choose the closest infected palm (or highest confidence) as target.
        """
        if not targets:
            return None

        # Sort by Manhattan distance from current position
        sorted_targets = sorted(
            targets,
            key=lambda t: self.manhattan_distance(current_pos, t["location"])
        )
        return sorted_targets[0]["location"]

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
