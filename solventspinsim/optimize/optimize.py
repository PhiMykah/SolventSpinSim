import numpy as np
from sys import stderr
import nmrPype
import dearpygui.dearpygui as dpg
from scipy.optimize import minimize

from simulate.simulate import simulate_peaklist
from ui.callbacks.plot import update_simulation_plot
from ui.callbacks import zoom_subplots_to_peaks
from spin.spin import Spin, loadSpinFromFile

def section_optimization(nmr_array : np.ndarray, spin : Spin, matrix_shape : tuple,
                         matrix_size : int, init_params : np.ndarray, water_range : tuple[float, float]) -> np.ndarray:
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

    optimized_params_list: list = []
    spin_names = spin.spin_names

    # Define water peak bounds
    water_left : float = min(water_range)
    water_center : float = sum(water_range)/2
    water_right : float = max(water_range) 

    bounds = [water_left, water_center, water_right]

    # Find indices of each water bound
    increasing_x = nmr_array[0][::-1]
    bound_indices = np.searchsorted(increasing_x, bounds)
    indices = [len(nmr_array[0]) - i for i in bound_indices]
    quadrants : tuple[tuple[float,float], ...] = ((0, indices[2]), 
                                                   (indices[2], indices[1]),
                                                   (indices[1], indices[0]),
                                                   (indices[0], len(nmr_array[0])))
    
    for quadrant in quadrants:
        start : int = quadrant[0]
        end : int = quadrant[1]

        real_x = nmr_array[0][start:end]
        real_y = nmr_array[1][start:end]

        # print(f"({start}, {end}) -> ({real_x[0]}, {real_x[-1]})", file=stderr)

        if dpg.does_item_exist('main_x_axis'):
            if dpg.does_item_exist('region_line_left'):
                dpg.delete_item('region_line_left')
            if dpg.does_item_exist('region_line_right'):
                dpg.delete_item('region_line_right')

            # Draw new region lines
            dpg.add_inf_line_series(real_x[0], label='Region Start', parent='main_x_axis', tag='region_line_left')
            dpg.add_inf_line_series(real_x[-1], label='Region End', parent='main_x_axis', tag='region_line_right')
            # dpg.bind_item_theme('region_line_left', Theme.red_line_theme())
            # dpg.bind_item_theme('region_line_right', Theme.red_line_theme())

        def quadrant_objective(params):
            couplings, intensities, spec_width, obs, hhw = unpack_params(params, matrix_size, matrix_shape)
            new_spin = Spin(spin_names, list(spin._ppm_nuclei_frequencies), couplings, hhw, spin.field_strength)
            simulation = simulate_peaklist(new_spin.peaklist(list(intensities)), len(real_x), hhw, (real_x[0],real_x[-1]))
            sim_y = list(np.ascontiguousarray(simulation[1][::-1]))
            if not dpg.does_item_exist('sim_opt_series'):
                dpg.add_line_series(real_x, sim_y, label='Simulation Slice', parent='opt_y_axis', tag='sim_opt_series')
            else:
                dpg.set_value('sim_opt_series', [real_x, sim_y])

            if not dpg.does_item_exist('real_opt_series'):
                dpg.add_line_series(real_x, real_y, label='Real Slice', parent='opt_y_axis', tag='real_opt_series')
            else:
                dpg.set_value('real_opt_series', [real_x, real_y])

            return np.sqrt(np.mean((sim_y - real_y) ** 2))
        
        result = minimize(quadrant_objective, init_params, method='L-BFGS-B')
        optimized_params_list.append(result.x)
        init_params = result.x

    optimized_params = np.mean(optimized_params_list, axis=0)
    if dpg.does_item_exist('region_line_left'):
        dpg.delete_item('region_line_left')
    if dpg.does_item_exist('region_line_right'):
        dpg.delete_item('region_line_right')
    return optimized_params


def optimize_simulation(nmr_file : str, spin_matrix_file : str, field_strength : int, water_range : tuple[float, float], init_hhw : float = 1.0) -> Spin:
    df = nmrPype.DataFrame(nmr_file)

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")
    
    x_vals : np.ndarray = np.arange(1, len(df.array) + 1)

    init_sw : float = df.getParam("NDSW") 
    init_obs : float = df.getParam("NDOBS")
    init_orig : float = df.getParam("NDORIG")
    init_size : float = df.getParam("NDSIZE")

    init_sw  = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta : float = -init_sw/(init_size)
    first : float = init_orig - delta*(init_size - 1)

    specValPPM = (first + (x_vals - 1.0)*delta)/init_obs
    specValHz : list[float] = [ppm * field_strength for ppm in specValPPM]

    freq_limits : list[float] = [specValHz[0], specValHz[-1]]
    freq_limits.sort()

    nmr_array = np.vstack((specValHz, df.array))
   
    spin_names, nuclei_frequencies, couplings = loadSpinFromFile(spin_matrix_file)
    spin = Spin(spin_names, nuclei_frequencies, couplings, half_height_width=init_hhw, field_strength=field_strength)

    initial_values : list[float] = [init_sw, init_obs, init_hhw]
    initial_intensities = [1.0] * spin._nuclei_number
    init_params : np.ndarray = np.concatenate((couplings.flatten(), initial_intensities, initial_values))
    matrix_shape = couplings.shape
    matrix_size : int = couplings.size 

    optimized_params = section_optimization(nmr_array, spin, matrix_shape, matrix_size, init_params, water_range)
    
    new_couplings, intensities, new_spec_width, new_obs, new_hhw = unpack_params(optimized_params, matrix_size, matrix_shape)
    
    optimized_spin = Spin(spin_names, nuclei_frequencies, new_couplings, new_hhw, field_strength, list(intensities))
    print('Optimization Complete!', file=stderr)
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
    water_range : tuple[float, float] = user_data.water_range

    if dpg.does_item_exist('water_drag_left'):
        dpg.hide_item('water_drag_left')
    if dpg.does_item_exist('water_center_line'):
        dpg.hide_item('water_center_line')
    if dpg.does_item_exist('water_drag_right'):
        dpg.hide_item('water_drag_right')

    optimized_spin = optimize_simulation(nmr_file, spin_matrix_file, field_strength, water_range)

    zoom_subplots_to_peaks(user_data)
    setattr(user_data, "spin", optimized_spin)
    update_simulation_plot(optimized_spin, user_data.points, optimized_spin.half_height_width, optimized_spin._nuclei_number)


def unpack_params(params : np.ndarray | list, matrix_size : int, matrix_shape : tuple):
    cMatrix_flat = np.array(params[:matrix_size])
    intensities = np.array(params[matrix_size:matrix_size+matrix_shape[0]])
    sw, obs, w = params[matrix_size+matrix_shape[0]:]

    return cMatrix_flat.reshape(matrix_shape), intensities, sw, obs, w