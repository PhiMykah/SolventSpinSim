from sys import stderr
import dearpygui.dearpygui as dpg
import numpy as np

from ui.components import Button
from simulate.simulate import simulate_peaklist

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    from spin.spin import Spin
    from typing import Any

COUPLING_DRAG_HEIGHT = -0.01

def add_subplots(ui : "UI") -> None:
    """
    Assumes that ui.spin has been set and main plot has been set
    """
    n_peaks : int = len(ui.spin.spin_names)
    if n_peaks != ui.spin._nuclei_number:
        raise ValueError(f"Number of spin nuclei {n_peaks} not equal to nuclei count {ui.spin._nuclei_number}!")
    
    if ui.window is None:
        print("Unable to add subplots to main window, since it does not exist for UI object.", file=stderr)
        return 
    
    # Subplots for each peak
    with dpg.subplots(rows=1, columns=n_peaks, label="##peak_sub_plots", width=-1, height=400, 
                      tag='subplots', parent=ui.window, link_rows=True, before='matrix_group') as subplots_tag:
        for i, spin_name in enumerate(ui.spin.spin_names):
            with dpg.plot(label=f"Nuclei {spin_name}", tag=f"peak_plot_{i}"):
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag=f"peak_x_axis_{i}")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag=f"peak_y_axis_{i}")

    dpg.configure_item('main_plot', before='peak_plot_0')
    ui.subplots_tag = subplots_tag

    # Store subplot tags in UI for later updates
    ui.plot_tags = {
        "main": {"plot": "main_plot", "x_axis": "main_x_axis", "y_axis": "main_y_axis"},
        "peaks": [
            {"plot": f"peak_plot_{i}", "x_axis": f"peak_x_axis_{i}", "y_axis": f"peak_y_axis_{i}"}
            for i in range(n_peaks)
        ]
    }

def zoom_subplots_to_peaks(ui: "UI", padding: float = 10.0):
    """
    Sets the x-axis limits for each subplot to zoom around the peaks associated with each spin nucleus.
    Uses the coupling matrix to determine the outer limits.
    """
    nuclei_freqs = ui.spin.nuclei_frequencies
    couplings = np.array(ui.spin.couplings)
    n = len(nuclei_freqs)

    for i in range(n):
        nucleus_freq = nuclei_freqs[i]
        # Get all non-zero couplings for this nucleus
        nonzero_couplings = np.abs(couplings[i][couplings[i] != 0])
        if nonzero_couplings.size > 0:
            max_coupling = np.max(nonzero_couplings)
            min_x = nucleus_freq - max_coupling - padding
            max_x = nucleus_freq + max_coupling + padding
        else:
            # No couplings, just center around nucleus_freq
            min_x = nucleus_freq - padding
            max_x = nucleus_freq + padding

        # Optionally, set y-axis limits as well (here, just a default range)
        min_y = -0.1
        max_y = 1.1

        # Set axis limits for subplot i
        dpg.set_axis_limits(f"peak_x_axis_{i}", min_x, max_x)
        dpg.set_axis_limits(f"peak_y_axis_{i}", min_y, max_y)
        
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
        from .matrix import matrix_table, load_table
        matrix_table(ui)
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
            tag : str = f"nuclei_{p}_{ui.spin.spin_names[i]}"
            dpg.add_drag_line(label=f"Nuclei {ui.spin.spin_names[i]}", color=color, tag=tag,
                    callback=update_drag_item, user_data=(ui, tag, (i,)), default_value=nuclei, parent=plot)

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
                                    callback=update_drag_item, user_data=(ui, right_tag, (i, col_index)),
                                    default_value=right_coords, parent=plot)
                    dpg.add_drag_point(label=f'Coupling {spin_col}-{spin_row}', color=coupling_color, tag=left_tag,
                                    callback=update_drag_item, user_data=(ui, left_tag, (i, col_index)), 
                                    default_value=left_coords, parent=plot)
            
    dpg.set_value("drag_lines_visible", True)
    dpg.set_value("drag_points_visible", True)


