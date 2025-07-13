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

        self.radio = Radio(model, unique_id)
        self.gps = GPS(*pos, model)
        self.camera = Camera(model)
        self.cv_model = CVModel()
        self.controller = Controller()
        self.battery = Battery(100)
        self.medicine = MedicineDispenser(model, 100)

        self.photo = None
        self.vision = None
        self.battery_level = 100
        self.medicine_level = 100

    def step(self):
        print(f"[Drone {self.unique_id}] Step - Position: {self.pos}, State: {self.state}")
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
        if self.target:
            self.radio.publish_blackboard_palms_target({
                "location": self.target,
                "confidence": 1.0
            })

    def do_sensing(self):
        self.photo = self.camera.take_photo()
        self.vision = self.cv_model.analyze(self.photo)
        self.battery_level = self.battery.get_level()
        self.medicine_level = self.medicine.get_level()

    def do_control(self):
        position = self.gps.get_position()

        if self.battery_level < 15:
            self.state = "returning_to_charging_station"
            return

        if self.state == "exploring":
            if self.vision.get("infected", False):
                self.target = position
                self.state = "curing"
                self.next_move = None
            elif self.known_targets:
                self.target = self.controller.choose_best_target(self.known_targets, position)
                self.state = "moving_to_target"
            else:
                self.next_move = self.controller.explore(position, self.known_drones)

        elif self.state == "curing":
            self.next_move = None

        elif self.state == "moving_to_target":
            if position == self.target:
                self.state = "curing"
                self.next_move = None
            else:
                self.next_move = self.controller.move_towards(position, self.target, self.known_drones)

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
