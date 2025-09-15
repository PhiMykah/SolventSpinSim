import dearpygui.dearpygui as dpg

from .component import Component


class InputFloat(Component):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_input_float and manages automatic disabling theme.

        Use:
            drag_float = InputFloat(label="Label Float", callback=my_callback, source="my_source")
        """
        super().__init__(*args, **kwargs)

        self.input_float = dpg.add_input_float(*self._args, **self._kwargs)

        if self.is_enabled is False:
            self.disable()


class InputInt(Component):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_input_float and manages automatic disabling theme.

        Use:
            drag_float = InputFloat(label="Label Float", callback=my_callback, source="my_source")
        """
        super().__init__(*args, **kwargs)

        self.input_float = dpg.add_input_int(*self._args, **self._kwargs)

        if self.is_enabled is False:
            self.disable()


class DragFloat(Component):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_drag_float and manages automatic disabling theme.

        Use:
            drag_float = DragFloat(label="Label Float", callback=my_callback, source="my_source")
        """

        super().__init__(*args, **kwargs)

        self.drag_float = dpg.add_drag_float(*self._args, **self._kwargs)

        if self.is_enabled is False:
            self.disable()


class Checkbox(Component):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_checkbox and manages automatic disabling theme.

        Use:
            chk = Checkbox(label="My Checkbox", default_value=False, source="my_source")
        """

        super().__init__(*args, **kwargs)

        self.checkbox = dpg.add_checkbox(*self._args, **self._kwargs)

        if self.is_enabled is False:
            self.disable()
