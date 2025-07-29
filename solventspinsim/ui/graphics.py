import enum
from pathlib import Path
import os
import dearpygui.dearpygui as dpg
from ui.callbacks import load_table, help_msg, set_field_strength_callback, set_points_callback, setter_callback, test_callback
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    import numpy as np

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
    
def simulation_settings(ui : "UI") -> None:
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
            