from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from solventspinsim.themes import hover_callback

from .component import Component

if TYPE_CHECKING:
    from typing import Any


class Button(Component):
    def __init__(self, *args, **kwargs):
        """
        Wraps dpg.add_button and manages automatic disabling theme.

        Use:
            btn = Button(label="My Button", callback=my_callback)

        Args:
            label (str, optional): Overrides 'name' as label.
            user_data (Any, optional): User data for callbacks
            use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
            tag (Union[int, str], optional): Unique id used to programmatically refer to the item.If label is unused this will be the label.
            width (int, optional): Width of the item.
            height (int, optional): Height of the item.
            indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
            parent (Union[int, str], optional): Parent to add this item to. (runtime adding)
            before (Union[int, str], optional): This item will be displayed before the specified item in the parent.
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
            small (bool, optional): Shrinks the size of the button to the text of the label it contains. Useful for embedding in text.
            arrow (bool, optional): Displays an arrow in place of the text string. This requires the direction keyword.
            direction (int, optional): Sets the cardinal direction for the arrow by using constants mvDir_Left, mvDir_Up, mvDir_Down, mvDir_Right, mvDir_None. Arrow keyword must be set to True.
            repeat (bool, optional): Hold to continuosly repeat the click.
            id (Union[int, str], optional): (deprecated)
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


# ---------------------------------------------------------------------------- #
#                               Button Callbacks                               #
# ---------------------------------------------------------------------------- #


def step_value_callback(
    sender, app_data, user_data: "tuple[str, int | float | complex, bool]"
) -> None:
    source: str = user_data[0]
    value: Any = user_data[1]
    try:
        negate: int = -1 if user_data[2] else 1
    except IndexError:
        negate: int = 1

    dpg.set_value(source, dpg.get_value(source) + negate * value)
