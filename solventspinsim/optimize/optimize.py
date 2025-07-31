import numpy as np
import nmrPype
from scipy.optimize import dual_annealing, differential_evolution
from simulate.simulate import simulate_peaklist
from optimize.types import PeakArray
from ui.callbacks import set_nmr_plot_values, set_plot_values, zoom_subplots_to_peaks
from spin.spin import Spin, loadSpinFromFile
from sys import stderr

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

    # ppm_first = df.getParam()
    # ppm_last = df.getParam()

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

    # initial_matrix
    initial_values = [init_sw, init_obs, init_hhw]
    points = len(nmr_array[0])
    params = np.concatenate((nuclei_frequencies, couplings.flatten(), initial_values))
    matrix_shape = couplings.shape
    matrix_size = couplings.size

    freq_bounds = [(0, 20.0)] * num_of_freq
    matrix_bounds = [(0, 20.0)] * matrix_size
    sw_bounds = [(0,100.0)] 
    obs_bounds = [(0,100.0)]
    w_bounds = [(1,10.0)]

    bounds = freq_bounds + matrix_bounds + sw_bounds + obs_bounds + w_bounds

    result = differential_evolution(objective_function, bounds, (nmr_array, spin, num_of_freq, matrix_shape, matrix_size, points, freq_limits))

    optimized_params = result.x
    
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