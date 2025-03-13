# utils.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import ListedColormap
from constants import EMPTY, DEAD, ALIVE, DIVIDING, SENESCENT
import os
import pandas as pd
import imageio
import glob


# Create custom colormap and legend for visualization
cmap = ListedColormap(['white', 'red', 'green', 'blue', 'yellow'])  # [EMPTY, DEAD, ALIVE, DIVIDING, SENESCENT]

def create_legend():
    legend_labels = ['EMPTY', 'DEAD', 'ALIVE', 'DIVIDING', 'SENESCENT']
    legend_colors = ['white', 'red', 'green', 'blue', 'yellow']
    return [mpatches.Patch(color=legend_colors[i], label=legend_labels[i]) for i in range(1, 5)]  # Exclude 'EMPTY'

def update_grid(grid, cell_positions, cell_states, grid_size_x, grid_size_y):
    # Clear the grid and assign different colors based on cell state
    grid = np.full((grid_size_x, grid_size_y), EMPTY)  # Initialize the grid to EMPTY (-1)
    color_grid = np.full((grid_size_x, grid_size_y), EMPTY)  # Initialize color grid for visualization
    for pos, state in zip(cell_positions, cell_states):
        grid[pos[0], pos[1]] = state
        color_grid[pos[0], pos[1]] = state

    return grid, color_grid

# def visualize_grid(color_grid, step, run_number, senescence_probability, save_images=False):
#     output_dir='simulation_images'

#         # Plot the grid with the custom colormap
#     plt.imshow(color_grid, cmap=cmap, vmin=-1, vmax=3)
#     plt.title(f'Run {run_number + 1} - Step {step}')
#     plt.legend(handles=create_legend(), bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

#     # Save the image if required
#     if save_images:
#         # Ensure the output directory exists
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
#         # Save the image with a descriptive filename
#         filename = os.path.join(output_dir, f'run_{run_number + 1}_senescence_{senescence_probability:.1e}_step_{step:03d}.png')
#         plt.savefig(filename)

#     # Display the plot and clear it afterward
#     plt.pause(0.1)
#     plt.clf()

def visualize_grid(color_grid, step, run_number, senescence_probability, save_images=False):
    output_dir = 'simulation_images'

    # Create the plot without axes or any extra elements
    plt.imshow(color_grid, cmap=cmap, vmin=-1, vmax=3)
    plt.axis('off')  # Turn off axis

    # Save the image if required
    if save_images:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Save the image with a descriptive filename
        filename = os.path.join(output_dir, f'run_{run_number + 1}_senescence_{senescence_probability:.1e}_step_{step:03d}.png')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=100)  # Set dpi for 100x100 pixels
    plt.clf()  # Clear the plot after saving

def create_simulation_video(run_number, senescence_probability, frames_dir='simulation_images', output_dir='simulation_videos', fps=5):
    os.makedirs(output_dir, exist_ok=True)
    video_filename = os.path.join(output_dir, f'simulation_run_{run_number + 1}_senescence_{senescence_probability:.1e}.mp4')

    # Collect all frame files in order
    frame_files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png') and f'run_{run_number + 1}' in f])

    # Write frames to video
    with imageio.get_writer(video_filename, fps=fps) as writer:
        for frame_file in frame_files:
            image = imageio.imread(frame_file)
            writer.append_data(image)

    print(f"Video saved as {video_filename}")

def calculate_permeability(grid):
    # Calculate the permeability
    edge_neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    avg_permeability_sum = 0
    cell_count = 0
    avg_permeability = 0

    # Cache grid dimensions to avoid repeated calls to len(grid)
    grid_rows = len(grid)
    grid_cols = len(grid[0])

    # Loop through every cell in the grid
    for width in range(grid_rows):
        for length in range(grid_cols):
            # Check if the grid cell is not EMPTY or DEAD
            if grid[width, length] not in {EMPTY, DEAD}:  
                cell_count += 1
                single_cell_permeability_sum = 0

                # Check neighboring cells
                for dx, dy in edge_neighbors:
                    nx, ny = width + dx, length + dy
                    # Ensure we stay within grid bounds
                    if 0 <= nx < grid_rows and 0 <= ny < grid_cols:
                        # Check if neighbor is EMPTY or SENESCENT
                        if grid[nx, ny] in {EMPTY, SENESCENT}:
                            single_cell_permeability_sum += 1

                # Add the permeability score of the current cell
                avg_permeability_sum += single_cell_permeability_sum / 4  # Dividing by 4 to average the permeability score for the cell

    # Only calculate the final average if we have valid cells
    if cell_count > 0:
        avg_permeability = avg_permeability_sum / cell_count
    
    return avg_permeability

