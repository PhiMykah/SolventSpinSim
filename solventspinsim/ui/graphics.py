from pathlib import Path
import os
import dearpygui.dearpygui as dpg
import numpy as np

def load_static_texture(file : str, texture_tag : int | str = 0) -> int | str:
    if not Path(file).is_file():
        print(f"CWD: {os.getcwd()}")
        raise FileNotFoundError(f"Loading Texture Failed! File not found: {file}")
    with dpg.texture_registry():
        image_width, image_height, image_channels, image_buffer = dpg.load_image(file)
        return dpg.add_static_texture(image_width, image_height, image_buffer, tag=texture_tag)

def plot_window() -> None:
    with dpg.plot(label="Plot", height=400, width=400):
        dpg.add_plot_legend()
        
        x = []
        y = []
        for i in range(0, 500):
            x.append(i / 1000)
            y.append(0.5 + 0.5 * np.sin(50 * i / 1000))
            
        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")

        # series belong to a y axis
        dpg.add_line_series(x,y , label="test", parent="y_axis", tag="main_plot")