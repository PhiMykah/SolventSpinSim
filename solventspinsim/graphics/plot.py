import dearpygui.dearpygui as dpg

from .graphics import Graphic
from callbacks import set_water_range_callback

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui import UI

class PlotWindow(Graphic):

    main_plot_tag : str = 'main_plot'
    main_x_axis_tag : str = 'main_x_axis'
    main_y_axis_tag : str = 'main_y_axis'

    def __init__(self, ui : "UI | None" = None, parent : str | int | None = None, 
                 is_enabled : bool = False, height : int = 400, x_axis_label : str = 'x', 
                 y_axis_label : str = 'y') -> None:
        self.params = {
            PlotWindow.main_plot_tag : height,
            PlotWindow.main_x_axis_tag : x_axis_label, 
            PlotWindow.main_y_axis_tag : y_axis_label, 
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
        
    def update_ui_values(self) -> None:
        main_plot, main_x_axis, main_y_axis = self.params.keys()
        
        dpg.configure_item(main_plot, height=self.params[PlotWindow.main_plot_tag])
        dpg.configure_item(main_x_axis, label=self.params[main_x_axis])
        dpg.configure_item(main_y_axis, label=self.params[main_y_axis])