# Function to plot Division Count and Migration Count vs Step
def plot_results(input_dir, output_dir='wound_closure_plot_results'):
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx') and 'division_migration_senescence' in file:
            # Load the results from the Excel file
            filepath = os.path.join(input_dir, file)
            df = pd.read_excel(filepath)
    
            # Extract data for plotting
            step = df['Step']
            division_count = df['Division Count']
            migration_count = df['Migration Count']
            avg_permeability = df['Average Permeability']
            senescence_probability = df['Senescence Probability'].iloc[0]
            wound_closure_step = df['Wound Closure Step'].iloc[0]

            # Create the plot
            plt.figure(figsize=(12, 6))

            # Plot Division Count
            plt.plot(step, division_count, label='Division Count', color='blue', linestyle='-', marker='o')

            # Plot Migration Count
            plt.plot(step, migration_count, label='Migration Count', color='green', linestyle='-', marker='x')

            # Add titles and labels
            plt.title(f'Division and Migration Counts vs Step (Senescence Probability: {senescence_probability:.1e})')
            plt.xlabel('Step')
            plt.ylabel('Count / Permeability')
            plt.legend()

            # Add text annotation for wound closure step
            if wound_closure_step != 'Not closed yet':
                plt.axvline(x=wound_closure_step, color='red', linestyle='--', label=f'Wound Closure Step: {wound_closure_step}')
                plt.text(wound_closure_step + 1, max(division_count.max(), migration_count.max()) * 0.9,
                        f'Wound Closure Step: {wound_closure_step}', color='red')

            # Ensure the output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save the plot to a file in the new directory
            plot_filename = os.path.join(output_dir, os.path.basename('division_migration_step').replace('.xlsx', '.png'))
            plt.savefig(plot_filename)

            # Show the plot
            plt.close()


            # Plot Average Permeability separately
            plt.figure(figsize=(12, 6))

            # Plot Average Permeability
            plt.plot(step, avg_permeability, label='Average Permeability', color='orange', linestyle='-', marker='s')

            # Add titles and labels
            plt.title(f'Average Permeability vs Step (Senescence Probability: {senescence_probability:.1e})')
            plt.xlabel('Step')
            plt.ylabel('Average Permeability')
            plt.legend()

            # Add text annotation for wound closure step (optional, since it may not make sense here)
            if wound_closure_step != 'Not closed yet':
                plt.axvline(x=wound_closure_step, color='red', linestyle='--', label=f'Wound Closure Step: {wound_closure_step}')
                plt.text(wound_closure_step + 1, avg_permeability.max() * 0.9,
                        f'Wound Closure Step: {wound_closure_step}', color='red')

            # Save the Average Permeability plot
            plot_filename = os.path.join(output_dir, os.path.basename('permeability_step').replace('.xlsx', '_avg_permeability.png'))
            plt.savefig(plot_filename)
            plt.close()

# # Function to plot Division Count, Migration Count, Permeability, and Wound Area for different senescence probabilities in one graph
# def plot_combined_results_multiple_probabilities(input_dir, output_dir='plot_results_combined'):
#     # Initialize lists to store data from different senescence probabilities
#     sen_probabilities = []
#     step_list = []
#     division_counts_list = []
#     migration_counts_list = []
#     avg_permeability_list = []
#     wound_area_list = []

#     # Iterate through all Excel files in the input directory and extract data
#     for file in os.listdir(input_dir):
#         if file.endswith('.xlsx') and 'division_migration_senescence' in file:
#             # Load the results from the Excel file
#             filepath = os.path.join(input_dir, file)
#             df = pd.read_excel(filepath)
            
