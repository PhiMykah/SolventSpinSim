import dearpygui.dearpygui as dpg
from spin.spin import Spin
from ui.callbacks import *
import ui.configs as configs
from ui.graphics import load_static_texture, plot_window
from pathlib import Path

ASSETS_DIR = (Path(__file__).parent.parent / 'assets').resolve() # Directory of all package assets

class UI:
    """
    Class containing the graphics user interfase handling functions
    """
    def __init__(self, title : str = 'Viewport'):
        self.title : str = title
        self.spin_file : str = ""
        pass        

    def main_window(self) -> None:
        """
        Initialize main window

        Assumes dearpygui's context has been created
        """
        
        with dpg.file_dialog(directory_selector=False, show=False, callback=set_file_callback, width=800, height=400, 
                             user_data=(self, 'spin_file')) as load_file_dialog:
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension("Text Files (*.txt *.csv){.txt,.csv}", color=(0, 255, 255, 255)) 

        with dpg.window(label='Primary Window') as main_window:
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Load Spin Matrix", callback=lambda: dpg.show_item(load_file_dialog), check=False)

                dpg.add_menu_item(label="Help", callback=test_callback)

                with dpg.menu(label="Widget Items"):
                    dpg.add_checkbox(label="Pick Me", callback=test_callback)
                    dpg.add_button(label="Press Me", callback=test_callback)
                    dpg.add_color_picker(label="Color Me", callback=test_callback)

            dpg.add_text("Hello world")
            dpg.add_button(label='Update Plot', callback=update_plot, user_data=self)
            dpg.add_button(label="Test Me!", callback=test_callback)
            dpg.add_input_text(label="string")
            dpg.add_slider_float(label="float")
            plot_window()            

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