from pathlib import Path
import os
import dearpygui.dearpygui as dpg
from ui.callbacks import *

def load_static_texture(file : str, texture_tag : int | str = 0) -> int | str:
    if not Path(file).is_file():
        print(f"CWD: {os.getcwd()}")
        raise FileNotFoundError(f"Loading Texture Failed! File not found: {file}")
    with dpg.texture_registry():
        image_width, image_height, image_channels, image_buffer = dpg.load_image(file)
        return dpg.add_static_texture(image_width, image_height, image_buffer, tag=texture_tag)

def plot_window() -> None:
    with dpg.plot(label="Simulation & Target Plot", height=400, width=-1, tag='plt'):
        dpg.add_plot_legend()
        # REQUIRED FOR PLOTTING: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")

def matrix_table_settings(ui) -> str:
    table_tag = 'matrix_table'
    with dpg.table(header_row=False):
        dpg.add_table_column(width=100)
        dpg.add_table_column(width=100)
        dpg.add_table_column(width=100)

        with dpg.table_row():
            dpg.add_text('Minimum Frequency')
            dpg.add_text('Maximum Frequency')

        with dpg.table_row():
            dpg.add_slider_float(label='##Minimum Frequency', tag='table_min_freq', default_value=0.0, width=-1)
            dpg.add_slider_float(label='##Maximum Frequency', tag='table_max_freq', default_value=100.0, width=-1)
            dpg.add_button(label='Load Table', callback=load_table, user_data=ui)
            
    return table_tag