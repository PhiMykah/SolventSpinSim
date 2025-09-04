from pathlib import Path

import dearpygui.dearpygui as dpg
from solventspinsim.callbacks import (
    fit_axes,
    load_dialog_callback,
    load_settings_dialog,
    nmr_file_dialog,
    save_dialog_callback,
    save_optimization_dialog,
    save_settings_dialog,
    show_item_callback,
    spin_file_dialog,
    test_callback,
)
from solventspinsim.graphics import (
    OptimizationSettings,
    PlotWindow,
    SimulationSettings,
    WaterSettings,
)
from solventspinsim.settings import Settings
from solventspinsim.simulate import Water
from solventspinsim.spin import Spin

from .components import Button
from .themes import Theme, change_theme_callback

ASSETS_DIR = (
    Path(__file__).parent.parent / "assets"
).resolve()  # Directory of all package assets


class UI:
    """
    Class containing the graphics user interfase handling functions
    """

    def __init__(self, title: str = "Viewport", settings: Settings = Settings()):
        self.title = title
        self.settings: Settings = settings
        self.spin_file: str = settings["spin_file"]
        self.nmr_file: str = settings["nmr_file"]
        self.output_file: str = settings["output_file"]
        self.mat_table: str = ""
        self.spin = Spin(**settings["spin"])
        self.window = None
        self.disabled_theme = None
        self.buttons: dict[str, Button] = {}
        self.subplots_tag: str = ""
        self.plot_tags: dict = {}
        self.water_range: tuple[float, float] | tuple[float, ...] = settings[
            "water_range"
        ]
        self.sim_settings = SimulationSettings()
        self.opt_settings = OptimizationSettings(**settings["opt_settings"])
        self.plot_window: PlotWindow = PlotWindow(**settings["plot_window"])
        self.water_sim: Water = Water(**settings["water_sim"])

    # ---------------------------------------------------------------------------- #
    #                              Getters and Setters                             #
    # ---------------------------------------------------------------------------- #

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        from solventspinsim.main import DPGStatus

        if isinstance(value, str):
            self._title: str = value
        else:
            self._title: str = "Viewport"
        if (
            DPGStatus.is_viewport_enabled()
            and self.window
            and dpg.does_item_exist(self.window)
        ):
            dpg.set_viewport_title(self._title)

    @property
    def points(self) -> int:
        return self.sim_settings.points

    @points.setter
    def points(self, value) -> None:
        self.sim_settings.points = value

    # ---------------------------------------------------------------------------- #
    #                              Main Render Window                              #
    # ---------------------------------------------------------------------------- #

    def main_window(self) -> None:
        """
        Initialize main window

        Assumes dearpygui's context has been created
        """
        Theme.main_themes()
        Theme.disabled_theme()
        Theme.sim_plot_theme()
        Theme.nmr_plot_theme()
        Theme.region_theme()

        dpg.bind_theme(Theme.main_themes("dark"))

        self.water_sim = Water()

        load_file = spin_file_dialog(self)
        load_nmr = nmr_file_dialog(self)
        save_opt = save_optimization_dialog(self)
        save_settings = save_settings_dialog(self)
        load_settings = load_settings_dialog(self)

        with dpg.window(label="Primary Window", width=1080, height=720) as main_window:
            self.window = main_window
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(
                        label="Load Spin Matrix",
                        callback=load_dialog_callback,
                        check=False,
                        user_data=(self, load_file, "spin"),
                    )
                    dpg.add_menu_item(
                        label="Load NMR File",
                        callback=load_dialog_callback,
                        check=False,
                        user_data=(self, load_nmr, "nmr"),
                    )
                    dpg.add_menu_item(
                        label="Save Optimization",
                        callback=save_dialog_callback,
                        check=False,
                        user_data=(self, save_opt, "optimization"),
                        enabled=False,
                        tag="opt_save",
                    )
                dpg.add_menu_item(label="Help", callback=test_callback)

                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(
                        label="Save Settings",
                        callback=lambda: dpg.show_item(save_settings),
                        check=False,
                    )
                    dpg.add_menu_item(
                        label="Load Settings",
                        callback=lambda: dpg.show_item(load_settings),
                        check=False,
                    )

                with dpg.menu(label="Theme"):
                    dpg.add_radio_button(
                        ("Dark", "Light"),
                        callback=change_theme_callback,
                        default_value="Dark",
                    )

                with dpg.menu(label="Widget Items"):
                    dpg.add_checkbox(label="Pick Me", callback=test_callback)
                    dpg.add_button(label="Press Me", callback=test_callback)
                    dpg.add_color_picker(label="Color Me", callback=test_callback)

                with dpg.menu(label="View", tag="view_menu"):
                    dpg.add_menu_item(
                        label="Show Spin Matrix Table",
                        callback=show_item_callback,
                        user_data="matrix_window",
                    )

            self.sim_settings = SimulationSettings(
                self, main_window, **self.settings["sim_settings"]
            )

            dpg.add_separator()

            self.opt_settings = OptimizationSettings(
                self, main_window, **self.settings["opt_settings"]
            )

            dpg.add_separator()

            self.water_settings = WaterSettings(
                self, main_window, True, **self.settings["water_sim"]
            )

            self.plot_window = PlotWindow(self, main_window, True)

            self.buttons["fit_axes"] = Button(
                label="Fit Axes",
                callback=lambda: fit_axes(
                    {"x_axis": "main_x_axis", "y_axis": "main_y_axis"}
                ),
                enabled=False,
            )

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
        from solventspinsim.main import DPGStatus

        dpg.create_context()
        DPGStatus.set_context_status(True)

        dpg.create_viewport(title=self.title, decorated=True, **viewport_kwargs)
        DPGStatus.set_viewport_status(True)

        dpg.setup_dearpygui()

        self.main_window()

        dpg.show_viewport()
        dpg.start_dearpygui()