#             # Verify the dataframe is not empty and contains necessary columns
#             if df.empty or 'Senescence Probability' not in df.columns:
#                 print(f"Skipping file {file} due to missing data or incorrect format.")
#                 continue
            
#             senescence_probability = df['Senescence Probability'].iloc[0]
#             print(f"Processing file: {file} with senescence probability: {senescence_probability}")

#             # Store data for plotting
#             sen_probabilities.append(senescence_probability)
#             step_list.append(df['Step'])
#             division_counts_list.append(df['Division Count'])
#             migration_counts_list.append(df['Migration Count'])
#             avg_permeability_list.append(df['Average Permeability'])
#             wound_area_list.append(df['Wound Area'])

#     # Create a figure with 4 subplots in a 2x2 layout
#     fig, axs = plt.subplots(2, 2, figsize=(15, 10))
#     fig.suptitle('Division, Migration, Permeability, and Wound Area vs Step for Different Senescence Probabilities', fontsize=16)

#     # Plot Division Count for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[0, 0].plot(step_list[i], division_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[0, 0].set_xlabel('Step')
#     axs[0, 0].set_ylabel('Division Count')
#     axs[0, 0].set_title('Division Count vs Step')
#     axs[0, 0].legend(loc='upper right')

#     # Plot Migration Count for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[0, 1].plot(step_list[i], migration_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[0, 1].set_xlabel('Step')
#     axs[0, 1].set_ylabel('Migration Count')
#     axs[0, 1].set_title('Migration Count vs Step')
#     axs[0, 1].legend(loc='upper right')

#     # Plot Average Permeability for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[1, 0].plot(step_list[i], avg_permeability_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[1, 0].set_xlabel('Step')
#     axs[1, 0].set_ylabel('Average Permeability')
#     axs[1, 0].set_title('Average Permeability vs Step')
#     axs[1, 0].legend(loc='upper right')

#     # Plot Wound Area (Empty/Dead Cells Count in Wound) for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[1, 1].plot(step_list[i], wound_area_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[1, 1].set_xlabel('Step')
#     axs[1, 1].set_ylabel('Wound Area (Empty/Dead Cells)')
#     axs[1, 1].set_title('Wound Area vs Step')
#     axs[1, 1].legend(loc='upper right')

#     # Adjust layout
#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])

#     # Ensure the output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Save the combined plot to a file in the new directory
#     plot_filename = os.path.join(output_dir, 'combined_plot_all_senescence_probabilities.png')
#     plt.savefig(plot_filename)

#     # Close the plot
#     plt.close()

# # Simplified function to ensure data is plotted and legends are displayed properly in a sorted order
# def plot_combined_results(input_dir, output_dir='plot_results_combined'):
#     # Initialize lists to store data from different senescence probabilities
#     sen_probabilities = []
#     step_list = []
#     division_counts_list = []
#     migration_counts_list = []
#     avg_permeability_list = []
#     wound_area_list = []

#     # Iterate through all Excel files in the input directory and extract data
#     for file in os.listdir(input_dir):
#         if file.endswith('.xlsx') and 'division_migration_senescence' in file:
#             # Load the results from the Excel file
#             filepath = os.path.join(input_dir, file)
#             df = pd.read_excel(filepath)
            
#             # Verify the dataframe is not empty and contains necessary columns
#             if df.empty or 'Senescence Probability' not in df.columns:
#                 print(f"Skipping file {file} due to missing data or incorrect format.")
#                 continue
            
#             senescence_probability = df['Senescence Probability'].iloc[0]
#             print(f"Processing file: {file} with senescence probability: {senescence_probability}")

#             # Store data for plotting
#             sen_probabilities.append(senescence_probability)
#             step_list.append(df['Step'])
#             division_counts_list.append(df['Division Count'])
#             migration_counts_list.append(df['Migration Count'])
#             avg_permeability_list.append(df['Average Permeability'])
#             wound_area_list.append(df['Wound Area'])

#     # Sort data by senescence probability
#     sorted_indices = sorted(range(len(sen_probabilities)), key=lambda i: sen_probabilities[i])
#     sen_probabilities = [sen_probabilities[i] for i in sorted_indices]
#     step_list = [step_list[i] for i in sorted_indices]
#     division_counts_list = [division_counts_list[i] for i in sorted_indices]
#     migration_counts_list = [migration_counts_list[i] for i in sorted_indices]
#     avg_permeability_list = [avg_permeability_list[i] for i in sorted_indices]
#     wound_area_list = [wound_area_list[i] for i in sorted_indices]

