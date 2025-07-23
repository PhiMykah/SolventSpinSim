from operator import call
from pathlib import Path
from turtle import width
import dearpygui
import dearpygui.dearpygui as dpg
from simulate.simulate import simulate_peaklist
from spin.spin import Spin, loadSpinFromFile, ppm_to_hz
from sys import stderr
import nmrPype
import numpy as np
from ui.components import Button
from typing import TYPE_CHECKING
from .themes import Theme
if TYPE_CHECKING:
    from ui.ui import UI

COUPLING_DRAG_HEIGHT = -0.1

# ---------------------------------------------------------------------------- #
#                              Callback Functions                              #
# ---------------------------------------------------------------------------- #

# ---------------------- Utility and Debug Callbacks ------------------------- #

def test_callback(sender, app_data, user_data) -> None:
    """Debug callback to print sender, app_data, and user_data."""
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

def close_application(sender, app_data, user_data) -> None:
    """Callback to close all windows and the viewport."""
    dpg.stop_dearpygui()

def viewport_resize_callback(sender, app_data, user_data) -> None:
    """Callback to handle viewport resizing events."""
    current_width = dpg.get_viewport_width()
    current_height = dpg.get_viewport_height()
    print(f"Viewport resized to: Width={current_width}, Height={current_height}")

def help_msg(message) -> None:
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text("(?)", color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)

# ---------------------- File Selection Callbacks ---------------------------- #

def set_file_callback(sender, app_data : dict, user_data : tuple["UI", str, str]) -> None:
    """
    Sets the attribute of a UI object to the selected file path.
    Optionally triggers a plot update.
    """
    file : str = app_data['file_path_name']
    ui : "UI" = user_data[0]
    attr : str = user_data[1]
    update_callback = user_data[2]

    setattr(ui, attr, file)

    if update_callback:
        update_plot_callback(sender, app_data, (file, ui))

def set_nmr_file_callback(sender, app_data, user_data : "tuple[UI, str, bool]") -> None:
    """
    Sets the NMR file attribute and optionally updates the NMR plot.
    """
    file = app_data['file_path_name']
    ui = user_data[0]
    attr = user_data[1]

    setattr(ui, attr, file)


    field_strength : float = getattr(user_data[0], 'field_strength', 500.0)
    nmr_array = load_nmr_array(file, field_strength)
    ui.points = len(nmr_array[0])
    if user_data[2]:
        set_nmr_plot_values(nmr_array)

# ---------------------- Plot Update Callbacks ------------------------------- #

def update_plot_callback(sender, app_data, user_data: "UI | tuple[str, UI]") -> None:
    """
    Updates the simulation plot based on the provided user_data.
    Handles multiple input formats for user_data.
    """
    ui : "UI | None" = None
    if hasattr(user_data, 'spin_file') and not isinstance(user_data, tuple):
        # UI component with spin_file attribute
        ui = user_data
        if not user_data.spin_file:
            print("No file found, skipping update...", file=stderr)
            return 
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        setattr(ui, "spin", spin)

    elif isinstance(user_data, tuple) and len(user_data) == 2:
        # Tuple: (str, UI)
        file = user_data[0]
        ui = user_data[1]

        setattr(ui, 'spin_file', file)
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        setattr(ui, "spin", spin)

    else:
        print(f"Failure to update plot. User_data of incorrect format. user_data: {user_data}", file=stderr)
        return
    
    if ui is not None:
        optimize_button : Button | None = ui.buttons.get('optimize', None)
        fit_axes_button : Button | None = ui.buttons.get('fit_axes', None)

        if optimize_button is not None:
            optimize_button.enable()
        
        if fit_axes_button is not None:
            fit_axes_button.enable()

    update_simulation_plot(spin, ui.points, spin.half_height_width)
    fit_axes()
    create_drag_lines(ui)
    if ui is not None:
        load_table(sender, app_data, ui)

