from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from solventspinsim.components.text import Text
from solventspinsim.themes import Theme

from .button import Button, step_value_callback
from .component import Component

if TYPE_CHECKING:
    from typing import Callable


class Input(Component):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.has_step_buttons = False

    def initialize(
        self,
        source_function: "Callable",
        dpg_function: "Callable",
    ):
        with dpg.value_registry():
            src = self._kwargs.get("source", None)
            if src:
                self.source = src
            else:
                self.source = source_function
                self._kwargs["source"] = self.source

        if self.has_step_buttons:
            self.step = self._kwargs.get("step", 1.0)
            self._kwargs["step"] = 0

        kwarg_label: str = self._kwargs["label"]
        if kwarg_label.startswith("##"):
            show_text = True
        else:
            show_text = False

        self._kwargs["label"] = ""
        with dpg.group(horizontal=True, horizontal_spacing=3) as input_group:
            self.group_tag = input_group
            self._kwargs.pop("enabled", None)
            self.input_float = dpg_function(*self._args, **self._kwargs)
            if self.has_step_buttons:
                self.decrease = Button(
                    label="-",
                    callback=step_value_callback,
                    user_data=(self.source, self.step, True),
                )
                self.increase = Button(
                    label="+",
                    callback=step_value_callback,
                    user_data=(self.source, self.step),
                )

            if show_text:
                self.text = Text(self.label)
                self.tags += [self.group_tag, self.text.tag]
            else:
                self.tags += [self.group_tag]

        if self.has_step_buttons:
            self.tags += [self.decrease.tag, self.increase.tag]

        if self.is_enabled is False:
            self.disable()

    def disable(self) -> None:
        dpg.disable_item(self.group_tag)
        dpg.bind_item_theme(self.tag, Theme.disabled_theme())
        self.is_enabled = False
        if self.has_step_buttons:
            self.decrease.disable()
            self.increase.disable()

    def enable(self) -> None:
        dpg.enable_item(self.group_tag)
        dpg.bind_item_theme(self.tag, Theme.global_theme())
        self.is_enabled = True
        if self.has_step_buttons:
            self.decrease.enable()
            self.increase.enable()

    def hide(self) -> None:
        dpg.hide_item(self.group_tag)
        if hasattr(self, "info_tag"):
            if dpg.does_item_exist(self.info_tag):
                dpg.hide_item(self.info_tag)

    def show(self) -> None:
        dpg.show_item(self.group_tag)
        if hasattr(self, "info_tag"):
            if dpg.does_item_exist(self.info_tag):
                dpg.show_item(self.info_tag)

    def set_help_msg(self, message):
        group = dpg.add_group(horizontal=True, horizontal_spacing=3)
        dpg.move_item(self.group_tag, parent=group)
        dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
        self.info_tag = f"{self.label}_info"
        t = dpg.add_text(
            "(?)",
            color=Theme._theme_collection[Theme._current_theme]["INFO"],
            tag=self.info_tag,
        )
        Theme.add_info_tag(f"{self.label}", f"{self.label}_info")
        with dpg.tooltip(t):
            dpg.add_text(message)


class InputFloat(Input):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_input_float and manages enabling, disabling, visibility, and themes.

        Use:
            input_float = InputFloat(label="Label Float", callback=my_callback, source="my_source")

        Args:
            label (str, optional): Overrides 'name' as label.
            user_data (Any, optional): User data for callbacks
            use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
            tag (Union[int, str], optional): Unique id used to programmatically refer to the item.If label is unused this will be the label.
            width (int, optional): Width of the item.
            indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
            parent (Union[int, str], optional): Parent to add this item to. (runtime adding)
            before (Union[int, str], optional): This item will be displayed before the specified item in the parent.
            source (Union[int, str], optional): Overrides 'id' as value storage key.
            payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
            callback (Callable, optional): Registers a callback.
            drag_callback (Callable, optional): Registers a drag callback for drag and drop.
            drop_callback (Callable, optional): Registers a drop callback for drag and drop.
            show (bool, optional): Attempt to render widget.
            enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
            pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
            filter_key (str, optional): Used by filter widget.
            tracked (bool, optional): Scroll tracking
            track_offset (float, optional): 0.0f:top, 0.5f:center, 1.0f:bottom
            default_value (float, optional):
            format (str, optional): Determines the format the float will be displayed as use python string formatting.
            min_value (float, optional): Value for lower limit of input. By default this limits the step buttons. Use min_clamped to limit manual input.
            max_value (float, optional): Value for upper limit of input. By default this limits the step buttons. Use max_clamped to limit manual input.
            step (float, optional): Increment to change value by when the step buttons are pressed. Setting this and step_fast to a value of 0 or less will turn off step buttons.
            step_fast (float, optional): Increment to change value by when ctrl + step buttons are pressed. Setting this and step to a value of 0 or less will turn off step buttons.
            min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
            max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
            on_enter (bool, optional): Only runs callback on enter key press.
            readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
            id (Union[int, str], optional): (deprecated)
        """
        super().__init__(*args, **kwargs)
        self.has_step_buttons = True
        self.initialize(dpg.add_float_value, dpg.add_input_float)


class InputInt(Input):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_input_float and manages automatic disabling theme.

        Use:
            drag_float = InputFloat(label="Label Float", callback=my_callback, source="my_source")
        """
        super().__init__(*args, **kwargs)
        self.has_step_buttons = True
        self.initialize(dpg.add_int_value, dpg.add_input_int)


class DragFloat(Input):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_drag_float and manages automatic disabling theme.

        Use:
            drag_float = DragFloat(label="Label Float", callback=my_callback, source="my_source")
        """

        super().__init__(*args, **kwargs)
        self.has_step_buttons = False
        self.initialize(dpg.add_float_value, dpg.add_drag_float)


class Checkbox(Input):
    def __init__(self, *args, **kwargs) -> None:
        """
        Wraps dpg.add_checkbox and manages automatic disabling theme.

        Use:
            chk = Checkbox(label="My Checkbox", default_value=False, source="my_source")
        """

        super().__init__(*args, **kwargs)
        self.has_step_buttons = False
        self.initialize(dpg.add_bool_value, dpg.add_checkbox)
