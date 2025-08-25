import numpy as np
from sys import stderr
import nmrPype
import dearpygui.dearpygui as dpg
from scipy.optimize import minimize

from simulate.simulate import simulate_peaklist
from ui.callbacks.plot import update_simulation_plot, update_plotting_ui
from ui.callbacks import zoom_subplots_to_peaks, show_item_callback
from spin.spin import Spin, loadSpinFromFile
from ui.themes import Theme

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    from simulate.water import Water

def section_optimization(nmr_array : np.ndarray, spin : Spin, matrix_shape : tuple,
                         matrix_size : int, init_params : np.ndarray, water_range : tuple[float, float], 
                         simulate_water : bool = False) -> np.ndarray:
    from simulate.water import Water

    if not dpg.does_item_exist('opt_window'):
        with dpg.window(label='Optimization in Progress', tag='opt_window', width=600, height=500) as opt_window:
            with dpg.plot(label="Optimization Snippet", tag='opt_plot', width=-1, height=400):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="opt_x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="opt_y_axis")
        with dpg.window(label='Optimization Parameters', tag='opt_params_window', width=400, height=600) as opt_window:
            dpg.add_text('Couplings:', tag='opt_coupling_title')
            with dpg.table(tag='opt_coupling_table', header_row=True, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=opt_window):
                dpg.add_table_column(label="##Top Left Corner")
                for atom in spin.spin_names:
                    dpg.add_table_column(label=str(atom))
                for i in range(spin._couplings.shape[0]):
                    with dpg.table_row():
                        dpg.add_text(spin.spin_names[i], tag=f'coupling_row_{i}_header')
                        for j in range(spin._couplings.shape[-1]):
                            dpg.add_text(f"", tag=f'opt_coupling_{i}_{j}')

            dpg.add_text('Intensities:', tag='opt_intensity_title')
            with dpg.table(tag='opt_intensity_table', header_row=False, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=opt_window):
                for i in range(spin._couplings.shape[0]):
                    dpg.add_table_column()

                with dpg.table_row():
                    for i in range(spin._couplings.shape[1]):
                        dpg.add_text(f"", tag=f'opt_intensities_{i}')

            dpg.add_text(default_value=f'Water Frequency', tag='opt_wf')
            
            dpg.add_text(default_value=f'Water Intensity', tag='opt_wi')

            dpg.add_text(default_value=f'Water Half-Height Width', tag='opt_whhw')

            dpg.add_text(default_value=f'Spectral Width', tag='opt_sw')

            dpg.add_text(default_value=f'Observation Frequency', tag='opt_obs')

            dpg.add_text('Half-Height Width:', tag='opt_hhw_title')
            with dpg.table(tag='opt_hhw_table', row_background=False, header_row=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=opt_window):
                for i in range(spin._couplings.shape[0]):
                    dpg.add_table_column()

                with dpg.table_row():
                    for i in range(spin._couplings.shape[1]):
                        dpg.add_text(f"", tag=f'opt_hhw_{i}')
        with dpg.value_registry():
            dpg.add_bool_value(default_value=False, tag='opt_series_added')
    else:
        dpg.show_item('opt_window')

    dpg.fit_axis_data("opt_x_axis")
    
    dpg.add_menu_item(label='Show Optimization Graph', callback=show_item_callback, user_data='opt_window', parent='view_menu')
    dpg.add_menu_item(label='Show Optimization Parameters', callback=show_item_callback, user_data='opt_params_window', parent='view_menu')

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
    
    if simulate_water:
        param_bounds : list[tuple[float, float]] = [(-100, 100)] * len(spin._couplings.flatten()) + \
                                                [(-1000, 1000)] * spin._nuclei_number + [(water_left, water_right)] + [(-1000, 1000)] + \
                                                [(0.5, 100)] + [(1e-6, 1e6)] + [(1e-6, 1e6)] + [(0.5, 100)] * spin._nuclei_number
    else:
        param_bounds : list[tuple[float, float]] = [(-100, 100)] * len(spin._couplings.flatten()) + \
                                                [(-1000, 1000)] * spin._nuclei_number + \
                                                [(1e-6, 1e6)] + [(1e-6, 1e6)] + [(0.5, 100)] * spin._nuclei_number
    
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
            dpg.bind_item_theme('region_line_left', Theme.region_theme())
            dpg.bind_item_theme('region_line_right', Theme.region_theme())

        full_x = nmr_array[0]

        def quadrant_objective(params):
            if simulate_water:
                couplings, intensities, water_freq, water_intensity, water_hhw, spec_width, obs, hhw = unpack_params_water(params, matrix_size, matrix_shape)
                new_spin = Spin(spin_names, list(spin._ppm_nuclei_frequencies), couplings, list(hhw), spin.field_strength)
                simulation = simulate_peaklist(new_spin.peaklist(list(intensities)), len(real_x),
                                            list(hhw), (real_x[0],real_x[-1]))
                new_water = Water(water_freq, water_intensity, water_hhw, water_enable=True)
                water_simulation_full = simulate_peaklist(new_water.peaklist, len(full_x), new_water.hhw, (full_x[0], full_x[-1]))
                water_y_quadrant = np.interp(real_x, full_x, water_simulation_full[1][::-1])
                sim_y = list(np.ascontiguousarray(simulation[1][::-1] + water_y_quadrant))

                dpg.set_value('opt_wf', f'Water Frequency {water_freq}')
                dpg.set_value('opt_wi', f'Water Intensity: {water_intensity}')
                dpg.set_value('opt_whhw', f'Water Half-Height Width: {water_hhw}')
            else:
                couplings, intensities, spec_width, obs, hhw = unpack_params(params, matrix_size, matrix_shape)
                new_spin = Spin(spin_names, list(spin._ppm_nuclei_frequencies), couplings, list(hhw), spin.field_strength)
                simulation = simulate_peaklist(new_spin.peaklist(list(intensities)), len(real_x),
                                            list(hhw), (real_x[0],real_x[-1]))
                sim_y = list(np.ascontiguousarray(simulation[1][::-1]))

            for i in range(matrix_shape[0]):
                for j in range(matrix_shape[1]):
                    dpg.set_value(f'opt_coupling_{i}_{j}', f"{couplings[i][j]}")
            for i in range(matrix_shape[0]):
                dpg.set_value(f'opt_intensities_{i}', f"{intensities[i]}")
            dpg.set_value('opt_sw', f"Spectral Width: {spec_width:.03f}")
            dpg.set_value('opt_obs', f"Observation Frequency: {spec_width:.03f}")
            for i in range(matrix_shape[0]):
                dpg.set_value(f'opt_hhw_{i}', f"{hhw[i]}")

            if not dpg.does_item_exist('sim_opt_series'):
                dpg.add_line_series(real_x, sim_y, label='Simulation Slice', parent='opt_y_axis', tag='sim_opt_series')
                dpg.bind_item_theme("sim_opt_series", Theme.sim_plot_theme())
            else:
                dpg.set_value('sim_opt_series', [real_x, sim_y])

            if not dpg.does_item_exist('real_opt_series'):
                dpg.add_line_series(real_x, real_y, label='Real Slice', parent='opt_y_axis', tag='real_opt_series')
                dpg.bind_item_theme("real_opt_series", Theme.nmr_plot_theme())
            else:
                dpg.set_value('real_opt_series', [real_x, real_y])

            return np.sqrt(np.mean((sim_y - real_y) ** 2))
        
        result = minimize(quadrant_objective, init_params, method='L-BFGS-B', bounds=param_bounds)
        optimized_params_list.append(result.x)
        init_params = result.x

    nuclei_quadrant_indices = []
    for quadrant in quadrants:
        start, end = quadrant
        quadrant_range = (nmr_array[0][start], nmr_array[0][end-1])
        indices_in_quadrant = [
            idx for idx, freq in enumerate(spin._nuclei_frequencies)
            if min(quadrant_range) <= freq <= max(quadrant_range)
        ]
        nuclei_quadrant_indices.append(indices_in_quadrant)

    # for idx, quadrant in enumerate(nuclei_quadrant_indices):
    #     print(f"Quadrant {idx + 1}:", file=stderr, end=' ')
    #     for j in range(len(quadrant)):
    #         print(f"{quadrant[j]}", file=stderr, end=" ")
    #     print("", file=stderr)

    if simulate_water:
        couplings_list = []
        intensities_list = [] 
        hhw_list = []

        for opt_param in optimized_params_list:
            c, i, _, _, _, _, _, hhw = unpack_params_water(opt_param, matrix_size, matrix_shape)
            couplings_list.append(c)
            intensities_list.append(i)
            hhw_list.append(hhw)

        # Combine couplings and intensities from each quadrant using nuclei_quadrant_indices
        new_couplings = np.zeros_like(spin._couplings)
        new_intensities = np.zeros(spin._nuclei_number)
        new_hhw = np.zeros(spin._nuclei_number)

        for q_idx, indices in enumerate(nuclei_quadrant_indices):
            for i in indices:
                # For couplings, copy the row and column for each nucleus in this quadrant
                new_couplings[i, :] = couplings_list[q_idx][i, :]
                # For intensities, copy the value for each nucleus in this quadrant
                new_intensities[i] = intensities_list[q_idx][i]
                # For half_height_widths, copy the value for each nucleus in this quadrant
                new_hhw[i] = hhw_list[q_idx][i]

        _, _, new_water_freq, new_water_intensity, new_water_hhw, new_sw, new_obs, _ = unpack_params_water(optimized_params_list[0], matrix_size, matrix_shape)

        optimized_params = np.concatenate((new_couplings.flatten(), new_intensities, [new_water_freq, new_water_intensity, new_water_hhw, new_sw, new_obs], new_hhw))

    else:
        couplings_list = []
        intensities_list = [] 
        hhw_list = []
        
        for opt_param in optimized_params_list:
            c, i, _, _, hhw = unpack_params(opt_param, matrix_size, matrix_shape)
            couplings_list.append(c)
            intensities_list.append(i)
            hhw_list.append(hhw)

        # Combine couplings and intensities from each quadrant using nuclei_quadrant_indices
        new_couplings = np.zeros_like(spin._couplings)
        new_intensities = np.zeros(spin._nuclei_number)
        new_hhw = np.zeros(spin._nuclei_number)

        for q_idx, indices in enumerate(nuclei_quadrant_indices):
            for i in indices:
                # For couplings, copy the row and column for each nucleus in this quadrant
                new_couplings[i, :] = couplings_list[q_idx][i, :]
                # For intensities, copy the value for each nucleus in this quadrant
                new_intensities[i] = intensities_list[q_idx][i]
                # For half_height_widths, copy the value for each nucleus in this quadrant
                new_hhw[i] = hhw_list[q_idx][i]

        _, _, new_sw, new_obs, _ = unpack_params(optimized_params_list[0], matrix_size, matrix_shape)

        # Use the last optimized parameters for other values
        optimized_params = np.concatenate((new_couplings.flatten(), new_intensities, [new_sw, new_obs], new_hhw))

    if dpg.does_item_exist('region_line_left'):
        dpg.delete_item('region_line_left')
    if dpg.does_item_exist('region_line_right'):
        dpg.delete_item('region_line_right')

    return optimized_params