def create_drag_lines(ui : "UI") -> None:
    if dpg.get_value('drag_lines_visible'):
        return
    
    nuclei_frequencies = ui.spin.nuclei_frequencies
    couplings = np.array(ui.spin.couplings)
    for i, nuclei in enumerate(nuclei_frequencies):
        # Create a color gradient from blue to red as i increases
        n = len(nuclei_frequencies)
        r = int(255 * i / max(n - 1, 1))
        g = 0
        b = int(255 * (1 - i / max(n - 1, 1)))
        color : list[int] = [r, g, b, 255]
        dpg.add_drag_line(label=f"Nuclei {ui.spin.spin_names[i]}", color=color, tag=f"nuclei_{ui.spin.spin_names[i]}",
                  callback=update_spin_nuclei, user_data=(ui, i), default_value=nuclei, parent='plt')

        if dpg.get_value("drag_points_visible"):
            continue

        for j in range(n - i):
            col_index = n - 1 - j
            value = couplings[i][col_index]
            g = int(255 * j / max(n - 1, 1))
            coupling_color : list[int] = [r, g, b, 255]
            if value != 0.0:
                spin_row = ui.spin.spin_names[i]
                spin_col = ui.spin.spin_names[col_index]
                right_coords = (nuclei + value, COUPLING_DRAG_HEIGHT)
                left_coords = (nuclei - value, COUPLING_DRAG_HEIGHT)
                right_tag = f'coupling_drag_r_{i}_{col_index}'
                left_tag = f'coupling_drag_l_{i}_{col_index}'
                dpg.add_drag_point(label=f'Coupling {spin_row}-{spin_col}', color=coupling_color, tag=right_tag,
                                   callback=update_coupling, user_data=(ui, (i, col_index), left_tag),
                                   default_value=right_coords, parent='plt')
                dpg.add_drag_point(label=f'Coupling {spin_col}-{spin_row}', color=coupling_color, tag=left_tag,
                                   callback=update_coupling, user_data=(ui, (i, col_index), right_tag), 
                                   default_value=left_coords, parent='plt')
            
    dpg.set_value("drag_lines_visible", True)
    dpg.set_value("drag_points_visible", True)

def update_spin_nuclei(sender, app_data, user_data : "tuple[UI, int]"):
    ui : "UI" = user_data[0] # UI object containing spin matrix to handle changes 
    index : int = user_data[1] # Nuclei frequency index

    new_value = dpg.get_value(sender)
    # Set new nuclei frequency value 
    ui.spin._nuclei_frequencies[index] = new_value

    # Update all coupling drag points related to this nuclei frequency to move alongside this drag line
    n = len(ui.spin.spin_names)
    for j in range(n):
        if j == index:
            continue
        # Update both left and right drag points for this nuclei frequency
        for tag_type, sign in (('r', 1), ('l', -1)):
            tag = f'coupling_drag_{tag_type}_{index}_{j}'
            if dpg.does_item_exist(tag):
                coupling_value = ui.spin._couplings[index][j]
                dpg.set_value(tag, (new_value + sign * coupling_value, COUPLING_DRAG_HEIGHT))

    # Simulate new spectrum and plot
    update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width)

def update_coupling(sender, app_data, user_data : "tuple[UI, tuple[int, int], str]"):
    ui : "UI" = user_data[0] # UI object containing spin matrix to handle changes 
    cell_row, cell_col = user_data[1] # coupling row and column indices
    nuclei_value: float = ui.spin._nuclei_frequencies[cell_row]
    other_drag_point: str = user_data[2] # string id of mirrored drag point

    new_x_value, _ = dpg.get_value(sender)
    offset : float = new_x_value - nuclei_value # Offset coupling value from nuclei center 

    dpg.set_value(sender, (new_x_value, COUPLING_DRAG_HEIGHT)) # Update drag point to stay with consistent y value

    # Set mirrored drag point to the right or left based on current drag point
    other_x_value: float = nuclei_value - offset if new_x_value > nuclei_value else nuclei_value + abs(offset)
    dpg.set_value(other_drag_point, (other_x_value, COUPLING_DRAG_HEIGHT))

    # Set new coupling value on both sides of the diagonal
    ui.spin._couplings[cell_row][cell_col] = offset
    ui.spin._couplings[cell_col][cell_row] = offset

    # Set values on matrix table
    dpg.set_value(f'coupling_{cell_col}_{cell_row}', offset)
    dpg.set_value(f'coupling_{cell_row}_{cell_col}', offset)

    # Simulate new spectrum and plot
    update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width)
    
