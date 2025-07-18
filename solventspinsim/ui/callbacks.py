from pathlib import Path
import dearpygui.dearpygui as dpg
from simulate.simulate import simulate_peaklist
from spin.spin import Spin, loadSpinFromFile
from sys import stderr
import nmrPype
import numpy as np

# ---------------------------------------------------------------------------- #
#                              Callback Functions                              #
# ---------------------------------------------------------------------------- #

def test_callback(sender, app_data, user_data) -> None:
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

# Callback to close all windows and the viewport
def close_application(sender, app_data, user_data) -> None:
    dpg.stop_dearpygui()

# Callback to resize viewport and perform other
def viewport_resize_callback(sender, app_data, user_data) -> None:
    current_width = dpg.get_viewport_width()
    current_height = dpg.get_viewport_height()
    print(f"Viewport resized to: Width={current_width}, Height={current_height}")

def set_file_callback(sender, app_data : dict, user_data : tuple) -> None:
    """
    Sets the user_data[1] attribute of user_data[0] to the file from app_data,
    Assumes that the function parent has a file_path_name attribute and
    that user_data[0] has attribute user_data[1]

    Updates the plot if user_data (bool) is True
    """
    file : str = app_data['file_path_name']
    ui : str = user_data[0]
    attr : str = user_data[1]
    update_callback = user_data[2]

    setattr(ui, attr, file)

    if update_callback:
        update_plot_callback(sender, app_data, (file, ui))

def set_nmr_file_callback(sender, app_data, user_data) -> None:
    file = app_data['file_path_name']
    obj = user_data[0]
    attr = user_data[1]

    setattr(obj, attr, file)

    if hasattr(user_data[0], 'field_strength'):
        field_strength = user_data[0].field_strength
    else:
        field_strength = 500.0

    if user_data[2]:
        nmr_array = load_nmr_array(file, field_strength)
        set_nmr_plot_values(nmr_array)

def update_plot_callback(sender, app_data, user_data) -> None:
    if hasattr(user_data, 'spin_file'):
        # Obtain simulation from peak file if user_data is UI component
        if not user_data.spin_file:
            print("No file found, skipping update...", file=stderr)
            return 
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(user_data.spin_file)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        setattr(user_data, "spin", spin)
        simulation = simulate_peaklist(spin.peaklist(), 1000, spin.half_height_width)
    elif isinstance(user_data, str):
        file = Path(user_data)
        if not file.exists():
            print("No file found, skipping update...", file=stderr)
            return 
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(user_data)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        simulation = simulate_peaklist(spin.peaklist(), 1000, spin.half_height_width)
    elif isinstance(user_data, tuple) and len(user_data) == 2:
        ui = user_data[1]
        file = user_data[0]

        setattr(ui, 'spin_file', file)
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        setattr(ui, "spin", spin)
        simulation = simulate_peaklist(spin.peaklist(), 1000, spin.half_height_width)

    elif isinstance(user_data, tuple) and len(user_data) == 3:
        # Create simulation from tuple if user data is of format (Spin, float | int, float | int)
        spin, points, hhw = user_data
        if isinstance(spin, Spin) and isinstance(points, (int, float)) and isinstance(hhw, (int, float)):
            simulation = simulate_peaklist(spin.peaklist(), int(points), hhw)
        else:
            # Express error if the tuple is not correctly formatted
            print(f"Failure to update plot. User_data of incorrect format. user_data: {user_data}", file=stderr)
            return
    else:
        # Express error if update_data isn't of proper format
        print(f"Failure to update plot. User_data of incorrect format. user_data: {user_data}", file=stderr)
        return

    set_plot_values(simulation)

def set_plot_values(simulation) -> None:
    x_data, y_data = simulation[0], simulation[1]
    if dpg.does_item_exist('main_plot'):
        dpg.set_value('main_plot', [x_data, y_data])
    else:
        dpg.add_line_series(x_data, y_data, label="Simulation", parent="y_axis", tag="main_plot")

def fit_axes() -> None:
    dpg.fit_axis_data("x_axis")
    dpg.fit_axis_data("y_axis")

def set_nmr_plot_values(nmr_array) -> None:
    """
    Assumes nmr_array is C-contiguous
    """
    if not dpg.does_item_exist('main_plot'):
        return
    
    if dpg.does_item_exist('nmr_plot'):
        dpg.set_value('nmr_plot', [nmr_array[0], nmr_array[1]])
    else:
        dpg.add_line_series(nmr_array[0], nmr_array[1], label='Real Data', parent="y_axis", tag="nmr_plot")

def setter_callback(sender, app_data, user_data):
    """
    Sets the attribute `user_data[1]` of object `user_data[0]` to value app_data
    """
    setattr(user_data[0], user_data[1], app_data)

def load_nmr_array(nmr_file : str, field_strength : float) -> np.ndarray:
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
    return np.vstack((specValHz, df.array))

def load_table(sender, app_data, user_data) -> None:
    ui = user_data

    if not hasattr(ui, 'mat_table') or not ui.mat_table:
        return

    table_tag : str | int = ui.mat_table

    if not hasattr(ui, 'spin') or not ui.spin:
        return
    spin : Spin = ui.spin

    if not spin.spin_names or not spin.nuclei_frequencies:
        return
    
    min_value : float = dpg.get_value('table_min_freq')
    max_value : float = dpg.get_value('table_max_freq')

    with dpg.table(tag=table_tag, header_row=True, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=ui.window):
        for atom in spin.spin_names:
            dpg.add_table_column(label=str(atom))

        for i, row in enumerate(np.array(spin.couplings)):
            with dpg.table_row():
                for j, col in enumerate(row):
                    default_val = col
                    dpg.add_slider_float(label=f'##coupling_{i}_{j}', width=-1, min_value=min_value, default_value=default_val,
                                        user_data=(spin, j, i), callback=modify_matrix, max_value=max_value)

def modify_matrix(sender, app_data, user_data : tuple[Spin, int, int]) -> None:
    spin = user_data[0] 
    j = user_data[1]
    i = user_data[2]
    value = app_data

    spin._couplings[j][i] = value