def optimize_simulation(nmr_file : str, spin : Spin, water_range : tuple[float, float], water : "Water | None" = None) -> "Spin | tuple[Spin, Water]":
    from simulate.water import Water
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
    specValHz : list[float] = [ppm * spin._field_strength for ppm in specValPPM]

    freq_limits : list[float] = [specValHz[0], specValHz[-1]]
    freq_limits.sort()

    nmr_array = np.vstack((specValHz, df.array))

    if water is not None:
        simulate_water = True
        initial_values : list[float] = [water.frequency, water.intensity, water.hhw, init_sw, init_obs]
    else:
        initial_values : list[float] = [init_sw, init_obs]
        simulate_water = False

    initial_intensities = [1.0] * spin._nuclei_number
    matrix_shape = spin._couplings.shape
    matrix_size : int = spin._couplings.size 
    
    init_params : np.ndarray = np.concatenate((spin._couplings.flatten(), initial_intensities, initial_values, spin._half_height_width))

    optimized_params = section_optimization(nmr_array, spin, matrix_shape, matrix_size, init_params, water_range, simulate_water)
    
    if simulate_water:
        new_couplings, new_intensities, new_water_freq, new_water_intensity, new_water_hhw, new_spec_width, new_obs, new_hhw = unpack_params_water(optimized_params, matrix_size, matrix_shape)

        optimized_spin = Spin(spin.spin_names, spin._ppm_nuclei_frequencies, new_couplings, list(new_hhw), spin._field_strength, list(new_intensities))
        optimized_water = Water(new_water_freq, new_water_intensity, new_water_hhw, True)

        print('Optimization Complete!', file=stderr)
        return optimized_spin, optimized_water
    else:
        new_couplings, new_intensities, new_spec_width, new_obs, new_hhw = unpack_params(optimized_params, matrix_size, matrix_shape)
        
        optimized_spin = Spin(spin.spin_names, spin._ppm_nuclei_frequencies, new_couplings, list(new_hhw), spin._field_strength, list(new_intensities))
        print('Optimization Complete!', file=stderr)
        return optimized_spin


