from sys import stderr
import dearpygui.dearpygui as dpg

from spin.spin import Spin, loadSpinFromFile
from .plot import ( add_subplots, update_plot_callback, set_nmr_plot_values, 
                     zoom_subplots_to_peaks, update_simulation_plot, fit_axes ) 
from .nmr import load_nmr_array
from .callbacks import set_points_callback, set_water_range_callback
from scipy.signal import find_peaks
from numpy import argmax

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    from ui.components import Button

def set_spin_file(sender, app_data : dict, user_data : "UI") -> None:
    """
    Sets the spin file of a UI object to the selected file path.
    Additionally trigger plot update and set spin value.
    Optionally triggers a plot update.
    """
    file : str = app_data['file_path_name']
    ui : "UI" = user_data

    if not file:
        print("No file found, skipping update...", file=stderr)
        return 

    ui.spin_file = file
    
    spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
    spin = Spin(spin_names, nuclei_frequencies, couplings)
    ui.spin = spin

    add_subplots(ui)
    zoom_subplots_to_peaks(ui)
    update_plot_callback(sender, app_data, ui)

def set_nmr_file_callback(sender, app_data, user_data : "UI") -> None:
    """
    Sets the NMR file attribute and optionally updates the NMR plot.
    """
    file = app_data['file_path_name']

    user_data.nmr_file = file

    field_strength : float = getattr(user_data, 'field_strength', 500.0)
    nmr_array = load_nmr_array(file, field_strength)
    user_data.points = len(nmr_array[0])

    if dpg.get_value('main_plot_added'):
        update_simulation_plot(user_data.spin, user_data.points, user_data.spin.half_height_width, 
                           user_data.spin._nuclei_number)
    set_nmr_plot_values(nmr_array)

    optimize_button : "Button | None" = user_data.buttons.get('optimize', None)
    fit_axes_button : "Button | None" = user_data.buttons.get('fit_axes', None)

    if (optimize_button is not None) and dpg.get_value('main_plot_added') and not optimize_button.is_enabled:
            optimize_button.enable()
    if (fit_axes_button is not None) and not fit_axes_button.is_enabled:
            fit_axes_button.enable()

    fit_axes({"x_axis": "main_x_axis", "y_axis": "main_y_axis"})

    highest_peak_index = argmax(nmr_array[1])
    water_peak_x_value = nmr_array[0][highest_peak_index]

    set_water_range_callback(sender, water_peak_x_value-100.0, (user_data, 'left'))
    set_water_range_callback(sender, water_peak_x_value+100.0, (user_data, 'right'))
    
    dpg.show_item('water_drag_left')
    dpg.show_item('water_center_line')
    dpg.show_item('water_drag_right')