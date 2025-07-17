# src/agents/components/Controller.py
import random


# Drone Finite State Machine (FSM) States
State_S0_INIT                       = "init"                           # Inicio del agente
State_S1_IDLE                       = "idle"                           # En espera, sin tareas
State_S2_EXPLORING                  = "exploring"                      # Exploración aleatoria
State_S3_MOVING_TO_TARGET           = "moving_to_target"              # Moviéndose hacia una palma infectada conocida
State_S4_CURING                     = "curing"                         # Dispensando medicina en palma enferma
State_S5_GOING_TO_CHARGING_STATION  = "going_to_charging_station"     # Dirigiéndose a estación de carga
State_S6_CHARGING                   = "charging"                       # Cargando batería y medicina
State_S7_EMERGENCY_RETURN           = "emergency_return"              # Retorno forzoso por batería crítica (opcional)
State_S8_DEATH                      = "death"                          # Fin del ciclo del dron (sin batería/daño/etc.)



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


    def explore(self, current_pos, last_pos, known_drones):
        """
        Picks the next exploration move:
        - 70% chance to continue in the same direction as the last move
        - 30% chance to pick a random direction
        - Avoids collision with known drones
        """
        possible_moves = self.get_neighborhood(current_pos)
        safe_moves = [
            move for move in possible_moves
            if move not in known_drones.values()
        ]

        # Case: no safe moves → stay in place
        if not safe_moves:
            return current_pos

        # Case: no previous move → choose random safe move
        if last_pos is None:
            return random.choice(safe_moves)

        # Compute preferred direction (current - last)
        dx = current_pos[0] - last_pos[0]
        dy = current_pos[1] - last_pos[1]
        preferred_move = (current_pos[0] + dx, current_pos[1] + dy)

        # 70% chance to try to continue in the same direction
        if random.random() < 0.7 and preferred_move in safe_moves:
            return preferred_move

        # Otherwise, pick random safe move
        return random.choice(safe_moves)


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
    
    def go_to_target(self, current_pos, targets, known_drones=None):
        """
        High-level navigation logic:
        - Select the best target using choose_best_target
        - Move one step toward that target using move_towards
        - Avoid collisions with known drones
        """
        if known_drones is None:
            known_drones = {}

        target_pos = self.choose_best_target(targets, current_pos)
        if target_pos is None:
            return current_pos  # No target found, stay in place

        return self.move_towards(current_pos, target_pos, known_drones)

    def get_closest_charging_station(self, position, charging_stations_dict):
        """
        Given a drone position and a dict of charging station positions (as keys),
        returns the closest charging station position and its Manhattan distance.
        
        Parameters:
        - position: tuple(int, int) — current drone position
        - charging_stations_dict: dict — {(x, y): drone_id or status}
        
        Returns:
        - closest_station_pos: tuple(int, int)
        - min_distance: int
        """
        min_distance = float("inf")
        closest_station_pos = None

        for station_pos in charging_stations_dict.keys():
            dist = abs(position[0] - station_pos[0]) + abs(position[1] - station_pos[1])
            if dist < min_distance:
                min_distance = dist
                closest_station_pos = station_pos

        return closest_station_pos, min_distance

