import numpy as np
from sys import stderr
import nmrPype
import dearpygui.dearpygui as dpg
from scipy.optimize import dual_annealing, differential_evolution, minimize
from scipy.signal import find_peaks

from simulate.simulate import simulate_peaklist
from optimize.types import PeakArray
from ui.callbacks.plot import update_plot_callback, update_simulation_plot
from ui.callbacks import set_nmr_plot_values, set_plot_values, zoom_subplots_to_peaks
from spin.spin import Spin, loadSpinFromFile
from ui.themes import Theme

def objective_function(params : np.ndarray | list, nmr_array : np.ndarray, spin : Spin, num_of_freq : int,
                       matrix_shape : tuple, matrix_size : int, points : int, freq_limits : list[float]):
    
    nuclei_frequencies, couplings, spec_width, obs, hhw = unpack_params(params, num_of_freq, matrix_size, matrix_shape)

    new_spin = Spin(spin.spin_names, list(nuclei_frequencies), couplings, half_height_width=hhw, field_strength=spin.field_strength)

    simulation : PeakArray = simulate_peaklist(new_spin.peaklist(), points, hhw, (freq_limits[0], freq_limits[1]))

    # Scale peaks_plot x axis to match nmr_peaks_plot x axis
    nmr_x = nmr_array[0]
    sim_x = simulation[0]
    if np.ptp(sim_x) != 0:
        scale_x = np.ptp(nmr_x) / np.ptp(sim_x)
        # offset_x = np.min(nmr_x) - np.min(sim_x) * scale_x
        simulation[0] = sim_x * scale_x #+ offset_x

    # Scale peaks_plot y axis to match nmr_peaks_plot y axis
    nmr_y = nmr_array[1]
    sim_y = simulation[1]
    if np.ptp(sim_y) != 0:
        scale = np.ptp(nmr_y) / np.ptp(sim_y)
        # offset = np.min(nmr_y) - np.min(sim_y) * scale
        simulation[1] = sim_y * scale #+ offset

    difference = np.sqrt(np.mean((np.flip(sim_y) - nmr_y) ** 2))

    new_simulation = np.vstack((nmr_x, np.flip(sim_y)))
    set_plot_values(new_simulation, new_spin._nuclei_number)
    set_nmr_plot_values(np.vstack((nmr_x, nmr_y)))

    return difference

def unpack_params(params : np.ndarray | list, num_of_freq : int, matrix_size : int, matrix_shape : tuple):
    frequencies= np.array(params[:num_of_freq])
    cMatrix_flat = np.array(params[num_of_freq:num_of_freq+matrix_size])
    sw, obs, w = params[num_of_freq+matrix_size:]

    return frequencies, cMatrix_flat.reshape(matrix_shape), sw, obs, w

