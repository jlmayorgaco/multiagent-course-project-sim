import random
from mesa import Agent

# Imports Classes
from .PalmAgent import PalmAgent
from .components.GPS import GPS
from .components.Radio import Radio
from .components.Battery import Battery
from .components.Camera import Camera
from .components.Controller import Controller
from .components.MedicineDispenser import MedicineDispenser
from .components.CVModel import CVModel

class DroneAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)

        self.pos = pos
        self.next_move = pos
        self.last_pos = pos  # Used to calculate direction

        self.state = "exploring"
        self.target = None

        self.known_targets = []
        self.known_drones = []

        self.detected_palms_in_photo = {} # (x,y): confianza, (1,0): 0.9

        self.radio = Radio(model, unique_id)
        self.gps = GPS(*pos, model)
        self.camera = Camera(model)
        self.cv_model = CVModel(model)
        self.controller = Controller()
        self.battery = Battery(100)
        self.medicine = MedicineDispenser(model, 100)

        self.photo = None
        self.vision = None
        self.battery_level = 100
        self.medicine_level = 100

    def step(self):
        #print(f"[Drone {self.unique_id}] Step - Position: {self.pos}, State: {self.state}")
        self.do_input_communication()
        self.do_sensing()
        self.do_control()
        self.do_action()
        self.do_output_communication()

    def do_input_communication(self):
        self.known_targets = self.radio.read_blackboard_palms_targets()
        self.known_drones = self.radio.read_blackboard_drones_positions()

    def do_output_communication(self):
        self.radio.publish_blackboard_drones_position(self.gps.get_position())
        # Only if the drone saw some palms
        if self.detected_palms_in_photo:
            for pos, confidence in self.detected_palms_in_photo.items():
                self.radio.publish_blackboard_palms_target(pos, confidence)
        self.detected_palms_in_photo = {}

    def do_sensing(self):

        print(' ====> [0/4] Sensing position')
        print(self.pos)

        self.photo = self.camera.take_photo(self.pos)
        print(' ====> [1/4] Sensing taking photo')
        print(self.photo)

        self.vision = self.cv_model.analyze(self.photo)
        self.battery_level = self.battery.get_level()
        self.medicine_level = self.medicine.get_level()
        
        x0 , y0 = self.pos
        self.detected_palms_in_photo = self.cv_model.convert_infected_matrix_to_dict(self.vision, x0, y0)
        print(' ====> [2/4] Sensing analizing photo')
        print(self.detected_palms_in_photo)


    def do_control(self):
        position = self.gps.get_position()
        pos_str = str(position)

        # Safety condition: return to charging station
        if self.battery_level < 15:
            self.state = "returning_to_charging_station"
            return

        # --- State: Exploring ---
        if self.state == "exploring":
            print('\n# --- State: Exploring ---')
            print('Detected palms in photo:', self.detected_palms_in_photo)

            # Case 1: Current position is infected → cure here
            if pos_str in self.detected_palms_in_photo:
                print(f"[{self.unique_id}] Detected infected palm at current position {pos_str}. Switching to curing.")
                self.target = position
                self.state = "curing"
                self.next_move = self.last_pos if hasattr(self, 'last_pos') else None

            # Case 2: Choose closest infected palm from detected photo
            elif self.detected_palms_in_photo:
                # Convert string keys to tuple for distance calculation
                detected_tuples = [eval(k) for k in self.detected_palms_in_photo.keys()]
                closest = min(detected_tuples, key=lambda p: self.controller.manhattan_distance(position, p))
                print(f"[{self.unique_id}] Moving to new infected palm at {closest}")
                self.target = closest
                self.state = "moving_to_target"
                self.next_move = self.controller.move_towards(position, self.target, self.known_drones)

            # Case 3: Use shared known targets if available
            elif self.known_targets:
                self.target = self.controller.choose_best_target(self.known_targets, position)
                self.state = "moving_to_target"
                self.next_move = self.controller.move_towards(position, self.target, self.known_drones)

            # Case 4: Explore
            else:
                print(f"[{self.unique_id}] No targets, exploring...")
                self.next_move = self.controller.explore(position, self.known_drones)

        # --- State: Curing ---
        elif self.state == "curing":
            self.next_move = self.pos  # Stay in place

        # --- State: Moving to Target ---
        elif self.state == "moving_to_target":
            if position == self.target:
                self.state = "curing"
                self.next_move = self.last_pos if hasattr(self, 'last_pos') else None
            else:
                self.next_move = self.controller.move_towards(position, self.target, self.known_drones)

        # --- State: Returning to Charging Station ---
        elif self.state == "returning_to_charging_station":
            station = self.controller.get_nearest_station(position)
            self.next_move = self.controller.move_towards(position, station, self.known_drones)



    def do_action(self):
        if self.state == "curing":
            position = self.gps.get_position()
            self.medicine.dispense(position)

        elif self.next_move:
            self.last_pos = self.gps.get_position()  # Save previous position for direction
            self.model.grid.move_agent(self, self.next_move)
            self.gps.set_position(*self.next_move)
            self.battery.consume(1)

    def get_direction(self):
        # Compute direction vector as tuple (dx, dy)
        x1, y1 = self.last_pos
        x2, y2 = self.gps.get_position()
        return (x2 - x1, y2 - y1)
