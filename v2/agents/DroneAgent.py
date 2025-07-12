from mesa import Agent
from .PalmAgent import PalmAgent
from .components import (
    GPS, 
    Battery, 
    Camera, 
    IRSensor, 
    Controller,
    MedicineDispenser, 
    CVModel
)
import random


class DroneAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

        # Components
        self.radio = Radio()
        self.gps = GPS(*pos)
        self.battery = Battery(100)
        self.camera = Camera()
        self.ir_sensors = {
            "top": IRSensor(),
            "left": IRSensor(),
            "right": IRSensor(),
            "bottom": IRSensor()
        }
        self.controller = Controller()
        self.medicine = MedicineDispenser()
        self.cv_model = CVModel()

        # State (updated every step)
        self.state = {
            "position": pos,
            "battery": 100,
            "medicine": 100
        }

        # Cached data per step
        self.sensor_data = {}
        self.analysis_result = {}
        self.infected_coords = []

    def update_state(self):
        self.state["position"] = self.gps.get_position()
        self.state["battery"] = self.battery.get_level()
        self.state["medicine"] = self.medicine.get_level()

    def sense_environment(self):
        self.sensor_data = {
            "battery": self.battery.get_level(),
            "position": self.gps.get_position(),
            "photo": self.camera.take_photo(),
            "proximity": {
                direction: sensor.get_value()
                for direction, sensor in self.ir_sensors.items()
            }
        }

    def communicate_read(self):
        # Placeholder for receiving information from other agents or environment
        # For now, simulate reading local infected palms
        self.nearby_palms = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)

    def controller_process(self):
        # Process photo to detect infection
        self.analysis_result = self.cv_model.analyze(self.sensor_data["photo"])
        if self.analysis_result.get("infected", False):
            self.infected_coords = self.controller.get_affected_palms(
                self.analysis_result, self.sensor_data["position"]
            )

    def communicate_send(self):
        # Simulate sending a message if infection detected
        if self.infected_coords:
            message = self.controller.build_message(self.infected_coords, self.sensor_data["position"])
            self.send_message(message)

    def execute_actions(self):
        self.try_to_cure_nearby_palms()
        self.move_randomly()
        self.controller.execute_actions()

    def try_to_cure_nearby_palms(self):
        for neighbor in self.nearby_palms:
            if isinstance(neighbor, PalmAgent) and neighbor.estado == "infectada":
                if random.random() < self.model.tasa_cura:
                    if self.medicine.dispense():
                        neighbor.estado = "verde"

    def move_randomly(self):
        possible_moves = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_pos = random.choice(possible_moves)
        self.model.grid.move_agent(self, new_pos)
        self.gps.set_position(*new_pos)
        self.battery.consume(1)

    def send_message(self, message):
        # Placeholder: could be network broadcast or shared model-level list
        print(f"[Drone {self.unique_id}] Notifying: {message}")

    def step(self):
        self.update_state()
        self.sense_environment()
        self.communicate_read()
        self.controller_process()
        self.communicate_send()
        self.execute_actions()







'''
from mesa import Agent
from .PalmAgent import PalmAgent

import random

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

class DroneAgent(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)

        #  Agent State
        self.state = {
            position_latitue = 
            position_longitude = 
            medicine_percentage = 
            battery_percentage = 
        }

        # Drone Components
        self._gps = new DroneGPS(latitude=0,longitude=0)
        self._battery = new DroneBattery(100)
        self._camera = new DroneCamera()
        self._IR1 = new DroneIRSensor()
        self._IR2 = new DroneIRSensor()
        self._IR3 = new DroneIRSensor()
        self._IR4 = new DroneIRSensor()
        self._controller = new DroneController()
        self._medicine = new DroneMedicineDispenser()
        self._model = new DroneCVModelML()

    def _state(self):
        self._state = {
            position_latitue = self._state_dynamics_latitute()
            position_longitude =  self._state_dynamics_latitute()
            medicine_percentage =  self._state_dynamics_latitute()
            battery_percentage =  self._state_dynamics_latitute()
        }

    def step(self):

        self._state()

        # Internal Sensors
        sensor_battery = self._battery.get_battery_level()
        sensor_position_latitude =  self._gps.get_latitude_value()
        sensor_position_longitude =  self._gps.get_longitude_value()

        # External Sensors
        sensor_camera_photo = self._camera.take_photo() 
        sensor_camera_values = self._model.get_camera_value_by_photo(sensor_camera_photo)
        
        sensor_proximity_top = self._IR1.get_value()
        sensor_proximity_left = self._IR2.get_value()
        sensor_proximity_rigth = self._IR3.get_value()
        sensor_proximity_bottom = self._IR4.get_value()

        coordinates_palms_affected = self._controller.get_palsm_affecteed(sensor_camera_values, sensor_position_latitude, sensor_position_longitude)

        message = self._controller.get_message(is_palm, is_affected, sensor_position)
        self.do_notify(message)

        _path = self._controller.get_path_planning()
        self.do_path(_path)

        self._controller.do_actions()


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
        


        '''