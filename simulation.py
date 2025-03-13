# simulation.py

import numpy as np
import random
import time
from constants import *
from initialization import initialize_grid, initialize_cells
from cell_actions import check_senescence_migration, random_action
from utils import *
import pandas as pd

def run_simulation(senescence_probability, num_steps, runs=1):
    for run in range(runs):
        # Seed the random number generator with the current time at the start of each run
        random.seed(time.time())

        grid = initialize_grid(grid_size_x, grid_size_y)
        cell_positions, cell_states = initialize_cells(grid_size_x, grid_size_x)
        
        results = []
        division_counts = []
        migration_counts = []
        avg_permeability_lst = []
        wound_empty_dead_counts = []  # List to store the count of EMPTY/DEAD in wound area per step
        wound_positions = set() # Variable to track when all wound area is update
        wound_closed_step = None # To record the step when all wound positions are updated
        wound_area = set((x, y) for x in range(30, 70) for y in range(grid_size_y)) # Define the full set of wound positions (x = 30 to x = 69 across all y)
        senescent_counts = []

        for step in range(num_steps):
            # Visualize the initial grid of alive and wound area (0-29 and 70-99: alive, 30-69: wound)
            if step == 0:
                color_grid, grid = update_grid(grid, cell_positions, cell_states, grid_size_x, grid_size_y)
                visualize_grid(color_grid, step, run, senescence_probability, save_images=True)
                print(step)

            # Process cell actions and update grid, cell positions, and cell states here
            new_positions, new_states = [], []
            migration_count = 0
            division_count = 0

            indices = list(range(cell_positions.shape[0]))
            random.shuffle(indices)

            for i in indices:
                x, y = cell_positions[i]
                state = cell_states[i]

                if state == ALIVE:
                    migration_count = random_action(x, y, grid, new_positions, new_states, migration_count, division_probability, death_probability, migration_probability, wound_positions)

                elif state == DIVIDING:
                    neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                    random.shuffle(neighbors)
            
                    open_neighbors = []  # List to store valid, open neighbors
            
                    # Collect open neighbors
                    for dx, dy in neighbors:
                        nx, ny = x + dx, y + dy
                
                        # Ensure the new position is within the grid boundaries
                        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                            if grid[nx, ny] == EMPTY and (nx, ny) not in new_positions:  # Check if the spot is open (empty)
                                open_neighbors.append((nx, ny))
            
                    # If there's an open spot, divide the cell and place the new cell
                    if open_neighbors:
                        new_position = random.choice(open_neighbors)  # Randomly choose one open neighbor

                        if random.random() < death_probability:
                            new_states.append(DEAD)
                            new_positions.append((x, y))
                        elif random.random() < senescence_probability:
                            new_states.append(SENESCENT)
                            new_positions.append((x, y))  # Add the new cell position
                        else:
                            new_states.append(ALIVE)
                            new_positions.append(new_position)  # Add the new cell position
                            new_states.append(ALIVE)
                            new_positions.append((x, y))
                            division_count += 1  # Count division
                            # Update the grid promptly in order to reflect the current grid status for next cells' division and migration in a single update step
                            grid[new_position[0], new_position[1]] = ALIVE

                            # If the new cell is placed in the wound region, mark it as updated
                            if (30 <= new_position[0] <= 69):
                                wound_positions.add((new_position[0], new_position[1]))  # Add this position to the updated wound positions

                    # If there is no open neighbor, the original cell change back to ALIVE
                    else:
                        new_states.append(ALIVE)
                        new_positions.append((x, y))

                elif state == DEAD:
                    new_states.append(EMPTY)
                    new_positions.append((x, y))
                    # Update the grid promptly in order to reflect the current grid status for next cells' division and migration in a single update step
                    grid[x, y] = EMPTY
                    # Dead cells are not added to new_states or new_positions after this cycle
                    continue  # Skip adding this cell to the new lists
                
                elif state == SENESCENT:
                    move_status, migration_count = check_senescence_migration(x, y, grid, new_positions, new_states, migration_count, senescence_migration_probability, wound_positions)
                    if not move_status:
                        new_states.append(SENESCENT)  # Senescent cells remain senescent
                        new_positions.append((x, y))
                        if 30 <= x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
                            wound_positions.add((x, y))
                    else:
                        continue # Skip further processing for this cell
            
            # After processing all cells for this step, check if the wound area is fully updated
            if wound_area == wound_positions and wound_closed_step is None:
                wound_closed_step = step + 1
                print(f"All wound positions were updated at step {wound_closed_step}")
            
            # Store the division and migration count for each step of update
            division_counts.append(division_count)
            migration_counts.append(migration_count)

            # Update positions and states
            cell_positions, cell_states = np.array(new_positions), np.array(new_states)
            
            # Visualization (update_grid will update the grid and return the color grid to visualize using visualize_grid)
            color_grid, grid = update_grid(grid, cell_positions, cell_states, grid_size_x, grid_size_y)
            visualize_grid(color_grid, step + 1, run, senescence_probability, save_images=True)
            print(step)

            # Calculate and append the permeability for each step
            avg_permeability_lst.append(calculate_permeability(grid))

            # Count EMPTY or DEAD cells in the wound area for this step
            empty_dead_count = sum(1 for (x, y) in wound_area if grid[x, y] in {EMPTY, DEAD})
            wound_empty_dead_counts.append(empty_dead_count)

            # Count the number of SENESCENT cell
            senescent_counts.append(np.sum(cell_states == 3))

        # Save data
        for step in range(num_steps):
            results.append([senescence_probability, step + 1, division_counts[step], migration_counts[step], avg_permeability_lst[step], wound_empty_dead_counts[step], senescent_counts[step]])

        filename = f'division_migration_senescence_{senescence_probability:.1e}_run_{run + 1}.xlsx'
        df_results = pd.DataFrame(results, columns=['Senescence Probability', 'Step', 'Division Count', 'Migration Count', 'Average Permeability', 'Wound Area', 'Senescent_Count'])
        # Reorder columns to move 'Senescent Count' to the last position
        df_results['Wound Closure Step'] = wound_closed_step if wound_closed_step is not None else 'Not closed yet'
        df_results.to_excel(filename, index=False)

        # # Plot the data
        # plot_results(filename)