#     # Create a figure with 4 subplots in a 2x2 layout
#     fig, axs = plt.subplots(2, 2, figsize=(15, 10))
#     fig.suptitle('Division, Migration, Permeability, and Wound Area vs Step for Different Senescence Probabilities', fontsize=16)

#     # Plot Division Count for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[0, 0].plot(step_list[i], division_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[0, 0].set_xlabel('Step')
#     axs[0, 0].set_ylabel('Division Count')
#     axs[0, 0].set_title('Division Count vs Step')

#     # Plot Migration Count for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[0, 1].plot(step_list[i], migration_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[0, 1].set_xlabel('Step')
#     axs[0, 1].set_ylabel('Migration Count')
#     axs[0, 1].set_title('Migration Count vs Step')

#     # Plot Average Permeability for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[1, 0].plot(step_list[i], avg_permeability_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[1, 0].set_xlabel('Step')
#     axs[1, 0].set_ylabel('Average Permeability')
#     axs[1, 0].set_title('Average Permeability vs Step')

#     # Plot Wound Area (Empty/Dead Cells Count in Wound) for different senescence probabilities
#     for i in range(len(sen_probabilities)):
#         axs[1, 1].plot(step_list[i], wound_area_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.2f}')
#     axs[1, 1].set_xlabel('Step')
#     axs[1, 1].set_ylabel('Wound Area (Empty/Dead Cells)')
#     axs[1, 1].set_title('Wound Area vs Step')

#     # Add legends to all subplots in a sorted order
#     for ax in axs.flat:
#         handles, labels = ax.get_legend_handles_labels()
#         if handles:  # Check if there are any handles to add to the legend
#             sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: float(x[1].split(": ")[1]))
#             sorted_handles, sorted_labels = zip(*sorted_handles_labels)
#             ax.legend(sorted_handles, sorted_labels, loc='upper right')

#     # Adjust layout
#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])

#     # Ensure the output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Save the combined plot to a file in the new directory
#     plot_filename = os.path.join(output_dir, 'combined_plot_all_senescence_probabilities_sorted_simple.png')
#     plt.savefig(plot_filename)

#     # Close the plot
#     plt.close()

import os
import pandas as pd
import matplotlib.pyplot as plt

