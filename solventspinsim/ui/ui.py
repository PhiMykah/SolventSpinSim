import dearpygui.dearpygui as dpg
from ui.callbacks import *
import ui.configs as configs
from ui.graphics import load_static_texture
from pathlib import Path

ASSETS_DIR = (Path(__file__).parent.parent / 'assets').resolve() # Directory of all package assets

class UI:
    """
    Class containing the graphics user interfase handling functions
    """
    def __init__(self, title : str = 'Viewport'):
        self.title=title
        pass        

    def main_window(self) -> None:
        """
        Initialize main window

        Assumes dearpygui's context has been created
        """
        with dpg.window(label='Primary Window') as main_window:
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Save", callback=test_callback)
                    dpg.add_menu_item(label="Save As", callback=test_callback)

                    with dpg.menu(label="Settings"):
                        dpg.add_menu_item(label="Setting 1", callback=test_callback, check=True)
                        dpg.add_menu_item(label="Setting 2", callback=test_callback)

                dpg.add_menu_item(label="Help", callback=test_callback)

                with dpg.menu(label="Widget Items"):
                    dpg.add_checkbox(label="Pick Me", callback=test_callback)
                    dpg.add_button(label="Press Me", callback=test_callback)
                    dpg.add_color_picker(label="Color Me", callback=test_callback)

            dpg.add_text("Hello world")
            dpg.add_button(label="Test Me!", callback=test_callback)
            dpg.add_input_text(label="string")
            dpg.add_slider_float(label="float")
            
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