def optimize_callback(sender, app_data, user_data : "UI"):
    if not hasattr(user_data, "spin_file") or not user_data.spin_file:
        print("Failed to Optimize! Missing Requirement: spin_file", file=stderr)
        return
    if not hasattr(user_data, "nmr_file") or not user_data.nmr_file:
        print("Failed to Optimize! Missing Requirement: nmr_file", file=stderr)
        return
    
    nmr_file : str = user_data.nmr_file
    spin_matrix_file : str = user_data.spin_file
    field_strength : float = user_data.sim_settings['field_strength']
    if len(user_data.water_range) == 2:
        water_range : tuple[float, float] = user_data.water_range
    elif len(user_data.water_range) > 2:
        water_range : tuple[float, float] = (user_data.water_range[0], user_data.water_range[1])
    else:
        raise ValueError("Water range is invalid. Water range must be two values!")
    
    init_hhw : list[float | int] = user_data.spin.half_height_width

    if dpg.does_item_exist('water_drag_left'):
        dpg.hide_item('water_drag_left')
    if dpg.does_item_exist('water_center_line'):
        dpg.hide_item('water_center_line')
    if dpg.does_item_exist('water_drag_right'):
        dpg.hide_item('water_drag_right')

    if user_data.sim_settings['use_settings']:
        initial_spin = user_data.spin
    else:
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(spin_matrix_file)
        initial_spin = Spin(spin_names, nuclei_frequencies, couplings, half_height_width=init_hhw, field_strength=field_strength)

    if user_data.water_sim.water_enable:
        optimizations = optimize_simulation(nmr_file, initial_spin, water_range, user_data.water_sim)
    else:
        optimizations = optimize_simulation(nmr_file, initial_spin, water_range, None)

    if isinstance(optimizations, Spin):
        optimized_spin = optimizations
        optimized_water = user_data.water_sim
    else:
        optimized_spin = optimizations[0]
        optimized_water = optimizations[1]

    setattr(user_data, "spin", optimized_spin)
    setattr(user_data, "water_sim", optimized_water)

    update_simulation_plot(optimized_spin, user_data.points, optimized_water, optimized_spin.half_height_width, optimized_spin._nuclei_number)
    update_plotting_ui(user_data)
    zoom_subplots_to_peaks(user_data)


def unpack_params(params : np.ndarray | list, matrix_size : int, matrix_shape : tuple):
    cMatrix_flat = np.array(params[:matrix_size])
    intensities = np.array(params[matrix_size:matrix_size+matrix_shape[0]])

    sw, obs = params[matrix_size+matrix_shape[0]:matrix_size+matrix_shape[0]+2]
    w = params[matrix_size+matrix_shape[0]+2:]

    return cMatrix_flat.reshape(matrix_shape), intensities, sw, obs, w
    
def unpack_params_water(params : np.ndarray | list, matrix_size : int, matrix_shape : tuple):
    cMatrix_flat = np.array(params[:matrix_size])
    intensities = np.array(params[matrix_size:matrix_size+matrix_shape[0]])

    water_freq, water_intensity, water_hhw = params[matrix_size+matrix_shape[0]:matrix_size+matrix_shape[0]+3]
    sw, obs = params[matrix_size+matrix_shape[0]+3:matrix_size+matrix_shape[0]+5]
    w = params[matrix_size+matrix_shape[0]+5:]

    return cMatrix_flat.reshape(matrix_shape), intensities, water_freq, water_intensity, water_hhw, sw, obs, w