def fit_axes() -> None:
    """Fits the axes to the current data."""
    dpg.fit_axis_data("x_axis")
    dpg.fit_axis_data("y_axis")
    dpg.reset_axis_limits_constraints("x_axis")
    dpg.reset_axis_limits_constraints("y_axis")

def set_plot_values(simulation : "np.ndarray") -> None:
    """
    Sets the simulation data to the main plot.
    """
    x_data, y_data = simulation[0], simulation[1]
    if dpg.does_item_exist('main_plot'):
        dpg.set_value('main_plot', [x_data, y_data])
    else:
        dpg.add_line_series(x_data, y_data, label="Simulation", parent="y_axis", tag="main_plot")

def set_nmr_plot_values(nmr_array : "np.ndarray") -> None:
    """
    Sets the NMR data to the plot.
    Assumes nmr_array is C-contiguous.
    """
    if not dpg.does_item_exist('main_plot'):
        return
    
    if dpg.does_item_exist('nmr_plot'):
        dpg.set_value('nmr_plot', [nmr_array[0], nmr_array[1]])
    else:
        dpg.add_line_series(nmr_array[0], nmr_array[1], label='Real Data', parent="y_axis", tag="nmr_plot")

def update_simulation_plot(spin : "Spin", points : int, hhw : int | float) -> None:
    """
    Simulates the spectrum and updates the plot for the given UI object.    
    """
    simulation = simulate_peaklist(spin.peaklist(), points, hhw)
    set_plot_values(simulation)

def update_plotting_ui(ui: "UI") -> None:
    """
    Updates all drag lines and drag points to reflect the current spin state.
    """
    n = len(ui.spin.spin_names)
    nuclei_frequencies = ui.spin.nuclei_frequencies
    couplings = np.array(ui.spin.couplings)

    # Update drag lines for nuclei frequencies
    for i, nuclei in enumerate(nuclei_frequencies):
        tag = f"nuclei_{ui.spin.spin_names[i]}"
        # Find drag line by label (since tag is label)
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, nuclei)

    # Update drag points for couplings
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            value = couplings[i][j]
            nuclei = nuclei_frequencies[i]
            right_tag = f'coupling_drag_r_{i}_{j}'
            left_tag = f'coupling_drag_l_{i}_{j}'
            if dpg.does_item_exist(right_tag):
                dpg.set_value(right_tag, (nuclei + value, COUPLING_DRAG_HEIGHT))
            if dpg.does_item_exist(left_tag):
                dpg.set_value(left_tag, (nuclei - value, COUPLING_DRAG_HEIGHT))


# ---------------------- Attribute Setter Callback --------------------------- #

def setter_callback(sender, app_data, user_data : tuple[object, str]) -> None:
    """
    Sets the attribute `user_data[1]` of object `user_data[0]` to value app_data.
    """
    setattr(user_data[0], user_data[1], app_data)

def set_points_callback(sender, app_data, user_data : "UI") -> None:
    user_data.points = app_data
    if not user_data.spin.spin_names:
        return
    update_simulation_plot(user_data.spin, user_data.points, user_data.spin.half_height_width)

