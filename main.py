# main.py

from simulation import run_simulation
from constants import *
from utils import plot_combined_results, plot_avg_wound_closure_with_std, plot_results, create_simulation_video
# from slope_calculation import senescence_slope_calculation, permeability_slope_calculation

if __name__ == "__main__":
    num_steps = 100

    for senescent_prob in constant_senescence_probability:
        run_simulation(senescent_prob, num_steps)

    # Directory where Excel files are saved
    input_dir = '/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Model_hour base'  # Current directory

    # Generate the combined plots for all senescence probabilities
    plot_combined_results(input_dir)

    # Run the function and generate the plot
    # plot_avg_wound_closure_with_std(input_dir)

    # #plot_results(input_dir)
    # plot_results(input_dir)

    # senescence_slope_calculation('/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Model')
    # permeability_slope_calculation('/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/Simple Homeostasis/CS Project Data/First Run')
    #create_simulation_video(0, 0.1, frames_dir='simulation_images', output_dir='simulation_videos', fps=5)