# Modified function to create plots for each run
def plot_combined_results(input_dir, output_dir='plot_results_each_run'):
    # Dictionary to store data for each run
    run_data = {}

    # Iterate through all Excel files in the input directory and extract data
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx') and 'division_migration_senescence' in file:
            # Load the results from the Excel file
            filepath = os.path.join(input_dir, file)
            # df = pd.read_excel(filepath)
            df = pd.read_excel(filepath, engine='openpyxl')
            
            # Verify the dataframe is not empty and contains necessary columns
            if df.empty or 'Senescence Probability' not in df.columns:
                print(f"Skipping file {file} due to missing data or incorrect format.")
                continue

            # Extract run number from the filename
            run_number = file.split('_run_')[-1].replace('.xlsx', '')
            if run_number not in run_data:
                run_data[run_number] = {
                    'sen_probabilities': [],
                    'step_list': [],
                    'division_counts_list': [],
                    'migration_counts_list': [],
                    'avg_permeability_list': [],
                    'wound_area_list': []
                }

            senescence_probability = df['Senescence Probability'].iloc[0]
            print(f"Processing file: {file} with senescence probability: {senescence_probability} for run: {run_number}")

            # Store data for plotting
            run_data[run_number]['sen_probabilities'].append(senescence_probability)
            run_data[run_number]['step_list'].append(df['Step'])
            run_data[run_number]['division_counts_list'].append(df['Division Count'])
            run_data[run_number]['migration_counts_list'].append(df['Migration Count'])
            run_data[run_number]['avg_permeability_list'].append(df['Average Permeability'])
            run_data[run_number]['wound_area_list'].append(df['Wound Area'])

    # Create plots for each run
    for run_number, data in run_data.items():
        sen_probabilities = data['sen_probabilities']
        step_list = data['step_list']
        division_counts_list = data['division_counts_list']
        migration_counts_list = data['migration_counts_list']
        avg_permeability_list = data['avg_permeability_list']
        wound_area_list = data['wound_area_list']

        # Sort data by senescence probability
        sorted_indices = sorted(range(len(sen_probabilities)), key=lambda i: sen_probabilities[i])
        sen_probabilities = [sen_probabilities[i] for i in sorted_indices]
        step_list = [step_list[i] for i in sorted_indices]
        division_counts_list = [division_counts_list[i] for i in sorted_indices]
        migration_counts_list = [migration_counts_list[i] for i in sorted_indices]
        avg_permeability_list = [avg_permeability_list[i] for i in sorted_indices]
        wound_area_list = [wound_area_list[i] for i in sorted_indices]

        # Create a figure with 4 subplots in a 2x2 layout
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Division, Migration, Permeability, and Wound Area vs Step', fontsize=16)

        # Plot Division Count for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[0, 0].plot(step_list[i], division_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[0, 0].set_xlabel('Step')
        axs[0, 0].set_ylabel('Division Count')
        axs[0, 0].set_title('Division Count vs Step')

        # Plot Migration Count for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[0, 1].plot(step_list[i], migration_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[0, 1].set_xlabel('Step')
        axs[0, 1].set_ylabel('Migration Count')
        axs[0, 1].set_title('Migration Count vs Step')

        # Plot Average Permeability for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[1, 0].plot(step_list[i], avg_permeability_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[1, 0].set_xlabel('Step')
        axs[1, 0].set_ylabel('Average Permeability')
        axs[1, 0].set_title('Average Permeability vs Step')

        # Plot Wound Area (Empty/Dead Cells Count in Wound) for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[1, 1].plot(step_list[i], wound_area_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[1, 1].set_xlabel('Step')
        axs[1, 1].set_ylabel('Wound Area (Empty/Dead Cells)')
        axs[1, 1].set_title('Wound Area vs Step')

        # Add legends to all subplots in a sorted order
        for ax in axs.flat:
            handles, labels = ax.get_legend_handles_labels()
            if handles:  # Check if there are any handles to add to the legend
                sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: float(x[1].split(": ")[1]))
                sorted_handles, sorted_labels = zip(*sorted_handles_labels)
                ax.legend(sorted_handles, sorted_labels, loc='upper right')

        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the combined plot to a file in the new directory
        plot_filename = os.path.join(output_dir, f'combined_plot_run_{run_number}.png')
        plt.savefig(plot_filename)

        # Close the plot
        plt.close()