def sliding_window_optimization(nmr_array, spin, num_of_freq, matrix_shape, matrix_size, points, freq_limits, window_size=200):
    """
    Perform sliding window optimization: for each detected peak in the real data, optimize parameters in a window around the peak.
    """
    # Find peaks in real data
    peak_indices, _ = find_peaks(nmr_array[1], height=np.max(nmr_array[1])*0.1, distance=window_size//2)
    optimized_params_list = []
    spin_names = spin.spin_names
    initial_params = np.concatenate((spin.nuclei_frequencies, spin.couplings.flatten(), [spin.field_strength, spin.field_strength, spin.half_height_width]))

    if not dpg.does_item_exist('opt_window'):
        with dpg.window(label='Optimization in Progress', tag='opt_window', width=600, height=500) as opt_window:
            with dpg.plot(label="Optimization Snippet", tag='opt_plot', width=-1, height=400):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="opt_x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="opt_y_axis")
        with dpg.value_registry():
            dpg.add_bool_value(default_value=False, tag='opt_series_added')
    else:
        dpg.show_item('opt_window')

    for idx in peak_indices:
        start = max(idx - window_size, 0)
        end = min(idx + window_size, len(nmr_array[0]))
        real_x = nmr_array[0][start:end]
        real_y = nmr_array[1][start:end]
        real_segment = np.vstack((real_x, real_y))

        def local_objective(params):
            nuclei_frequencies, couplings, spec_width, obs, hhw = unpack_params(params, num_of_freq, matrix_size, matrix_shape)
            new_spin = Spin(spin_names, list(nuclei_frequencies), couplings, half_height_width=hhw, field_strength=spin.field_strength)
            sim_segment = simulate_peaklist(new_spin.peaklist(), len(real_x), hhw, (real_x[0], real_x[-1]))
            sim_y = sim_segment[1]
            # Scale y for fair comparison
            if np.ptp(sim_y) != 0:
                scale = np.ptp(real_y) / np.ptp(sim_y)
                sim_y = sim_y * scale
            if not dpg.get_value('opt_series_added'):
                dpg.add_line_series(real_x, sim_y, label='Simulation Slice', parent='opt_y_axis', tag='sim_opt_series')
                dpg.add_line_series(real_x, real_y, label='Real Slice', parent='opt_x_axis', tag='real_opt_series')
                dpg.set_value('opt_series_added', True)
            else:
                dpg.set_value('sim_opt_series', [real_x, sim_y])
                dpg.set_value('real_opt_series', [real_x, real_y])

            # Ensure x bounds match real data's limits
            # dpg.set_axis_limits_constraints('opt_x_axis', real_x[0], real_x[-1])
            dpg.set_axis_limits_constraints('opt_y_axis', 0, np.max(real_y) + 0.1 * np.max(real_y))

            # Draw vertical lines on the main plot to indicate the current region
            # Only update if region has changed
            current_region = None
            new_region = (real_x[0], real_x[-1])
            if current_region is None or current_region != new_region:
                if dpg.does_item_exist('main_x_axis'):
                    # Remove previous region lines if they exist
                    if dpg.does_item_exist('region_line_left'):
                        dpg.delete_item('region_line_left')
                    if dpg.does_item_exist('region_line_right'):
                        dpg.delete_item('region_line_right')

                    # Draw new region lines
                    dpg.add_inf_line_series(real_x[0], label='Region Start', parent='main_x_axis', tag='region_line_left')
                    dpg.add_inf_line_series(real_x[-1], label='Region End', parent='main_x_axis', tag='region_line_right')
                    dpg.bind_item_theme('region_line_left', Theme.red_line_theme())
                    dpg.bind_item_theme('region_line_right', Theme.red_line_theme())
                    # Store current region
                    current_region = (real_x[0], real_x[-1])

            return np.sqrt(np.mean((sim_y - real_y) ** 2))
        # Use current spin parameters as initial guess
        result = minimize(local_objective, initial_params, method='L-BFGS-B')
        optimized_params_list.append(result.x)
        # Optionally update initial_params for next window
        initial_params = result.x
        
    # Combine all local results (e.g., average)
    optimized_params = np.mean(optimized_params_list, axis=0)
    if dpg.does_item_exist('region_line_left'):
        dpg.delete_item('region_line_left')
    if dpg.does_item_exist('region_line_right'):
        dpg.delete_item('region_line_right')
    return optimized_params

def optimize_simulation(nmr_file : str, spin_matrix_file : str, field_strength : int, init_hhw : float = 1.0) -> Spin:
    df = nmrPype.DataFrame(nmr_file)

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")
    
    x_vals = np.arange(1, len(df.array)+1)

    init_sw = df.getParam("NDSW") 
    init_obs = df.getParam("NDOBS")
    init_orig = df.getParam("NDORIG")
    init_size = df.getParam("NDSIZE")

    init_sw  = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta = -init_sw/(init_size)
    first = init_orig - delta*(init_size - 1)

    specValPPM  = (first + (x_vals - 1.0)*delta)/init_obs
    specValHz = [ppm * field_strength for ppm in specValPPM]

    freq_limits = [specValHz[0], specValHz[-1]]
    freq_limits.sort()

    nmr_array = np.vstack((specValHz, df.array))

    spin_names, nuclei_frequencies, couplings = loadSpinFromFile(spin_matrix_file)
    spin = Spin(spin_names, nuclei_frequencies, couplings, half_height_width=init_hhw, field_strength=field_strength)
    num_of_freq = len(nuclei_frequencies)

    initial_values = [init_sw, init_obs, init_hhw]
    points = len(nmr_array[0])
    params = np.concatenate((nuclei_frequencies, couplings.flatten(), initial_values))
    matrix_shape = couplings.shape
    matrix_size = couplings.size

    # Use sliding window optimization
    optimized_params = sliding_window_optimization(nmr_array, spin, num_of_freq, matrix_shape, matrix_size, points, freq_limits)

    new_freqs, new_couplings, sw, obs, new_hhw = unpack_params(optimized_params, num_of_freq, matrix_size, matrix_shape)

    optimized_spin = Spin(spin_names, list(new_freqs), new_couplings, new_hhw, field_strength=field_strength)
    print("Successfully optimized spin matrix!", file=stderr)
    return optimized_spin

def optimize_callback(sender, app_data, user_data):
    if not hasattr(user_data, "spin_file") or not user_data.spin_file:
        print("Failed to Optimize! Missing Requirement: spin_file", file=stderr)
        return
    if not hasattr(user_data, "nmr_file") or not user_data.nmr_file:
        print("Failed to Optimize! Missing Requirement: nmr_file", file=stderr)
        return
    if not hasattr(user_data, 'field_strength') or not user_data.field_strength:
        print("Failed to Optimize! Missing Requirement: field_strength", file=stderr)
        return
    
    nmr_file : str = user_data.nmr_file
    spin_matrix_file : str = user_data.spin_file
    field_strength : int = user_data.field_strength

    optimized_spin = optimize_simulation(nmr_file, spin_matrix_file, field_strength)

    zoom_subplots_to_peaks(user_data)
    setattr(user_data, "spin", optimized_spin)
    update_simulation_plot(optimized_spin, user_data.points, optimized_spin.half_height_width, optimized_spin._nuclei_number)