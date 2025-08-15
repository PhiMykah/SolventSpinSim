from operator import call
from pathlib import Path
import os
import dearpygui.dearpygui as dpg

from ui.components import Button
from ui.callbacks import (load_table, help_msg, set_field_strength_callback, 
                          set_points_callback, set_hhw_callback, set_intensity_callback,
                          set_water_range_callback, test_callback)
from optimize.optimize import optimize_callback
from ui.themes import Theme

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

class Graphic():
    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, is_enabled : bool = False) -> None:
        if ui is not None:
            self.ui : "UI" = ui
        if parent is not None:
            self.parent : str | int = parent

        self.is_enabled : bool = is_enabled
        self.is_rendered = False
        if not hasattr(self, 'params'):
            self.params : dict = {}

        if ui is not None or parent is not None:
            self.render()

    def render(self) -> None:
        pass 

    def disable(self) -> None:
        for tag in self.params.keys():
            if dpg.does_item_exist(tag):
                dpg.disable_item(tag)
                dpg.bind_item_theme(tag, Theme.disabled_theme())
        self.enabled = False

    def enable(self) -> None:
        for tag in self.params.keys():
            if dpg.does_item_exist(tag):
                dpg.enable_item(tag)
                dpg.bind_item_theme(tag, "")
        self.enabled = True

    def toggle(self) -> None:
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def __getitem__(self, key):
        return self.params[key]

    def __setitem__(self, key, value):
        self.params[key] = value

    def get(self, key, default = None):
        return self.params.get(key, default)

class PlotWindow(Graphic):
    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, 
                 is_enabled : bool = False, height : int = 400, x_axis_label : str = 'x', 
                 y_axis_label : str = 'y') -> None:
        self.params = {
            'main_plot': height,
            'main_x_axis' : x_axis_label, 
            'main_y_axis' : y_axis_label, 
        }

        super().__init__(ui, parent, is_enabled)
        
    def render(self) -> None:
        # Main plot
        main_plot, main_x_axis, main_y_axis = self.params.keys()
        with dpg.plot(label="Spectrum & Peaks", tag=main_plot, width=-1, height=self.params[main_plot]):
            dpg.add_plot_legend()
            # REQUIRED FOR PLOTTING: create x and y axes
            dpg.add_plot_axis(dpg.mvXAxis, label=self.params[main_x_axis], tag=main_x_axis)
            dpg.add_plot_axis(dpg.mvYAxis, label=self.params[main_y_axis], tag=main_y_axis)
        
        with dpg.value_registry():
            dpg.add_bool_value(default_value=False, tag="drag_lines_visible")
            dpg.add_bool_value(default_value=False, tag="drag_points_visible")
            dpg.add_bool_value(default_value=False, tag='main_plot_added')
            dpg.add_bool_value(default_value=False, tag='peak_plot_added')
        
        dpg.add_drag_line(label=f"Water Left Limit", tag='water_drag_left', show=False,
                        color=(255, 255, 255, 255),
                        callback=set_water_range_callback, user_data=(self.ui, 'left'),
                        default_value=dpg.get_value("water_left_value"), parent='main_plot')
        
        center = (dpg.get_value("water_left_value") + dpg.get_value("water_right_value")) / 2

        dpg.add_drag_line(label=f"Water Center Line", tag='water_center_line', color=(255, 255, 255, 50),
                        show=False, default_value=center, parent='main_plot', no_inputs=True, no_cursor=True)
        
        dpg.add_drag_line(label=f"Water Right Limit", tag='water_drag_right', show=False,
                        color=(255, 255, 255, 255),
                        callback=set_water_range_callback, user_data=(self.ui, 'right'), 
                        default_value=dpg.get_value("water_right_value"), parent='main_plot')


