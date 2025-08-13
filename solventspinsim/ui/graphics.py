from operator import call
from pathlib import Path
import os
import dearpygui.dearpygui as dpg

from ui.components import Button
from ui.callbacks import (load_table, help_msg, set_field_strength_callback, 
                          set_points_callback, set_hhw_callback, set_intensity_callback,
                          set_water_range_callback, test_callback)
from optimize.optimize import optimize_callback

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI

def load_static_texture(file : str, texture_tag : int | str = 0) -> int | str:
    if not Path(file).is_file():
        print(f"CWD: {os.getcwd()}")
        raise FileNotFoundError(f"Loading Texture Failed! File not found: {file}")
    with dpg.texture_registry():
        image_width, image_height, image_channels, image_buffer = dpg.load_image(file)
        return dpg.add_static_texture(image_width, image_height, image_buffer, tag=texture_tag)

def plot_window(ui : "UI") -> None:
    # Main plot
    with dpg.plot(label="Spectrum & Peaks", tag='main_plot', width=-1, height=400):
        dpg.add_plot_legend()
        # REQUIRED FOR PLOTTING: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="main_x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="main_y_axis")
    
    with dpg.value_registry():
        dpg.add_bool_value(default_value=False, tag="drag_lines_visible")
        dpg.add_bool_value(default_value=False, tag="drag_points_visible")
        dpg.add_bool_value(default_value=False, tag='main_plot_added')
        dpg.add_bool_value(default_value=False, tag='peak_plot_added')
    
    dpg.add_drag_line(label=f"Water Left Limit", tag='water_drag_left', show=False,
                      color=(255, 255, 255, 255),
                      callback=set_water_range_callback, user_data=(ui, 'left'),
                      default_value=dpg.get_value("water_left_value"), parent='main_plot')
    
    center = (dpg.get_value("water_left_value") + dpg.get_value("water_right_value")) / 2

    dpg.add_drag_line(label=f"Water Center Line", tag='water_center_line', color=(255, 255, 255, 50),
                      show=False, default_value=center, parent='main_plot', no_inputs=True, no_cursor=True)
    
    dpg.add_drag_line(label=f"Water Right Limit", tag='water_drag_right', show=False,
                      color=(255, 255, 255, 255),
                      callback=set_water_range_callback, user_data=(ui, 'right'), 
                      default_value=dpg.get_value("water_right_value"), parent='main_plot')
    
def simulation_settings(ui : "UI") -> None:
    dpg.add_text(default_value='Simulation Settings', tag='sim_settings_title')
    with dpg.table(header_row=False):
        dpg.add_table_column(width=100)
        dpg.add_table_column(width=100)

        with dpg.table_row():
            dpg.add_input_float(label='Field Strength', default_value=500.0, format="%.02f", step=1, 
                                step_fast=10, tag='field_strength', callback=set_field_strength_callback,
                                user_data=ui)
            help_msg("Field Strength in Hz of the magnet to simulate.")

            dpg.add_input_int(label='Points', default_value=1000, step=1, step_fast=100, 
                              tag='points', callback=set_points_callback, user_data=ui)
            help_msg("Number of points in entire spectrum to simulate.")
        with dpg.table_row():
            dpg.add_input_float(label='Intensity', default_value=1.0, format="%.02f", step=1,
                                step_fast=10, tag='intensity', callback=set_intensity_callback,
                                user_data=ui)
            help_msg("Maximum starting intensity for each peak.")
            dpg.add_drag_float(label='Half-Height Width', default_value=1.0, format="%.02f", speed=0.1,
                               tag='hhw', callback=set_hhw_callback,
                               user_data=ui)
            help_msg("Width of the peak lorentzian at half-height.")
        with dpg.table_row():
            dpg.add_checkbox(label="Optimize with Current Settings", tag='use_settings', 
                             callback=lambda sender, value, ui : setattr(ui, "use_settings", value),
                             user_data=ui)
            help_msg("Utilize current simulation settings as initial parameters for optimization")

def optimization_settings(ui : "UI") -> None:
    dpg.add_text(default_value='Optimization Settings', tag='opt_settings_title')

    with dpg.value_registry():
        dpg.add_float_value(default_value=0.0, tag="water_left_value")
        dpg.add_float_value(default_value=100.0, tag="water_right_value")

    with dpg.table(header_row=False):
        dpg.add_table_column(width=100)
        dpg.add_table_column(width=100)

        with dpg.table_row():
            dpg.add_drag_float(label='Water Left Limit', format="%.02f", source='water_left_value',
                               tag='water_left', callback=set_water_range_callback, user_data=(ui, 'left'))
            help_msg("Leftmost region of the water signal peak")

            dpg.add_drag_float(label='Water Right Limit', format="%.02f", source='water_right_value',
                               tag='water_right', callback=set_water_range_callback, user_data=(ui, 'right'))
            help_msg("Rightmost region of the water signal peak")
    
    ui.buttons['optimize'] = Button(label='Optimize', callback=optimize_callback, user_data=ui, enabled=False)