# Function to calculate and plot the average wound closure step with standard deviation, ensuring x-axis labels are readable
def plot_avg_wound_closure_with_std(input_dir, output_dir='plot_results_each_run'):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Dictionary to store wound closure steps per senescence probability
    senescence_data = {}

    # Iterate through all Excel files in the input directory and extract data
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx') and 'division_migration_senescence' in file:
            # Extract senescence probability from the filename dynamically
            parts = file.split('_')
            try:
                senescence_prob = parts[3]  # Extract probability from the 4th part of the filename
            except IndexError:
                print(f"Skipping file {file} due to unexpected filename format.")
                continue

            # Load the results from the Excel file
            filepath = os.path.join(input_dir, file)
            df = pd.read_excel(filepath, engine='openpyxl')

            # Verify the dataframe is not empty and contains necessary columns
            if df.empty or 'Wound Closure Step' not in df.columns:
                print(f"Skipping file {file} due to missing data or incorrect format.")
                continue

            # Store the wound closure step data
            wound_closure_steps = df['Wound Closure Step'].tolist()
            if senescence_prob not in senescence_data:
                senescence_data[senescence_prob] = []
            senescence_data[senescence_prob].extend(wound_closure_steps)

    # Compute mean and standard deviation for each detected senescence probability
    avg_wound_closure_per_senescence = {k: np.mean(v) if v else 0 for k, v in senescence_data.items()}
    std_wound_closure_per_senescence = {k: np.std(v) if v else 0 for k, v in senescence_data.items()}
    print(avg_wound_closure_per_senescence)
    print(std_wound_closure_per_senescence)

    # Sort data by senescence probability in scientific notation order
    sorted_senescence = sorted(avg_wound_closure_per_senescence.keys(), key=lambda x: float(x))
    sorted_means = [avg_wound_closure_per_senescence[k] for k in sorted_senescence]
    sorted_stds = [std_wound_closure_per_senescence[k] for k in sorted_senescence]

    # Create bar chart with error bars (standard deviation)
    plt.figure(figsize=(8, 6))
    plt.bar(sorted_senescence, sorted_means, yerr=sorted_stds, capsize=5, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Senescence Probability', fontsize=12, labelpad=15)
    plt.ylabel('Average Wound Closure Step', fontsize=12, labelpad=15)
    plt.title('Average Wound Closure Step', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)  # Ensure readability by rotating and aligning x-axis labels
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot
    output_plot_path = os.path.join(output_dir, "avg_wound_closure_step_with_std.png")
    plt.savefig(output_plot_path, bbox_inches='tight')  # Ensure x-axis labels are not cut off
    plt.show()

    return output_plot_path

# def calculate_avg_division_count_per_senescence(input_dir):
#     # Dictionary to store division counts per senescence probability
#     senescence_division_data = {}

#     # Iterate through all Excel files in the input directory
#     for file in os.listdir(input_dir):
#         if file.endswith('.xlsx') and 'division_migration_senescence' in file:
#             # Extract senescence probability from the filename dynamically
#             parts = file.split('_')
#             try:
#                 senescence_prob = parts[3]  # Extract probability from the 4th part of the filename
#             except IndexError:
#                 print(f"Skipping file {file} due to unexpected filename format.")
#                 continue

#             # Load the results from the Excel file
#             filepath = os.path.join(input_dir, file)
#             df = pd.read_excel(filepath, engine='openpyxl')

#             # Verify the dataframe is not empty and contains necessary columns
#             if df.empty or 'Wound Closure Step' not in df.columns or 'Division Count' not in df.columns:
#                 print(f"Skipping file {file} due to missing data or incorrect format.")
#                 continue

#             # Extract wound closure step
#             wound_closure_step = df["Wound Closure Step"].iloc[0]  # Assuming constant within a file

#             # Sum division counts before wound closure
#             division_before_closure = df[df["Step"] <= wound_closure_step]["Division Count"].sum()

#             # Store the data
#             if senescence_prob not in senescence_division_data:
#                 senescence_division_data[senescence_prob] = []

#             senescence_division_data[senescence_prob].append(division_before_closure)
#             print(senescence_division_data)

#     # Compute the average division count for each senescence probability
#     avg_division_per_senescence = {
#         k: np.mean(v) if v else 0 for k, v in senescence_division_data.items()
#     }

#     return avg_division_per_senescence

# # Example usage
# input_directory = '/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Model_hour base'
# avg_division_counts = calculate_avg_division_count_per_senescence(input_directory)

# # Display the results
# df_results = pd.DataFrame(list(avg_division_counts.items()), columns=["Senescence Probability", "Avg Division Count"])
# print(df_results)

# def calculate_corrected_avg_division_count_per_senescence(input_dir):
#     # Dictionary to store division counts per senescence probability
#     senescence_division_data = {}

#     # Iterate through all Excel files in the input directory
#     for file in os.listdir(input_dir):
#         if file.endswith('.xlsx') and 'division_migration_senescence' in file:
#             # Extract senescence probability from the filename dynamically
#             parts = file.split('_')
#             try:
#                 senescence_prob = parts[3]  # Extract probability from the 4th part of the filename
#             except IndexError:
#                 print(f"Skipping file {file} due to unexpected filename format.")
#                 continue

#             # Load the results from the Excel file
#             filepath = os.path.join(input_dir, file)
#             df = pd.read_excel(filepath, engine='openpyxl')

#             # Verify the dataframe is not empty and contains necessary columns
#             if df.empty or 'Wound Closure Step' not in df.columns or 'Division Count' not in df.columns:
#                 print(f"Skipping file {file} due to missing data or incorrect format.")
#                 continue

#             # Extract wound closure step
#             wound_closure_step = df["Wound Closure Step"].iloc[0]  # Assuming constant within a file

#             # Compute the mean division count before wound closure for this run
#             df_filtered = df[df["Step"] <= wound_closure_step]
#             mean_division_before_closure = df_filtered["Division Count"].mean()

#             # Store the data
#             if senescence_prob not in senescence_division_data:
#                 senescence_division_data[senescence_prob] = []

#             senescence_division_data[senescence_prob].append(mean_division_before_closure)

#     # Compute the average of mean division counts for each senescence probability
#     corrected_avg_division_per_senescence = {
#         k: np.mean(v) if v else 0 for k, v in senescence_division_data.items()
#     }

#     return corrected_avg_division_per_senescence

# # Example usage
# input_directory = "/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Model_hour base"
# corrected_avg_division_counts = calculate_corrected_avg_division_count_per_senescence(input_directory)
# print(corrected_avg_division_counts)

# # Display the results
# df_results_corrected = pd.DataFrame(
#     list(corrected_avg_division_counts.items()), columns=["Senescence Probability", "Corrected Avg Division Count"]
# )

def calculate_corrected_avg_migration_count_per_senescence(input_dir):
    # Dictionary to store migration counts per senescence probability
    senescence_migration_data = {}
    fluctuation_std_per_senescence = {}

    # Iterate through all Excel files in the input directory
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx') and 'division_migration_senescence' in file:
            # Extract senescence probability from the filename dynamically
            parts = file.split('_')
            try:
                senescence_prob = parts[3]  # Extract probability from the 4th part of the filename
            except IndexError:
                print(f"Skipping file {file} due to unexpected filename format.")
                continue

            # Load the results from the Excel file
            filepath = os.path.join(input_dir, file)
            df = pd.read_excel(filepath, engine='openpyxl')

            # Verify the dataframe is not empty and contains necessary columns
            if df.empty or 'Wound Closure Step' not in df.columns or 'Migration Count' not in df.columns:
                print(f"Skipping file {file} due to missing data or incorrect format.")
                continue

            # Extract wound closure step
            wound_closure_step = df["Wound Closure Step"].iloc[0]  # Assuming constant within a file

            # Compute the mean migration count before wound closure for this run
            df_filtered = df[df["Step"] <= wound_closure_step]
            mean_migration_before_closure = df_filtered["Migration Count"].mean()

            # Store the data
            if senescence_prob not in senescence_migration_data:
                senescence_migration_data[senescence_prob] = []

            senescence_migration_data[senescence_prob].append(mean_migration_before_closure)

            # Compute the standard deviation of fluctuations after a big drop (5 steps after wound closure)
            df_post_closure = df[(df["Step"] > wound_closure_step) & (df["Step"] <= wound_closure_step + 5)]
            fluctuation_std = df_post_closure["Migration Count"].std()

            if senescence_prob not in fluctuation_std_per_senescence:
                fluctuation_std_per_senescence[senescence_prob] = []
            
            fluctuation_std_per_senescence[senescence_prob].append(fluctuation_std)

    # Compute the average of mean migration counts for each senescence probability
    corrected_avg_migration_per_senescence = {
        k: np.mean(v) if v else 0 for k, v in senescence_migration_data.items()
    }

    # Compute the average standard deviation of fluctuations per senescence probability
    avg_fluctuation_std_per_senescence = {
        k: np.mean(v) if v else 0 for k, v in fluctuation_std_per_senescence.items()
    }

    return corrected_avg_migration_per_senescence, avg_fluctuation_std_per_senescence

# Example usage
input_directory = "/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Model_hour base"
corrected_avg_migration_counts, avg_fluctuation_stds = calculate_corrected_avg_migration_count_per_senescence(input_directory)
print("Corrected Average Migration Counts:", corrected_avg_migration_counts)
print("Average Fluctuation Standard Deviations:", avg_fluctuation_stds)

# Display the results
df_results_corrected = pd.DataFrame(
    list(corrected_avg_migration_counts.items()), columns=["Senescence Probability", "Corrected Avg Migration Count"]
)

df_fluctuation_stds = pd.DataFrame(
    list(avg_fluctuation_stds.items()), columns=["Senescence Probability", "Fluctuation Std Dev"]
)