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
        self.pos = pos

    def step(self):

        # 1. Sensar Palmas
        # 2. Decidir Ruta
        # 3. Comunicar Pos Palma
        # 4. Go 

        sensor_battery = get_sensor_battery()
        sensor_camera = get_sensor_camera()
        sensor_position = get_sensor_position()
        sensor_proximity = get_sensor_proximity()

        [is_palm is_affected] = get_results_sensor(camera=sensor_camera, proximity = sensor_proximity)

        message = get_message(is_palm, is_affected, sensor_position)
        do_notify(message)

        _path = get_path_planning()
        do_path(_path)

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