class SimulationSettings(Graphic):
    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, is_enabled : bool = False, 
                 field_strength : float = 500.0, points : int = 1000, 
                 intensity : float = 1.0, half_height_width : float = 1.0, 
                 use_settings : bool = False) -> None:
        self.params = {
            'field_strength': field_strength, # Field strength of system in Hz
            'points' : points, # Number of points in System
            'intensity' : intensity, # Average intensity of peaks
            'hhw' : half_height_width, # Average half_height_width
            'use_settings' : use_settings # Whether or not to use settings for optimization
        }

        super().__init__(ui, parent, is_enabled)

    def render(self) -> None:
        if self.is_rendered:
            return 
        
        dpg.add_text(default_value='Simulation Settings', tag='sim_settings_title', parent=self.parent)

        field_strength, points, intensity, half_height_width, use_settings = self.params.keys()
        with dpg.table(header_row=False, parent=self.parent):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_input_float(label='Field Strength', default_value=self.params[field_strength], format="%.02f", step=1, 
                                    step_fast=10, tag=field_strength, callback=set_field_strength_callback,
                                    user_data=self.ui)
                help_msg("Field Strength in Hz of the magnet to simulate.")

                dpg.add_input_int(label='Points', default_value=self.params[points], step=1, step_fast=100, 
                                tag=points, callback=set_points_callback, user_data=self.ui)
                help_msg("Number of points in entire spectrum to simulate.")

            with dpg.table_row():
                dpg.add_input_float(label='Intensity', default_value=self.params[intensity], format="%.02f", step=1,
                                    step_fast=10, tag=intensity, callback=set_intensity_callback,
                                    user_data=self.ui)
                help_msg("Maximum starting intensity for each peak.")

                dpg.add_drag_float(label='Half-Height Width', default_value=self.params[half_height_width], format="%.02f", 
                                   speed=0.1, tag=half_height_width, callback=set_hhw_callback, user_data=self.ui)
                help_msg("Width of the peak lorentzian at half-height.")

            with dpg.table_row():
                dpg.add_checkbox(label="Optimize with Current Settings", tag=use_settings, 
                                callback=lambda sender, value, ui : setattr(ui, "use_settings", value),
                                user_data=self.ui, default_value=self.params[use_settings])
                help_msg("Utilize current simulation settings as initial parameters for optimization")

        if self.is_enabled: 
            self.enable()
        else:
            self.disable()   
        self.is_rendered = True

    @property
    def points(self) -> int:
        if not hasattr(self, 'params'):
            return 1000
        return self.params.get('points', 1000)
    
    @points.setter
    def points(self, value) -> None:
        self.params['points'] = value
        dpg.set_value("points", value)

class OptimizationSettings(Graphic):
    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, is_enabled : bool = False, 
                 water_left : float = 0.0, water_right : float = 100.0) -> None:
        self.params = {
            "water_left": water_left, 
            "water_right" : water_right,
        }

        super().__init__(ui, parent, is_enabled)

    def render(self) -> None:
        dpg.add_text(default_value='Optimization Settings', tag='opt_settings_title', parent=self.parent)

        water_left, water_right = self.params.keys()
        with dpg.value_registry():
            dpg.add_float_value(default_value=self.params['water_left'], tag="water_left_value")
            dpg.add_float_value(default_value=self.params['water_right'], tag="water_right_value")

        with dpg.table(header_row=False, parent=self.parent):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_drag_float(label='Water Left Limit', format="%.02f", source='water_left_value',
                                tag=water_left, callback=set_water_range_callback, user_data=(self.ui, 'left'))
                help_msg("Leftmost region of the water signal peak")

                dpg.add_drag_float(label='Water Right Limit', format="%.02f", source='water_right_value',
                                tag=water_right, callback=set_water_range_callback, user_data=(self.ui, 'right'))
                help_msg("Rightmost region of the water signal peak")
        
        self.ui.buttons['optimize'] = Button(label='Optimize', callback=optimize_callback, user_data=self.ui, enabled=False, parent=self.parent)