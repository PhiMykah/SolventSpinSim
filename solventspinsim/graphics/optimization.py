from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg
from callbacks import help_msg, set_water_range_callback
from optimize import optimize_callback
from ui.components import Button

from .graphics import Graphic

if TYPE_CHECKING:
    from ui import UI


class OptimizationSettings(Graphic):
    water_left_tag: str = "water_left"
    water_right_tag: str = "water_right"

    def __init__(
        self,
        ui: "UI | None" = None,
        parent: str | int | None = None,
        is_enabled: bool = False,
        water_left: float = 0.0,
        water_right: float = 100.0,
    ) -> None:
        self.params = {
            OptimizationSettings.water_left_tag: water_left,
            OptimizationSettings.water_right_tag: water_right,
        }

        super().__init__(ui, parent, is_enabled)

    def render(self) -> None:
        dpg.add_text(
            default_value="Optimization Settings",
            tag="opt_settings_title",
            parent=self.parent,
        )

        water_left, water_right = self.params.keys()
        with dpg.value_registry():
            dpg.add_float_value(
                default_value=self.params[water_left], tag=f"{water_left}_value"
            )
            dpg.add_float_value(
                default_value=self.params[water_right], tag=f"{water_right}_value"
            )

        with dpg.table(header_row=False, parent=self.parent):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_drag_float(
                    label="Water Left Limit",
                    format="%.02f",
                    source=f"{water_left}_value",
                    tag=water_left,
                    callback=set_water_range_callback,
                    user_data=(self.ui, "left"),
                )
                help_msg("Leftmost region of the water signal peak")

                dpg.add_drag_float(
                    label="Water Right Limit",
                    format="%.02f",
                    source=f"{water_right}_value",
                    tag=water_right,
                    callback=set_water_range_callback,
                    user_data=(self.ui, "right"),
                )
                help_msg("Rightmost region of the water signal peak")

        self.ui.buttons["optimize"] = Button(
            label="Optimize",
            callback=optimize_callback,
            user_data=self.ui,
            enabled=False,
            parent=self.parent,
        )
