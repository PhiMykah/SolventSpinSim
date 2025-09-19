import os
from pathlib import Path
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from solventspinsim.ui import UI
    from solventspinsim.components.component import Component


def load_static_texture(file: str, texture_tag: int | str = 0) -> int | str:
    if not Path(file).is_file():
        print(f"CWD: {os.getcwd()}")
        raise FileNotFoundError(f"Loading Texture Failed! File not found: {file}")
    with dpg.texture_registry():
        image_width, image_height, image_channels, image_buffer = dpg.load_image(file)
        return dpg.add_static_texture(
            image_width, image_height, image_buffer, tag=texture_tag
        )


class Graphic:
    def __init__(
        self,
        ui: "UI | None" = None,
        parent: str | int | None = None,
        is_enabled: bool = False,
    ) -> None:
        if ui is not None:
            self.ui: "UI" = ui
        if parent is not None:
            self.parent: str | int = parent

        self.is_enabled: bool = is_enabled
        self.is_rendered = False
        if not hasattr(self, "params"):
            self.params: dict = {}
        if not hasattr(self, "components"):
            self.components: "dict[str, Component]" = {}

        if ui is not None or parent is not None:
            self.render()

    def render(self) -> None:
        pass

    def update_ui_values(self) -> None:
        from solventspinsim.main import DPGStatus

        if DPGStatus.is_context_enabled():
            for key in self.params.keys():
                if dpg.does_item_exist(f"{key}_value"):
                    dpg.set_value(f"{key}_value", self.params[key])

    def disable(self) -> None:
        for component in self.components.values():
            component.disable()
        self.enabled = False

    def enable(self) -> None:
        for component in self.components.values():
            component.enable()
        self.enabled = True

    def toggle(self) -> None:
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def __getitem__(self, key):
        return self.params[key]

    def __setitem__(self, key, value):
        self.params[key] = value

    def get(self, key, default=None):
        return self.params.get(key, default)