def set_field_strength_callback(sender, app_data, user_data : "UI") -> None:
    user_data.field_strength = app_data
    if not user_data.spin.spin_names:
        return
    user_data.spin.field_strength = app_data
    user_data.spin.nuclei_frequencies = user_data.spin._ppm_nuclei_frequencies

    update_simulation_plot(user_data.spin, user_data.points, user_data.spin.half_height_width)
    update_plotting_ui(user_data)

# ---------------------- NMR Data Loading ------------------------------------ #

def load_nmr_array(nmr_file : str, field_strength : float) -> np.ndarray:
    """
    Loads NMR data from file and returns a 2D array of (Hz, intensity).
    """
    df = nmrPype.DataFrame(nmr_file)

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")
    
    x_vals = np.arange(1, len(df.array)+1)

    init_sw: float = df.getParam("NDSW") 
    init_obs: float = df.getParam("NDOBS")
    init_orig: float = df.getParam("NDORIG")
    init_size: float = df.getParam("NDSIZE")

    init_sw  = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta: float = -init_sw/(init_size)
    first: float = init_orig - delta*(init_size - 1)

    specValPPM  = (first + (x_vals - 1.0)*delta)/init_obs

    specValHz : list[float] = [ppm * field_strength for ppm in specValPPM]
    return np.vstack((specValHz, df.array))

# ---------------------- Table Loading and Modification ---------------------- #

def load_table(sender, app_data, user_data : "UI") -> None:
    """
    Loads the spin coupling matrix into a DearPyGui table for editing.
    """
    ui : "UI" = user_data

    min_value : float = dpg.get_value('table_min_freq')
    max_value : float = dpg.get_value('table_max_freq')

    if not hasattr(ui, 'spin') or not ui.spin:
        return
    spin : Spin = ui.spin

    if hasattr(ui, 'mat_table') and ui.mat_table is not None:
        for i,row in enumerate(np.array(spin.couplings)):
            for j, col in enumerate(row):
                dpg.configure_item(f'coupling_{i}_{j}', min_value=min_value, max_value=max_value)
        return

    table_tag = 'matrix_table'

    if not spin.spin_names or not spin.nuclei_frequencies:
        return
    
    if ui.window is None:
        return
    
    with dpg.table(tag=table_tag, header_row=True, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=ui.window):
        dpg.add_table_column(label="##Top Left Corner")
        for atom in spin.spin_names:
            dpg.add_table_column(label=str(atom))

        for i, row in enumerate(np.array(spin.couplings)):
            with dpg.table_row():
                dpg.add_text(spin.spin_names[i], tag=f'row_{i}_header')
                for j, col in enumerate(row):
                    default_val = col
                    if i != j:
                        dpg.add_drag_float(label=f'##coupling_{i}_{j}', tag=f'coupling_{i}_{j}', width=-1, 
                                        min_value=min_value, max_value=max_value, default_value=default_val,
                                        user_data=(ui, j, i, ui.spin._nuclei_frequencies[i]), callback=modify_matrix)
                    else:
                        dpg.add_text(f"", label=f'##coupling_{i}_{j}', tag=f'coupling_{i}_{j}')

    ui.mat_table = table_tag

def modify_matrix(sender, app_data, user_data : "tuple[UI, int, int, float]") -> None:
    """
    Modifies the spin coupling matrix value at (j, i) with the new value.
    """
    spin : Spin = user_data[0].spin
    j : int = user_data[1]
    i : int = user_data[2]
    nuclei = user_data[3]
    value = app_data

    spin._couplings[j][i] = value
    dpg.set_value(f'coupling_{j}_{i}', value)

    for tag_type, sign in (('r', 1), ('l', -1)):
        for a, b in ((i, j), (j, i)):
            tag = f'coupling_drag_{tag_type}_{a}_{b}'
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, (nuclei + sign * value, COUPLING_DRAG_HEIGHT))
                break

    f'coupling_drag_l_{i}_{j}'
    spin._couplings[i][j] = value
    update_simulation_plot(spin, user_data[0].points, spin.half_height_width)