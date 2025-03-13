# cell_actions.py

import random
import time
from constants import EMPTY, ALIVE, DEAD, DIVIDING, SENESCENT

# Function to check room for division (without periodic boundary and correct boundary checks)
def check_room_in_grid(x, y, grid):
    neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in neighbors:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx, ny] == EMPTY:
                return True
    return False

# Function to check if room is available in the list of new positions
def check_room_in_new_positions(x, y, new_positions, grid):
    neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in neighbors:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if (nx, ny) not in new_positions:
                return True
    return False

# Function to move cells to an available empty neighboring spot
def move_cells(x, y, new_positions, grid):
    # # Non Directional Movement; during homeostasis
    # neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # random.shuffle(neighbors)
    # for dx, dy in neighbors:
    #     nx, ny = x + dx, y + dy
    #     if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
    #         if grid[nx, ny] == EMPTY and check_room_in_new_positions(x, y, new_positions, grid):
    #             return nx, ny
    # return x, y # Since we use move_cells function when we know there is a open spot, code will not reach return x, y

    # Directional movement; during wound healing process
    neighbors = [(-1, 1), (0, 1), (1, 1)] if y <= 49 else [(-1, -1), (0, -1), (1, -1)]
    random.shuffle(neighbors)
    for dx, dy in neighbors:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx, ny] == EMPTY and check_room_in_new_positions(x, y, new_positions, grid):
                # print(f"Moving cell from ({x}, {y}) to ({nx}, {ny})")
                return nx, ny
    # print(f"No valid move found for cell at ({x}, {y})")
    return x, y  # Return the original position if no move is possible

def move_senescent_cells(x, y, new_positions, grid):
    # Non Directional Movement; during homeostasis
    neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    random.shuffle(neighbors)
    for dx, dy in neighbors:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx, ny] == EMPTY and check_room_in_new_positions(x, y, new_positions, grid):
                return nx, ny
    return x, y # Since we use move_cells function when we know there is a open spot, code will not reach return x, y

# Define a function for cell division
def check_division(x, y, grid, new_positions, new_states, division_probability, wound_positions):
    if random.random() < division_probability and check_room_in_grid(x, y, grid) and check_room_in_new_positions(x, y, new_positions, grid):
        new_states.append(DIVIDING)  # Enter dividing state
        new_positions.append((x, y))  # Keep the original cell's position
        if 30 <= x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
            wound_positions.add((x, y))
        return True  # Division occurred
    return False  # Division didn't happen

# Define a function for cell death
def check_death(x, y, new_positions, new_states, death_probability, wound_positions):
    if random.random() < death_probability:  # Chance to die
        new_states.append(DEAD)
        new_positions.append((x, y))  # Keep the dead cell in the grid for this cycle
        if 30 <= x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
            wound_positions.add((x, y))
        return True  # Death occurred
    return False  # Death didn't happen

# Define a function for cell migration (modifies migration_count)
def check_migration(x, y, grid, new_positions, new_states, migration_count, migration_probability, wound_positions):
    if random.random() < migration_probability and check_room_in_grid(x, y, grid) and check_room_in_new_positions(x, y, new_positions, grid):
        migration_count += 1  # Increment migration count
        new_x, new_y = move_cells(x, y, new_positions, grid)  # Move cell to a new position
        new_states.append(ALIVE)
        new_positions.append((new_x, new_y))
        # Update the grid promptly in order to reflect the current grid status for next cells' division and migration in a single update step
        grid[x, y] = EMPTY
        grid[new_x, new_y] = ALIVE

        if 30 <= new_x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
            wound_positions.add((new_x, new_y))

        return True, migration_count  # Migration occurred
    return False, migration_count  # Migration didn't happen

def check_senescence_migration(x, y, grid, new_positions, new_states, migration_count, senescence_migration_probability, wound_positions):
    if random.random() < senescence_migration_probability and check_room_in_grid(x, y, grid) and check_room_in_new_positions(x, y, new_positions, grid):
        migration_count += 1  # Increment migration count
        new_x, new_y = move_senescent_cells(x, y, new_positions, grid)  # Move cell to a new position
        new_states.append(SENESCENT)
        new_positions.append((new_x, new_y))
        # Update the grid promptly in order to reflect the current grid status for next cells' division and migration in a single update step
        grid[x, y] = EMPTY
        grid[new_x, new_y] = SENESCENT

        if 30 <= new_x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
            wound_positions.add((new_x, new_y))

        return True, migration_count  # Migration occurred
    return False, migration_count  # Migration didn't happen

# Define a function for keeping a cell alive
def check_alive(x, y, new_positions, new_states, wound_positions):
    new_states.append(ALIVE)
    new_positions.append((x, y))  # Keep the original position
    if 30 <= x <= 69:  # If the cell moves into the wound region, mark the wound position as updated
        wound_positions.add((x, y))
    return True  # Cell stays alive

# Function to choose a random action for each cell
def random_action(x, y, grid, new_positions, new_states, migration_count, division_probability, death_probability, migration_probability, wound_positions):
    # If the cell is senescent, it remains in its state and is not processed further
    if grid[x, y] == SENESCENT:
        new_states.append(SENESCENT)
        new_positions.append((x, y))
        if 30 <= x <= 69:  # Mark the wound position as updated if applicable
            wound_positions.add((x, y))
        return migration_count
    
    actions = [
        lambda: (check_division(x, y, grid, new_positions, new_states, division_probability, wound_positions), migration_count),
        lambda: (check_death(x, y, new_positions, new_states, death_probability, wound_positions), migration_count,),
        lambda: check_migration(x, y, grid, new_positions, new_states, migration_count, migration_probability, wound_positions),
        lambda: (check_alive(x, y, new_positions, new_states, wound_positions), migration_count)
    ]

    random.shuffle(actions)

    for action in actions:
        success, migration_count = action()
        if success:
            break

    return migration_count  # Return the updated migration_count
