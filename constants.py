# Constants for cell states
ALIVE = 1
DEAD = 0
DIVIDING = 2
SENESCENT = 3
EMPTY = -1  # New constant for empty spots

# Parameters for probabilities
# division_probability = 0.0278  # Probability of a cell dividing if space is available
# migration_probability = 0.9  # Probability of migration happening during division
# senescence_migration_probability = 0.45
# death_probability = 0.0003  # Probability of death happening per step

# Parameters for proliferation depenedent wound closing
# division_probability = 0.7  # Probability of a cell dividing if space is available
# migration_probability = 0.4  # Probability of migration happening during division
# senescence_migration_probability = 0.2
# death_probability = 0.01  # Probability of death happening per step

division_probability = 0.03  # Probability of a cell dividing if space is available
migration_probability = 0.9  # Probability of migration happening during division
senescence_migration_probability = 0.45
death_probability = 0.0003  # Probability of death happening per step


# constant_senescence_probability = [0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]  # Probability of senescence happening during division
# constant_senescence_probability =[0.1, 0.01, 0.001, 0.00001]
constant_senescence_probability =[0.1]

# Size of the grid
grid_size_x = 100
grid_size_y = 100
