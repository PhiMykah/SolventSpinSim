from sys import stderr
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from solventspinsim.callbacks import (
    update_plotting_ui,
    update_simulation_plot,
    zoom_subplots_to_peaks,
)
from solventspinsim.spin import Spin, loadSpinFromFile

from .optimize import optimize_simulation

if TYPE_CHECKING:
    from solventspinsim.ui import UI


def optimize_callback(sender, app_data, user_data: "UI"):
    if not hasattr(user_data, "spin_file") or not user_data.spin_file:
        print("Failed to Optimize! Missing Requirement: spin_file", file=stderr)
        return
    if not hasattr(user_data, "nmr_file") or not user_data.nmr_file:
        print("Failed to Optimize! Missing Requirement: nmr_file", file=stderr)
        return

    nmr_file: str = user_data.nmr_file
    spin_matrix_file: str = user_data.spin_file
    field_strength: float = user_data.sim_settings["field_strength"]
    if len(user_data.water_range) == 2:
        water_range: tuple[float, float] = user_data.water_range
    elif len(user_data.water_range) > 2:
        water_range: tuple[float, float] = (
            user_data.water_range[0],
            user_data.water_range[1],
        )
    else:
        raise ValueError("Water range is invalid. Water range must be two values!")

    init_hhw: list[float | int] = user_data.current_spin.half_height_width

    if dpg.does_item_exist("water_drag_left"):
        dpg.hide_item("water_drag_left")
    if dpg.does_item_exist("water_center_line"):
        dpg.hide_item("water_center_line")
    if dpg.does_item_exist("water_drag_right"):
        dpg.hide_item("water_drag_right")

    if user_data.sim_settings["use_settings"]:
        initial_spin = user_data.current_spin
    else:
        spin_names, nuclei_frequencies, couplings = loadSpinFromFile(spin_matrix_file)
        initial_spin = Spin(
            spin_names,
            nuclei_frequencies,
            couplings,
            half_height_width=init_hhw,
            field_strength=field_strength,
        )

    if user_data.water_sim.water_enable:
        optimizations = optimize_simulation(
            nmr_file, initial_spin, water_range, user_data.water_sim
        )
    else:
        optimizations = optimize_simulation(nmr_file, initial_spin, water_range, None)

    if isinstance(optimizations, Spin):
        optimized_spin = optimizations
        optimized_water = user_data.water_sim
    else:
        optimized_spin = optimizations[0]
        optimized_water = optimizations[1]

    setattr(user_data, "spin", optimized_spin)
    setattr(user_data, "water_sim", optimized_water)

    update_simulation_plot(
        optimized_spin,
        user_data.points,
        optimized_water,
        optimized_spin.half_height_width,
        optimized_spin._nuclei_number,
    )
    update_plotting_ui(user_data)
    zoom_subplots_to_peaks(user_data)

    dpg.enable_item("opt_save")
