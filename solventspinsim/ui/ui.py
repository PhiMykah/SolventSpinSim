import dearpygui.dearpygui as dpg
from ui.themes import Theme
from ui.graphics import plot_window, simulation_settings
from ui.callbacks import set_spin_file, set_nmr_file_callback, test_callback, fit_axes, show_item_callback
from ui.components import Button
from spin.spin import Spin
from optimize.optimize import optimize_callback
from pathlib import Path
ASSETS_DIR = (Path(__file__).parent.parent / 'assets').resolve() # Directory of all package assets

class UI:
    """
    Class containing the graphics user interfase handling functions
    """
    def __init__(self, title : str = 'Viewport'):
        self.title : str = title
        self.spin_file : str = ""
        self.nmr_file : str = ""
        self.mat_table : str | None = None
        self.field_strength : float = 500.0
        self.spin = Spin()
        self.window = None
        self.disabled_theme = None
        self.buttons: dict[str, Button] = {}
        self._points : int = 1000
        self.subplots_tag : str = ""
        self.plot_tags : dict = {}
        pass        

    # ---------------------------------------------------------------------------- #
    #                              Getters and Setters                             #
    # ---------------------------------------------------------------------------- #

    @property
    def points(self) -> int:
        return self._points
    
    @points.setter
    def points(self, value) -> None:
        self._points = value
        dpg.set_value("points", value)
    
    # ---------------------------------------------------------------------------- #
    #                              Main Render Window                              #
    # ---------------------------------------------------------------------------- #
    
    def main_window(self) -> None:
        """
        Initialize main window

        Assumes dearpygui's context has been created
        """
            
        with dpg.file_dialog(directory_selector=False, show=False, callback=set_spin_file, width=800, height=400, 
                             user_data=self) as load_file_dialog:
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension("Text Files (*.txt *.csv){.txt,.csv}", color=(0, 255, 255, 255)) 

        with dpg.file_dialog(directory_selector=False, show=False, callback=set_nmr_file_callback, width=800, height=400,
                             user_data=self) as load_nmr_dialog:
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension("FT1 Files (*.ft1){.ft1,}", color=(0, 255, 255, 255))

        with dpg.window(label='Primary Window') as main_window:
            self.window = main_window
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Load Spin Matrix", callback=lambda: dpg.show_item(load_file_dialog), check=False)
                    dpg.add_menu_item(label="Load NMR File", callback=lambda: dpg.show_item(load_nmr_dialog), check=False)
                dpg.add_menu_item(label="Help", callback=test_callback)

                with dpg.menu(label="Widget Items"):
                    dpg.add_checkbox(label="Pick Me", callback=test_callback)
                    dpg.add_button(label="Press Me", callback=test_callback)
                    dpg.add_color_picker(label="Color Me", callback=test_callback)
                
                with dpg.menu(label='View'):
                    dpg.add_menu_item(label='Show Spin Matrix Table', callback=show_item_callback, user_data='matrix_window')

            simulation_settings(self)

            self.buttons['optimize'] = Button(label='Optimize', callback=optimize_callback, user_data=self, enabled=False)

            plot_window(self)            

            self.buttons['fit_axes'] = Button(label='Fit Axes', 
                                              callback= lambda : fit_axes({"x_axis": "main_x_axis", "y_axis": "main_y_axis"}), 
                                              enabled=False)
            
        # dpg.set_viewport_resize_callback(callback=viewport_resize_callback)   
        dpg.set_primary_window(main_window, True)
        
    def run(self, **viewport_kwargs) -> None:
        """
        Load and run the UI components

        Parameters
        ----------
        
        **kwargs
            Keyword arguments for dearpygui.dearpygui.create_viewport function

        Notes
        -----
        Do not include `decorated` keyword argument, as it is included in functon
        """
        dpg.create_context()
        Theme.disabled_theme()
        Theme.red_line_theme()
        dpg.create_viewport(title=self.title, decorated=True, **viewport_kwargs)
        dpg.setup_dearpygui()

        self.main_window()

        dpg.show_viewport()
        dpg.start_dearpygui()        