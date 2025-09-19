from sys import stderr
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg
from nmrPype import DataFrame, write_to_file
from numpy import argmax
from numpy import array as nparray

from solventspinsim.settings import load_settings_callback, save_settings_callback
from solventspinsim.spin import Spin, loadSpinFromFile

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
    from solventspinsim.ui import UI
    from solventspinsim.components import Button


def spin_file_dialog(ui: "UI"):
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=set_spin_file,
        width=800,
        height=400,
        user_data=ui,
    ) as load_file_dialog:
        dpg.add_file_extension("", color=(150, 255, 150, 255))
        dpg.add_file_extension(
            "Text Files (*.txt *.csv){.txt,.csv}", color=(0, 255, 255, 255)
        )
    return load_file_dialog


def nmr_file_dialog(ui: "UI"):
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=set_nmr_file_callback,
        width=800,
        height=400,
        user_data=ui,
    ) as load_nmr_dialog:
        dpg.add_file_extension("", color=(150, 255, 150, 255))
        dpg.add_file_extension("FT1 Files (*.ft1){.ft1,}", color=(0, 255, 255, 255))
    return load_nmr_dialog


def load_settings_dialog(ui: "UI"):
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=load_settings_callback,
        width=800,
        height=400,
        user_data=(ui.settings, ui),
    ) as settings_dialog:
        dpg.add_file_extension("", color=(150, 255, 150, 255))
        dpg.add_file_extension(
            "Settings Files (*.json){.json,}", color=(0, 255, 255, 255)
        )
    return settings_dialog


def save_settings_dialog(ui: "UI"):
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=save_settings_callback,
        width=800,
        height=400,
        default_filename="settings.",
        user_data=(ui.settings, ui),
    ) as settings_dialog:
        dpg.add_file_extension("JSON Files (*.json){.json,}", color=(0, 255, 255, 255))
    return settings_dialog


def save_optimization_dialog(ui: "UI"):
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=_save_optimization_to_nmr,
        width=800,
        height=400,
        default_filename="",
        user_data=ui,
    ) as optimization_dialog:
        dpg.add_file_extension("FT1 Files (*.ft1){.ft1,}", color=(0, 255, 255, 255))
    return optimization_dialog


def load_dialog_callback(
    sender, app_data, user_data: "tuple[UI, int | str, str, bool]"
) -> None:
    ui: UI = user_data[0]
    dialog: int | str = user_data[1]
    dialog_type: str = user_data[2]
    try:
        add_spin: bool = user_data[3]
    except IndexError:
        add_spin: bool = False

    if dialog_type == "nmr":
        if not ui.nmr_file or add_spin:
            dpg.show_item(dialog)
        else:
            _load_nmr(sender, app_data, ui)
    else:
        if not ui.spin_file or add_spin:
            dpg.show_item(dialog)
        else:
            _load_spin(sender, app_data, ui)


def save_dialog_callback(
    sender, app_data, user_data: "tuple[UI, int | str, str]"
) -> None:
    ui: UI = user_data[0]
    dialog: int | str = user_data[1]
    dialog_type: str = user_data[2]
    if dialog_type == "optimization":
        if not ui.output_file:
            dpg.show_item(dialog)
        else:
            _save_optimization_to_nmr(sender, ui.output_file, ui)
    else:
        if not ui.output_file:
            dpg.show_item(dialog)
        else:
            _save_optimization_to_nmr(sender, ui.output_file, ui)


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
    if ui.spin_file in ui.spins.keys():
        ui.current_spin = ui.spins[ui.spin_file]
    else:
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
        spin = Spin(spin_names, nuclei_frequencies, couplings)
        ui.current_spin = spin
        ui.spins[ui.spin_file] = spin

    if not dpg.is_item_enabled("add_spin"):
        dpg.enable_item("add_spin")

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
            ui.current_spin,
            ui.sim_settings.points,
            ui.water_sim,
            ui.current_spin.half_height_width,
            ui.current_spin._nuclei_number,
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


def _save_optimization_to_nmr(sender, app_data, ui: "UI") -> None:
    from solventspinsim.simulate import simulate_peaklist

    if isinstance(app_data, dict):
        user_file = app_data["file_path_name"]
    elif isinstance(app_data, str):
        user_file = app_data
    else:
        return

    ui.settings.update_settings(ui)

    nmr_file = ui.settings["nmr_file"]
    field_strength = ui.settings["sim_settings"]["field_strength"]
    df = DataFrame(nmr_file)

    nmr_array = load_nmr_array(nmr_file, field_strength)
    l_limit: float = nmr_array[0][-1]
    r_limit: float = nmr_array[0][0]

    spin_simulation = simulate_peaklist(
        ui.current_spin.peaklist(),
        ui.points,
        ui.current_spin.half_height_width,
        (l_limit, r_limit),
    )

    water = ui.water_sim
    if water.water_enable:
        water_simulation = simulate_peaklist(
            water.peaklist, ui.points, water.hhw, (l_limit, r_limit)
        )

        simulation = [spin_simulation[0], spin_simulation[1] + water_simulation[1]]
    else:
        simulation = [spin_simulation[0], spin_simulation[1]]

    result_array = nparray(simulation[1][::-1], dtype="float32")
    df.setArray(result_array)

    output_file: str = user_file if user_file else "output.ft1"

    write_to_file(df, output_file, True)
