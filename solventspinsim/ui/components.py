from gc import enable
import dearpygui.dearpygui as dpg
from ui.themes import Theme

class Button:
    def __init__(self, *args, **kwargs):
        """
        Wraps dpg.add_button and manages automatic disabling theme.

        Use:
            btn = Button(label="My Button", callback=my_callback)
        """

        # Extract a user-provided tag or create our own
        self.label : str = kwargs.get("label", "")
        self.tag : int | str = kwargs.get("tag", dpg.generate_uuid())
        kwargs["tag"] = self.tag
        kwargs["label"] = self.label
        self.is_enabled = False

        # Create the button
        self.button = dpg.add_button(*args, **kwargs)
        if kwargs.get('enabled', True) is False:
            self.disable()

    def disable(self) -> None:
        dpg.disable_item(self.tag)
        dpg.bind_item_theme(self.tag, Theme.disabled_theme())
        self.is_enabled = False

    def enable(self) -> None:
        dpg.enable_item(self.tag)
        dpg.bind_item_theme(self.tag, 0)  # Unbinds the disabled_theme
        self.is_enabled = True

    def hide(self) -> None:
        dpg.hide_item(self.tag)

    def show(self) -> None:
        dpg.show_item(self.tag)

    def toggle_visibility(self) -> None:
        if dpg.is_item_shown(self.tag):
            self.hide()
        else:
            self.show()
    
    def get_tag(self) -> int | str:
        return self.tag
