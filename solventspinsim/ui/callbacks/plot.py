import dearpygui.dearpygui as dpg
import numpy as np

from ui.components import Button
from simulate.simulate import simulate_peaklist

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    from spin.spin import Spin

COUPLING_DRAG_HEIGHT = -0.01

def add_subplots(ui : "UI") -> None:
    """
    Assumes that ui.spin has been set and main plot has been set
    """
    if not ui.subplots_tag:
        return
    
    n_peaks : int = len(ui.spin.spin_names)
    if n_peaks != ui.spin._nuclei_number:
        raise ValueError(f"Number of spin nuclei {n_peaks} not equal to nuclei count {ui.spin._nuclei_number}!")
    
    # Subplots for each peak
    for i in range(n_peaks):
        with dpg.plot(label=f"Peak {i+1}", tag=f"peak_plot_{i}", parent=ui.subplots_tag):
            dpg.add_plot_axis(dpg.mvXAxis, label="x", tag=f"peak_x_axis_{i}")
            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag=f"peak_y_axis_{i}")

    # Store subplot tags in UI for later updates
    ui.plot_tags = {
        "main": {"plot": "main_plot", "x_axis": "main_x_axis", "y_axis": "main_y_axis"},
        "peaks": [
            {"plot": f"peak_plot_{i}", "x_axis": f"peak_x_axis_{i}", "y_axis": f"peak_y_axis_{i}"}
            for i in range(n_peaks)
        ]
    }

def update_plot_callback(sender, app_data, user_data: "UI") -> None:
    """
    Updates the simulation plot based on the provided user_data.
    Handles multiple input formats for user_data.
    """
    ui = user_data

    if ui is not None:
        optimize_button : Button | None = ui.buttons.get('optimize', None)
        fit_axes_button : Button | None = ui.buttons.get('fit_axes', None)

        if optimize_button is not None:
            optimize_button.enable()
        
        if fit_axes_button is not None:
            fit_axes_button.enable()

    update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width, ui.spin._nuclei_number)
    fit_axes(ui.plot_tags["main"])
    create_drag_lines(ui)
    if ui is not None:
        from .matrix import load_table
        load_table(sender, app_data, ui)

def create_drag_lines(ui : "UI") -> None:
    if dpg.get_value('drag_lines_visible'):
        return
    
    nuclei_frequencies = ui.spin.nuclei_frequencies
    n = len(nuclei_frequencies)

    plot_tags = [ui.plot_tags["main"]["plot"]] + [p["plot"] for p in ui.plot_tags["peaks"]]

    couplings = np.array(ui.spin.couplings)
    for i, nuclei in enumerate(nuclei_frequencies):
        # Create a color gradient from blue to red as i increases
        r = int(255 * i / max(n - 1, 1))
        g = 0
        b = int(255 * (1 - i / max(n - 1, 1)))
        color : list[int] = [r, g, b, 100]
        for p, plot in enumerate(plot_tags):
            tag : str = f"nuclei_{p}{ui.spin.spin_names[i]}"
            dpg.add_drag_line(label=f"Nuclei {ui.spin.spin_names[i]}", color=color, tag=tag,
                    callback=update_spin_nuclei, user_data=(ui, i), default_value=nuclei, parent=plot)

        if dpg.get_value("drag_points_visible"):
            continue

        for j in range(n - i):
            col_index = n - 1 - j
            value = couplings[i][col_index]
            g = int(255 * j / max(n - 1, 1))
            coupling_color : list[int] = [r, g, b, 255]
            if value != 0.0:
                for p, plot in enumerate(plot_tags):
                    spin_row = ui.spin.spin_names[i]
                    spin_col = ui.spin.spin_names[col_index]
                    right_coords = (nuclei + value, COUPLING_DRAG_HEIGHT)
                    left_coords = (nuclei - value, COUPLING_DRAG_HEIGHT)
                    right_tag = f'coupling_drag_{p}r_{i}_{col_index}'
                    left_tag = f'coupling_drag_{p}l_{i}_{col_index}'
                    dpg.add_drag_point(label=f'Coupling {spin_row}-{spin_col}', color=coupling_color, tag=right_tag,
                                    callback=update_coupling, user_data=(ui, (i, col_index), left_tag),
                                    default_value=right_coords, parent=plot)
                    dpg.add_drag_point(label=f'Coupling {spin_col}-{spin_row}', color=coupling_color, tag=left_tag,
                                    callback=update_coupling, user_data=(ui, (i, col_index), right_tag), 
                                    default_value=left_coords, parent=plot)
            
    dpg.set_value("drag_lines_visible", True)
    dpg.set_value("drag_points_visible", True)

