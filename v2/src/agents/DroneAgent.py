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
from .components.Rotors import Rotors


FSM_STATES = {

}
FSM_TRANSITIONS = {

}


class DroneAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.MIN_BATTERY_LEVEL = -1000000

        self.pos = pos
        self.next_move = pos
        self.last_pos = pos  # Used to calculate direction

        self.state = "exploring"
        self.target = None

        self.is_charging = False
        self.on_mission = False
        self.is_curing = False

        self.known_targets = []
        self.known_drones = []
        self.known_charging_stations = []

        self.detected_palms_in_photo = {} # (x,y): confianza, (1,0): 0.9

        self.radio = Radio(model, unique_id)
        self.rotors = Rotors(model)
        self.gps = GPS(*pos, model)
        self.camera = Camera(model)
        self.cv_model = CVModel(model)
        self.controller = Controller()
        self.battery = Battery(model, unique_id, 100)
        self.medicine = MedicineDispenser(model, unique_id, 100)

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

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height

    def do_input_communication(self):
        self.known_targets = self.radio.read_blackboard_palms_targets()
        self.known_drones = self.radio.read_blackboard_drones_positions()
        self.known_charging_stations = self.radio.read_blackboard_charging_stations_positions()

    def do_output_communication(self):
        self.radio.publish_blackboard_drones_position(self.gps.get_position())
        if self.detected_palms_in_photo:
            for pos, confidence in self.detected_palms_in_photo.items():
                if(confidence > 0):
                    self.radio.publish_blackboard_palms_target(pos, confidence)
                if(confidence < 0):
                    self.radio.report_palm_cured(pos, confidence)

        self.detected_palms_in_photo = {}

    def do_sensing(self):
        self.photo = self.camera.take_photo(self.pos)
        self.vision = self.cv_model.analyze(self.photo)
        self.battery_level = self.battery.get_level()
        self.medicine_level = self.medicine.get_level()
        x0 , y0 = self.pos
        self.detected_palms_in_photo = self.cv_model.convert_infected_matrix_to_dict(self.vision, x0, y0)

    def _set_exploration_path(self, position):
        self.state = "exploring"
        self.next_move = self.controller.explore(position, self.last_pos, self.known_drones)

    def do_control(self):
        position = self.gps.get_position()
        stations = self.known_charging_stations

        # If no stations are known, fallback to exploring
        if not stations:
            print(f"[WARNING] Drone {self.unique_id} found no charging stations.")
            self._set_exploration_path(position)
            return

        # Evaluate battery and medicine status
        battery_ok = self.battery.get_level() > 20
        medicine_ok = self.medicine.get_level() > 20

        # Get nearest charging station
        closest_station, _ = self.controller.get_closest_charging_station(position, stations)
        station_pos = closest_station

        # --- STATE CONTROL LOGIC ---
        if self.state == "charging":
            self.is_charging = True
            if self.battery.get_level() > 90 and self.medicine.get_level() > 90:
                self.state = "exploring"
                self.is_charging = False
            return

        if self.state == "going_to_charging_station":
            if position == station_pos:
                self.state = "charging"
            else:
                self.next_move = self.controller.move_towards(position, station_pos, self.known_drones)
            return

        if not battery_ok or not medicine_ok:
            self.state = "going_to_charging_station"
            self.next_move = self.controller.move_towards(position, station_pos, self.known_drones)
            return

        # Cure if standing on infected palm
        confidence = self.detected_palms_in_photo.get(position, 0)
        if confidence > 0.5:
            self.state = "curing"
            self.next_move = position
            return

        # Move to best known infected palm
        best_target = self.controller.choose_best_target(self.known_targets, position)
        if best_target:
            self.state = "moving_to_target"
            self.on_mission = True
            self.target = best_target
            self.next_move = self.controller.move_towards(position, best_target, self.known_drones)
        else:
            self.on_mission = False
            self._set_exploration_path(position)

    def do_action(self):
        position = self.gps.get_position()

        if self.state == "curing":
            self._perform_curing(position)

        elif self.state in ["going_to_charging_station", "moving_to_target", "exploring"]:
            if self.next_move:
                self.last_pos = position
                self.rotors.move(self, self.next_move)

        elif self.state == "charging":
            self.battery.recharge()
            self.medicine.refill()
            pass

        else:
            print(f"[WARNING] Drone {self.unique_id} attempted invalid move in state {self.state}")

    def _perform_curing(self, position):
        avg_health = self.medicine.get_sensor_palm_health(position)

        if avg_health is None:
            print(f"[DEBUG] No palm at {position}, aborting curing.")
            self.state = "exploring"
            return

        if avg_health < 100 and self.medicine.get_level() > 0:
            self.medicine.dispense(position)
            self.is_curing = True
            avg_health = self.medicine.get_sensor_palm_health(position)

            if avg_health >= PalmAgent.HEALTH_UMBRAL_MAX:
                self.radio.report_palm_cured(position)
                self.state = "exploring"
                self.is_curing = False

    def get_direction(self):
        # Compute direction vector as tuple (dx, dy)
        x1, y1 = self.last_pos
        x2, y2 = self.gps.get_position()
        return (x2 - x1, y2 - y1)
