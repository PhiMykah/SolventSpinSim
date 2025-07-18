import dearpygui.dearpygui as dpg
from ui.callbacks import *
from ui.graphics import matrix_table_settings, plot_window
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
        self.mat_table = ""
        self.field_strength : float = 500.0
        self.spin = Spin()
        self.window = None
        pass        

    def main_window(self) -> None:
        """
        Initialize main window

        Assumes dearpygui's context has been created
        """
        
        with dpg.file_dialog(directory_selector=False, show=False, callback=set_file_callback, width=800, height=400, 
                             user_data=(self, 'spin_file', True)) as load_file_dialog:
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension("Text Files (*.txt *.csv){.txt,.csv}", color=(0, 255, 255, 255)) 

        with dpg.file_dialog(directory_selector=False, show=False, callback=set_nmr_file_callback, width=800, height=400,
                             user_data=(self, 'nmr_file', True)) as load_nmr_dialog:
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

            dpg.add_input_float(label='Field Strength', default_value=500.0, format="%.02f", step=1, 
                                step_fast=10, tag='field_strength', callback=setter_callback,
                                user_data=(self, 'field_strength'), tracked=True, width=200)
            dpg.add_button(label='Optimize', callback=optimize_callback, user_data=self)

            plot_window()            

            dpg.add_button(label='Fit Axes', callback=fit_axes)

            dpg.add_separator()

            self.mat_table : str = matrix_table_settings(self)
            
            
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
        dpg.create_viewport(title=self.title, decorated=True, **viewport_kwargs)
        dpg.setup_dearpygui()

        self.main_window()

        dpg.show_viewport()
        dpg.start_dearpygui()        