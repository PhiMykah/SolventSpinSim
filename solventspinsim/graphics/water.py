from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from .graphics import Graphic

if TYPE_CHECKING:
    from solventspinsim.ui import UI


def set_ui_water_callback(sender, app_data, user_data: "tuple[UI, str]") -> None:
    from solventspinsim.callbacks import (
        update_plotting_ui,
        update_simulation_plot,
        zoom_subplots_to_peaks,
    )

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


class WaterSettings(Graphic):
    water_enable_tag: str = "water_enable"
    water_frequency_tag: str = "water_frequency"
    water_intensity_tag: str = "water_intensity"
    water_hhw_tag: str = "water_hhw"

    def __init__(
        self,
        ui: "UI | None" = None,
        parent: str | int | None = None,
        is_enabled: bool = False,
        water_enable: bool = True,
        frequency: float = 0.0,
        intensity: float = 1.0,
        hhw: float = 0.1,
    ) -> None:
        self.params = {
            WaterSettings.water_enable_tag: water_enable,
            WaterSettings.water_frequency_tag: frequency,
            WaterSettings.water_intensity_tag: intensity,
            WaterSettings.water_hhw_tag: hhw,
        }

        super().__init__(ui, parent, is_enabled)

    def render(self) -> None:
        dpg.add_text(default_value="Simulation Water Signal")
        water_enable, water_frequency, water_intensity, water_hhw = self.params.keys()

        with dpg.value_registry():
            dpg.add_bool_value(
                default_value=self.params[water_enable], tag=f"{water_enable}_value"
            )
            dpg.add_float_value(
                default_value=self.params[water_frequency],
                tag=f"{water_frequency}_value",
            )
            dpg.add_float_value(
                default_value=self.params[water_intensity],
                tag=f"{water_intensity}_value",
            )
            dpg.add_float_value(
                default_value=self.params[water_hhw], tag=f"{water_hhw}_value"
            )

        dpg.add_checkbox(
            label="Enable Water Simulation",
            default_value=self.params[water_enable],
            source=f"{water_enable}_value",
            tag=water_enable,
            callback=set_ui_water_callback,
            user_data=(self.ui, "water_enable"),
        )

        with dpg.table(header_row=False, parent=self.parent):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_drag_float(
                    label="Water Frequency",
                    format="%.02f",
                    tag=water_frequency,
                    source=f"{water_frequency}_value",
                    callback=set_ui_water_callback,
                    user_data=(self.ui, "frequency"),
                )

                dpg.add_drag_float(
                    label="Water Intensity",
                    format="%.02f",
                    tag=water_intensity,
                    source=f"{water_intensity}_value",
                    speed=0.1,
                    max_value=500,
                    callback=set_ui_water_callback,
                    user_data=(self.ui, "intensity"),
                )

            with dpg.table_row():
                dpg.add_drag_float(
                    label="Water Half-height Width",
                    format="%.02f",
                    tag=water_hhw,
                    source=f"{water_hhw}_value",
                    speed=0.1,
                    callback=set_ui_water_callback,
                    user_data=(self.ui, "hhw"),
                )
