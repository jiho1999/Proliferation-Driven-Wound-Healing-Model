# initialization.py

import numpy as np
from constants import EMPTY, ALIVE

def initialize_grid(grid_size_x, grid_size_y):
    return np.full((grid_size_x, grid_size_y), EMPTY, dtype=int)

def initialize_cells(grid_size_x, grid_size_y):
    # Left block of cells (first 30 grid points)
    left_block = [(j, i) for i in range(30) for j in range(grid_size_y)]
    # Right block of cells (last 30 grid points)
    right_block = [(j, i) for i in range(70, grid_size_x) for j in range(grid_size_y)]

    # Combine both blocks
    initial_positions = np.array(left_block + right_block)
    initial_states = np.array([ALIVE] * len(initial_positions))

    return initial_positions, initial_states
