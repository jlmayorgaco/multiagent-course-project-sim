def convert_infected_matrix_to_dict(result, top_left_x, top_left_y):
    """
    Convert the infection matrix into a dictionary:
    {
        "(x, y)": confidence
    }
    Only includes infected cells.

    Parameters:
        result (list of list of dict): Output from CVModel.analyze
        top_left_x (int): X coordinate of top-left cell of the matrix
        top_left_y (int): Y coordinate of top-left cell of the matrix

    Returns:
        dict: Detected infected cells with their coordinates as keys
    """
    infected_dict = {}

    for dy, row in enumerate(result):
        for dx, cell in enumerate(row):
            if cell["infected"] == 1:
                coord = (top_left_x + dx, top_left_y + dy)
                infected_dict[str(coord)] = cell["confidence"]

    return infected_dict