def update_drag_item(sender, app_data, user_data : tuple["UI", "str", "tuple"]):
    """
    Unified update for drag lines and drag points across all plots.
    If a drag line is changed, update all associated drag points.
    If a drag point is changed, update the corresponding drag line and mirrored drag point.
    `indices` should be (i,) for drag line, (i, j) for drag point.
    """
    ui: "UI" = user_data[0]
    tag : str = user_data[1]
    indices : "tuple[Any, ...]" = user_data[2]

    plot_tags = [ui.plot_tags["main"]["plot"]] + [p["plot"] for p in ui.plot_tags["peaks"]]
    n = len(ui.spin.spin_names)

    if tag.startswith("nuclei_"):
        # Drag line update
        i = indices[0]
        new_value = dpg.get_value(sender)
        ui.spin._nuclei_frequencies[i] = new_value

        # Update all drag lines for this nucleus
        for p in range(len(plot_tags)):
            nuclei_tag = f"nuclei_{p}_{ui.spin.spin_names[i]}"
            if dpg.does_item_exist(nuclei_tag):
                dpg.set_value(nuclei_tag, new_value)

            # Update associated drag points
            for j in range(n):
                for tag_type, sign in (("r", 1), ("l", -1)):
                    drag_tag = f'coupling_drag_{p}{tag_type}_{i}_{j}'
                    if dpg.does_item_exist(drag_tag):
                        coupling_value = ui.spin._couplings[i][j]
                        dpg.set_value(drag_tag, (new_value + sign * coupling_value, COUPLING_DRAG_HEIGHT))

        # Simulate and zoom
        update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width, ui.spin._nuclei_number)
        zoom_subplots_to_peaks(ui)

    elif tag.startswith("coupling_drag_"):
        # Drag point update
        i, j = indices
        nuclei_value = ui.spin._nuclei_frequencies[i]
        new_x_value, _ = dpg.get_value(sender)
        offset = new_x_value - nuclei_value
        # Update drag point
        dpg.set_value(tag, (new_x_value, COUPLING_DRAG_HEIGHT))
        # Find mirrored drag point
        tag_type = tag.split('_')[2][1] # 'r' or 'l'
        current_plot = int(tag.split('_')[2][0]) if tag.split('_')[2][0].isdigit() else 0
        mirrored_type = 'l' if tag_type == 'r' else 'r'
        mirrored_tag = f'coupling_drag_{current_plot}{mirrored_type}_{i}_{j}'
        other_x_value = nuclei_value - offset if new_x_value > nuclei_value else nuclei_value + abs(offset)
        if dpg.does_item_exist(mirrored_tag):
            dpg.set_value(mirrored_tag, (other_x_value, COUPLING_DRAG_HEIGHT))
        for p in range(len(plot_tags)):
            if p == current_plot:
                continue
            tag = f'coupling_drag_{p}{tag_type}_{i}_{j}'
            mirrored_tag = f'coupling_drag_{p}{mirrored_type}_{i}_{j}'
            dpg.set_value(tag, (new_x_value, COUPLING_DRAG_HEIGHT))
            dpg.set_value(mirrored_tag, (other_x_value, COUPLING_DRAG_HEIGHT))

        # Update coupling matrix
        ui.spin._couplings[i][j] = offset
        ui.spin._couplings[j][i] = offset
        # Update matrix table
        dpg.set_value(f'coupling_{j}_{i}', offset)
        dpg.set_value(f'coupling_{i}_{j}', offset)
        # Update drag lines for this nucleus
        for p in range(len(plot_tags)):
            nuclei_tag = f"nuclei_{p}_{ui.spin.spin_names[i]}"
            if dpg.does_item_exist(nuclei_tag):
                dpg.set_value(nuclei_tag, nuclei_value)
        # Simulate and zoom
        update_simulation_plot(ui.spin, ui.points, ui.spin.half_height_width, ui.spin._nuclei_number)
        zoom_subplots_to_peaks(ui)
    
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
    if dpg.get_value('main_plot_added'):
        dpg.set_value('main_plot_series', [x_data, y_data])
    else:
        dpg.add_line_series(x_data, y_data, label="Simulation", parent="main_y_axis", tag="main_plot_series")
        dpg.set_value('main_plot_added', True)

    if dpg.get_value('peak_plot_added'):
        for i in range(peak_count):
            dpg.set_value(f"peak_plot_series_{i}", [x_data, y_data])
    else:
        for i in range(peak_count):
            dpg.add_line_series(x_data, y_data, label=f'##peak_plot_{i}', parent=f"peak_y_axis_{i}", tag=f"peak_plot_series_{i}")
        dpg.set_value('peak_plot_added', True)

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
        dpg.add_line_series(nmr_array[0], nmr_array[1], label='Real Data', parent="main_y_axis", tag="nmr_plot")

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
            tag = f"nuclei_{p}_{ui.spin.spin_names[i]}"
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
