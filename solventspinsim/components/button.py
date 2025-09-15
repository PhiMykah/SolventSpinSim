import dearpygui.dearpygui as dpg

from solventspinsim.themes import hover_callback

from .component import Component


class Button(Component):
    def __init__(self, *args, **kwargs):
        """
        Wraps dpg.add_button and manages automatic disabling theme.

        Use:
            btn = Button(label="My Button", callback=my_callback)
        """

        super().__init__(*args, **kwargs)

        # Create the button
        self.button = dpg.add_button(*self._args, **self._kwargs)
        with dpg.handler_registry():
            dpg.add_mouse_move_handler(
                tag=f"{self.tag}_hover_handler",
                callback=hover_callback,
                user_data=self.tag,
            )

        if self.is_enabled is False:
            self.disable()