def update_spin_nuclei(sender, app_data, user_data : "tuple[UI, int]"):
    ui : "UI" = user_data[0] # UI object containing spin matrix to handle changes 
    index : int = user_data[1] # Nuclei frequency index

    plot_tags = [ui.plot_tags["main"]["plot"]] + [p["plot"] for p in ui.plot_tags["peaks"]]

    new_value = dpg.get_value(sender)
    # Set new nuclei frequency value 
    ui.spin._nuclei_frequencies[index] = new_value

    # Update all coupling drag points related to this nuclei frequency to move alongside this drag line
    n = len(ui.spin.spin_names)
    for j in range(n):
        if j == index:
            continue
        for p in range(len(plot_tags)):
            # Update both left and right drag points for this nuclei frequency
            for tag_type, sign in (('r', 1), ('l', -1)):
                tag = f'coupling_drag_{p}{tag_type}_{index}_{j}'
                if dpg.does_item_exist(tag):
                    coupling_value = ui.spin._couplings[index][j]
                    dpg.set_value(tag, (new_value + sign * coupling_value, COUPLING_DRAG_HEIGHT))

    # Simulate new spectrum and plot
    update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width,
                           ui.spin._nuclei_number)

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
    update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width, ui.spin._nuclei_number)
    
def fit_axes(plot_dict : dict) -> None:
    """Fits the axes to the current data."""
    dpg.fit_axis_data(plot_dict["x_axis"])
    dpg.fit_axis_data(plot_dict["y_axis"])
    dpg.reset_axis_limits_constraints(plot_dict["x_axis"])
    dpg.reset_axis_limits_constraints(plot_dict["y_axis"])

def set_plot_values(simulation : "np.ndarray", peak_count : int) -> None:
    """
    Sets the simulation data to the main plot.
    """
    x_data, y_data = simulation[0], simulation[1]
    if dpg.does_item_exist('main_plot'):
        dpg.set_value('main_plot', [x_data, y_data])
    else:
        dpg.add_line_series(x_data, y_data, label="Simulation", parent="y_axis", tag="main_plot_series")
    for i in range(peak_count):
        if dpg.does_item_exist(f"peak_plot_{i}"):
            dpg.set_value(f"peak_plot_{i}", [x_data, y_data])
        else:
            dpg.add_line_series(x_data, y_data, label=f'##peak_plot_{i}', parent=f"peak_y_axis_{i}", tag=f"peak_plot_{i}")

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

def update_simulation_plot(spin : "Spin", points : int, hhw : int | float, peak_count) -> None:
    """
    Simulates the spectrum and updates the plot for the given UI object.    
    """
    simulation = simulate_peaklist(spin.peaklist(), points, hhw)
    set_plot_values(simulation, peak_count)

def update_plotting_ui(ui: "UI") -> None:
    """
    Updates all drag lines and drag points to reflect the current spin state.
    """
    n = len(ui.spin.spin_names)
    nuclei_frequencies = ui.spin.nuclei_frequencies
    couplings = np.array(ui.spin.couplings)

    # Update drag lines for nuclei frequencies
    for i, nuclei in enumerate(nuclei_frequencies):
        for p in range(n):
            tag = f"nuclei_{p}{ui.spin.spin_names[i]}"
            # Find drag line by label (since tag is label)
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, nuclei)

    # Update drag points for couplings
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for p in range(n):
                value = couplings[i][j]
                nuclei = nuclei_frequencies[i]
                right_tag = f'coupling_drag_{p}r_{i}_{j}'
                left_tag = f'coupling_drag_{p}l_{i}_{j}'
                if dpg.does_item_exist(right_tag):
                    dpg.set_value(right_tag, (nuclei + value, COUPLING_DRAG_HEIGHT))
                if dpg.does_item_exist(left_tag):
                    dpg.set_value(left_tag, (nuclei - value, COUPLING_DRAG_HEIGHT))
