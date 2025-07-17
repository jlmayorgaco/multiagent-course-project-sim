import random

class CVModel:
    def __init__(self, model):
        self.model = model

    def analyze(self, photo_data):
        """
        Analyze each cell in photo_data and return a matrix of:
        { 'infected': 0 or 1, 'confidence': float }

        Args:
            photo_data (list of list): matrix with 'verde', 'infectada', or None

        Returns:
            list of list of dict: same shape with infection prediction per cell
        """
        result_matrix = []

        for row in photo_data:
            result_row = []
            for cell in row:
                
                # Simulate ML CV Model
                infected = 1 if cell == "infectada" else 0
                confidence = round(random.uniform(0.6, 0.99), 4)
                result_row.append({
                    "infected": infected,
                    "confidence": confidence
                })
                
            result_matrix.append(result_row)

        return result_matrix

    def convert_infected_matrix_to_dict(self, result, center_x, center_y):
        """
        Convert the infection matrix into a dictionary from the *center* position.

        Args:
            result (list of list of dict): Output from analyze()
            center_x, center_y (int): center position of the drone in the grid

        Returns:
            dict: {(x, y): confidence} for infected cells
        """
        infected_dict = {}

        height = len(result)
        width = len(result[0]) if height > 0 else 0

        offset_y = height // 2
        offset_x = width // 2

        for dy, row in enumerate(result):
            for dx, cell in enumerate(row):
                grid_x = center_x + (dx - offset_x)
                grid_y = center_y + (dy - offset_y)

                if (0 <= grid_x < self.model.grid.width) and (0 <= grid_y < self.model.grid.height):
                    if cell["infected"] == 1:
                        infected_dict[(grid_x, grid_y)] = cell["confidence"]  # ← Use tuple here
                    else :
                        infected_dict[(grid_x, grid_y)] = - cell["confidence"]
        return infected_dict


    def get_camera_value_by_photo(self, photo_data):
        return self.analyze(photo_data)
