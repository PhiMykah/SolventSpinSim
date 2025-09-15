import dearpygui.dearpygui as dpg

from .component import Component


class Text(Component):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_text and manages automatic disabling theme.

        Use:
            text = Text("Test")
        """
        super().__init__(*args, **kwargs)

        self.text = dpg.add_text(*self._args, **self._kwargs)

        if self.is_enabled is False:
            self.disable()
