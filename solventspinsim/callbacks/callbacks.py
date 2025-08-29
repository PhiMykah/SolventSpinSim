from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from .plot import (
    fit_axes,
    update_plotting_ui,
    update_simulation_plot,
    zoom_subplots_to_peaks,
)

if TYPE_CHECKING:
    from typing import Literal

    from ui import UI

# ---------------------------------------------------------------------------- #
#                              Callback Functions                              #
# ---------------------------------------------------------------------------- #

# ---------------------- Utility and Debug Callbacks ------------------------- #


def test_callback(sender, app_data, user_data) -> None:
    """Debug callback to print sender, app_data, and user_data."""
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")


def close_application(sender, app_data, user_data) -> None:
    """Callback to close all windows and the viewport."""
    dpg.stop_dearpygui()


def viewport_resize_callback(sender, app_data, user_data) -> None:
    """Callback to handle viewport resizing events."""
    current_width = dpg.get_viewport_width()
    current_height = dpg.get_viewport_height()
    print(f"Viewport resized to: Width={current_width}, Height={current_height}")


def help_msg(message) -> None:
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text("(?)", color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)


def show_item_callback(sender, app_data, user_data: int | str) -> None:
    if dpg.does_item_exist(user_data):
        dpg.show_item(user_data)


def hide_item_callback(sender, app_data, user_data: int | str) -> None:
    if dpg.does_item_exist(user_data):
        dpg.hide_item(user_data)


def toggle_visibility_callback(sender, app_data, user_data: int | str) -> None:
    if dpg.does_item_exist(user_data):
        if dpg.is_item_shown(user_data):
            dpg.hide_item(user_data)
        else:
            dpg.show_item(user_data)


# ---------------------- Attribute Setter Callback --------------------------- #


def setter_callback(sender, app_data, user_data: tuple[object, str]) -> None:
    """
    Sets the attribute `user_data[1]` of object `user_data[0]` to value app_data.
    """
    setattr(user_data[0], user_data[1], app_data)


def set_points_callback(sender, app_data, user_data: "UI") -> None:
    user_data.points = app_data
    if not user_data.spin.spin_names:
        return
    update_simulation_plot(
        user_data.spin,
        user_data.points,
        user_data.water_sim,
        user_data.spin.half_height_width,
        user_data.spin._nuclei_number,
    )


def set_field_strength_callback(sender, app_data, user_data: "UI") -> None:
    user_data.sim_settings["field_strength"] = app_data
    if not user_data.spin.spin_names:
        return
    user_data.spin.field_strength = app_data
    user_data.spin.nuclei_frequencies = user_data.spin._ppm_nuclei_frequencies

    update_simulation_plot(
        user_data.spin,
        user_data.points,
        user_data.water_sim,
        user_data.spin.half_height_width,
        user_data.spin._nuclei_number,
    )
    update_plotting_ui(user_data)
    zoom_subplots_to_peaks(user_data)
    fit_axes(user_data.plot_tags["main"])


def set_intensity_callback(sender, app_data, user_data: "UI") -> None:
    if user_data.spin._nuclei_number == 0:
        return
    user_data.spin.intensities = [app_data] * user_data.spin._nuclei_number

    update_simulation_plot(
        user_data.spin,
        user_data.points,
        user_data.water_sim,
        user_data.spin.half_height_width,
        user_data.spin._nuclei_number,
    )
    update_plotting_ui(user_data)
    zoom_subplots_to_peaks(user_data)


def set_hhw_callback(sender, app_data, user_data: "UI") -> None:
    if user_data.spin._nuclei_number == 0:
        return
    user_data.spin.half_height_width = app_data

    update_simulation_plot(
        user_data.spin,
        user_data.points,
        user_data.water_sim,
        user_data.spin.half_height_width,
        user_data.spin._nuclei_number,
    )
    update_plotting_ui(user_data)
    zoom_subplots_to_peaks(user_data)


def set_water_range_callback(
    sender, app_data, user_data: "tuple[UI, Literal['left'] | Literal['right']]"
):
    ui: "UI" = user_data[0]
    side: "Literal['left'] | Literal['right']" = user_data[1]

    item_alias = dpg.get_item_alias(sender)
    if item_alias in ("water_drag_left", "water_drag_right"):
        value = dpg.get_value(sender)
    else:
        value = app_data

    if side == "left":
        start = value
        end = value + 1
        if dpg.get_value("water_right_value") > start:
            end = dpg.get_value("water_right_value")
    else:
        start = value - 1
        end = value
        if dpg.get_value("water_left_value") < end:
            start = dpg.get_value("water_left_value")

    ui.water_range = (start, end)

    dpg.set_value("water_left_value", start)
    ui.opt_settings["water_left"] = start
    dpg.set_value("water_right_value", end)
    ui.opt_settings["water_right"] = end

    dpg.set_value("water_drag_left", start)
    dpg.set_value("water_drag_right", end)
    dpg.set_value("water_center_line", (start + end) / 2)


def set_ui_water_callback(sender, app_data, user_data: "tuple[UI, str]") -> None:
    ui = user_data[0]
    attribute = user_data[1]

    setattr(ui.water_sim, attribute, app_data)

    update_simulation_plot(
        ui.spin,
        ui.points,
        ui.water_sim,
        ui.spin.half_height_width,
        ui.spin._nuclei_number,
    )
    update_plotting_ui(ui)
    zoom_subplots_to_peaks(ui)
