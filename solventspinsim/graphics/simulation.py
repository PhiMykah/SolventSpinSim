import dearpygui.dearpygui as dpg

from .graphics import Graphic
from callbacks import (help_msg, set_field_strength_callback, 
                          set_points_callback, set_intensity_callback, 
                          set_hhw_callback)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui import UI

class SimulationSettings(Graphic):

    field_strength_tag : str = 'field_strength'
    points_tag : str = 'points'
    intensity_tag : str = 'intensity'
    hhw_tag : str = 'hhw'
    use_settings_tag : str = 'use_settings'

    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, is_enabled : bool = False, 
                 field_strength : float = 500.0, points : int = 1000, 
                 intensity : float = 1.0, half_height_width : float = 1.0, 
                 use_settings : bool = False) -> None:
        self.params = {
            SimulationSettings.field_strength_tag : field_strength, # Field strength of system in Hz
            SimulationSettings.points_tag : points, # Number of points in System
            SimulationSettings.intensity_tag : intensity, # Average intensity of peaks
            SimulationSettings.hhw_tag : half_height_width, # Average half_height_width
            SimulationSettings.use_settings_tag : use_settings # Whether or not to use settings for optimization
        }

        super().__init__(ui, parent, is_enabled)

    def render(self) -> None:
        if self.is_rendered:
            return 
        
        dpg.add_text(default_value='Simulation Settings', tag='sim_settings_title', parent=self.parent)

        field_strength, points, intensity, half_height_width, use_settings = self.params.keys()
        with dpg.value_registry():
            dpg.add_float_value(default_value=self.params[field_strength], tag=f"{field_strength}_value")
            dpg.add_int_value(default_value=self.params[points], tag=f"{points}_value")
            dpg.add_float_value(default_value=self.params[intensity], tag=f"{intensity}_value")
            dpg.add_float_value(default_value=self.params[half_height_width], tag=f"{half_height_width}_value")
            dpg.add_bool_value(default_value=self.params[use_settings], tag=f"{use_settings}_value")

        with dpg.table(header_row=False, parent=self.parent):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_input_float(label='Field Strength', source=f"{field_strength}_value", format="%.02f", step=1, 
                                    step_fast=10, tag=field_strength, callback=set_field_strength_callback,
                                    user_data=self.ui)
                help_msg("Field Strength in Hz of the magnet to simulate.")

                dpg.add_input_int(label='Points', source=f"{points}_value", step=1, step_fast=100, 
                                tag=points, callback=set_points_callback, user_data=self.ui)
                help_msg("Number of points in entire spectrum to simulate.")

            with dpg.table_row():
                dpg.add_input_float(label='Intensity', source=f"{intensity}_value", format="%.02f", step=1,
                                    step_fast=10, tag=intensity, callback=set_intensity_callback,
                                    user_data=self.ui)
                help_msg("Maximum starting intensity for each peak.")

                dpg.add_drag_float(label='Half-Height Width', source=f"{half_height_width}_value", format="%.02f", 
                                   speed=0.1, tag=half_height_width, callback=set_hhw_callback, user_data=self.ui)
                help_msg("Width of the peak lorentzian at half-height.")

            with dpg.table_row():
                dpg.add_checkbox(label="Optimize with Current Settings", tag=use_settings, source=f"{use_settings}_value", 
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
        self.params[SimulationSettings.points_tag] = value
        dpg.set_value(SimulationSettings.points_tag, value)