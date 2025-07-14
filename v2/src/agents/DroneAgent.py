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


class DroneAgent(Agent):
    def __init__(self, unique_id, model, pos):
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
        self.rotors = Rotors(model)
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

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height

    def do_input_communication(self):
        self.known_targets = self.radio.read_blackboard_palms_targets()
        self.known_drones = self.radio.read_blackboard_drones_positions()

    def do_output_communication(self):
        self.radio.publish_blackboard_drones_position(self.gps.get_position())
        if self.detected_palms_in_photo:
            for pos, confidence in self.detected_palms_in_photo.items():
                self.radio.publish_blackboard_palms_target(pos, confidence)
        self.detected_palms_in_photo = {}

    def do_sensing(self):
        self.photo = self.camera.take_photo(self.pos)
        self.vision = self.cv_model.analyze(self.photo)
        self.battery_level = self.battery.get_level()
        self.medicine_level = self.medicine.get_level()
        x0 , y0 = self.pos
        self.detected_palms_in_photo = self.cv_model.convert_infected_matrix_to_dict(self.vision, x0, y0)

    def do_control(self):
        position = self.gps.get_position()
        self.state = "exploring"
        self.next_move = self.controller.explore(position, self.known_drones)


    def do_action(self):
        if self.state == "curing":
            position = self.gps.get_position()
            self.medicine.dispense(position)

        elif self.next_move:
            self.last_pos = self.gps.get_position()
            self.rotors.move(self, self.next_move)
        else:
            # Optionally log or handle the invalid move
            print(f"[WARNING] Drone {self.unique_id} attempted invalid move to {self.next_move}")
    
    def get_direction(self):
        # Compute direction vector as tuple (dx, dy)
        x1, y1 = self.last_pos
        x2, y2 = self.gps.get_position()
        return (x2 - x1, y2 - y1)
