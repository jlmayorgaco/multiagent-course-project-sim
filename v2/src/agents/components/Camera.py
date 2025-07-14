class Camera:
    def __init__(self, model, radius=1):
        self.model = model
        self.radius = radius
        self.last_photo = None

    def take_photo(self, pos):
        """Returns a matrix of palm health status (or None) around the given position."""
        x0, y0 = pos
        result = []

        for dy in range(-self.radius, self.radius + 1):
            row = []
            for dx in range(-self.radius, self.radius + 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height:
                    cell_agents = self.model.grid.get_cell_list_contents((x, y))
                    palm = next((a for a in cell_agents if a.__class__.__name__ == "PalmAgent"), None)
                    row.append(palm.estado if palm else None)
                else:
                    row.append(None)  # Outside the grid
            result.append(row)

        self.last_photo = result
        return result
