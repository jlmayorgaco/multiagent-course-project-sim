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

# Comunicacion con vecinos
# Registro de zonas con palmas, zonas con palmans afectadas
# Bateria
# Inicio fijo
# Sensores: 1. Vision de Radio RVd 2. Sensor de Proximidad 3.Sensor de Bateria
# Algortimos: 
#     1. Algorimo de busquea: Buscar Palmeras infectadas.
#     2. Push para Notificar la ubicacion de la palma
#     3. Una vez marcada, el sigue con otra ruta hasta que se acabe la bateria.
#     4. Regresar antes de que se acabe la bateria


class DroneAgent1(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Intentar curar palmeras infectadas cercanas
        vecinos = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for vecino in vecinos:
            if isinstance(vecino, PalmAgent) and vecino.estado == "infectada":
                if random.random() < self.model.tasa_cura:
                    vecino.estado = "verde"

        # Moverse a una celda vecina aleatoria
        posibles_movimientos = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        nueva_pos = random.choice(posibles_movimientos)
        self.model.grid.move_agent(self, nueva_pos)






class DroneAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)

        # Position attributes
        self.pos = pos
        self.next_move = pos  # Next move decided by controller

        # Drone operational state (Finite State Machine)
        self.state = "exploring"  # States: exploring, curing, moving_to_target, returning_to_charging_station

        # Target (infected palm location)
        self.target = None

        # Known information from other agents
        self.known_targets = []  # List of known infected palm positions
        self.known_drones = []   # List of known drone positions

        # Sensor and internal components
        self.radio = Radio(model, unique_id)             # For blackboard communication
        self.gps = GPS(*pos, model)                      # Tracks current position
        self.camera = Camera(model)                      # Captures visual data
        self.cv_model = CVModel()                        # Analyzes camera photos
        self.controller = Controller()                   # Navigation and decision logic
        self.battery = Battery(100)                      # Battery level tracker
        self.medicine = MedicineDispenser(model, 100)    # Holds and dispenses medicine

        # Sensor readings (populated during sensing)
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

    # ---------------------
    # COMMUNICATION (INPUT)
    # ---------------------
    def do_input_communication(self):
        # Read from shared blackboard (global communication stacks)
        self.known_targets = self.radio.read_blackboard_palms_targets()
        self.known_drones = self.radio.read_blackboard_drones_positions()

    # ---------------------
    # COMMUNICATION (OUTPUT)
    # ---------------------
    def do_output_communication(self):
        # Share own position and discovered target (if any)
        self.radio.publish_blackboard_drones_position(self.gps.get_position())
        if self.target:
            self.radio.publish_blackboard_palms_target({
                "location": self.target,
                "confidence": 1.0
            })

    # ---------------------
    # SENSING
    # ---------------------
    def do_sensing(self):
        self.photo = self.camera.take_photo()
        self.vision = self.cv_model.analyze(self.photo)
        self.battery_level = self.battery.get_level()
        self.medicine_level = self.medicine.get_level()

    # ---------------------
    # CONTROL
    # ---------------------
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
            self.next_move = None  # Stay in place and cure

        elif self.state == "moving_to_target":
            if position == self.target:
                self.state = "curing"
                self.next_move = None
            else:
                self.next_move = self.controller.move_towards(position, self.target, self.known_drones)

        elif self.state == "returning_to_charging_station":
            station = self.controller.get_nearest_station(position)
            self.next_move = self.controller.move_towards(position, station, self.known_drones)

    # ---------------------
    # ACTION
    # ---------------------
    def do_action(self):
        if self.state == "curing":
            position = self.gps.get_position()
            self.medicine.dispense(position)

        elif self.next_move:
            self.model.grid.move_agent(self, self.next_move)
            self.gps.set_position(*self.next_move)
            self.battery.consume(1)
