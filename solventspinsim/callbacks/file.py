from sys import stderr
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg
from numpy import argmax
from spin import Spin, loadSpinFromFile

from .callbacks import set_water_range_callback
from .nmr import load_nmr_array
from .plot import (
    add_subplots,
    fit_axes,
    set_nmr_plot_values,
    update_plot_callback,
    update_simulation_plot,
    zoom_subplots_to_peaks,
)

if TYPE_CHECKING:
    from ui import UI
    from ui.components import Button


def load_dialog_callback(
    sender, app_data, user_data: "tuple[UI, int | str, str]"
) -> None:
    ui: UI = user_data[0]
    dialog: int | str = user_data[1]
    dialog_type: str = user_data[2]
    if dialog_type == "nmr":
        if not ui.nmr_file:
            dpg.show_item(dialog)
        else:
            _load_nmr(sender, app_data, ui)
    else:
        if not ui.spin_file:
            dpg.show_item(dialog)
        else:
            _load_spin(sender, app_data, ui)


def set_spin_file(sender, app_data: dict, user_data: "UI") -> None:
    """
    Sets the spin file of a UI object to the selected file path.
    Additionally trigger plot update and set spin value.
    Optionally triggers a plot update.
    """
    file: str = app_data["file_path_name"]
    ui: "UI" = user_data

    if not file:
        print("No file found, skipping update...", file=stderr)
        return

    ui.spin_file = file

    _load_spin(sender, app_data, ui)


def _load_spin(sender, app_data, ui: "UI"):
    spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
    spin = Spin(spin_names, nuclei_frequencies, couplings)
    ui.spin = spin

    if ui.sim_settings is not None:
        ui.sim_settings.enable()

    add_subplots(ui)
    zoom_subplots_to_peaks(ui)
    update_plot_callback(sender, app_data, ui)


def set_nmr_file_callback(sender, app_data, ui: "UI") -> None:
    """
    Sets the NMR file attribute and optionally updates the NMR plot.
    """
    file = app_data["file_path_name"]

    ui.nmr_file = file

    _load_nmr(sender, app_data, ui)


def _load_nmr(sender, app_data, ui: "UI"):
    field_strength: float = getattr(ui, "field_strength", 500.0)
    nmr_array = load_nmr_array(ui.nmr_file, field_strength)
    ui.sim_settings.points = len(nmr_array[0])

    if dpg.get_value("main_plot_added"):
        update_simulation_plot(
            ui.spin,
            ui.sim_settings.points,
            ui.water_sim,
            ui.spin.half_height_width,
            ui.spin._nuclei_number,
        )
    set_nmr_plot_values(nmr_array)

    optimize_button: "Button | None" = ui.buttons.get("optimize", None)
    fit_axes_button: "Button | None" = ui.buttons.get("fit_axes", None)

    if (
        (optimize_button is not None)
        and dpg.get_value("main_plot_added")
        and not optimize_button.is_enabled
    ):
        optimize_button.enable()
    if (fit_axes_button is not None) and not fit_axes_button.is_enabled:
        fit_axes_button.enable()

    fit_axes({"x_axis": "main_x_axis", "y_axis": "main_y_axis"})

    highest_peak_index = argmax(nmr_array[1])
    water_peak_x_value = nmr_array[0][highest_peak_index]

    set_water_range_callback(sender, water_peak_x_value - 100.0, (ui, "left"))
    set_water_range_callback(sender, water_peak_x_value + 100.0, (ui, "right"))

    dpg.show_item("water_drag_left")
    dpg.show_item("water_center_line")
    dpg.show_item("water_drag_right")


def load_settings_file(sender, app_data, user_data) -> None:
    file = app_data["file_path_name"]
    dpg.configure_app(init_file=file)
