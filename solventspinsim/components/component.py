import dearpygui.dearpygui as dpg

from solventspinsim.themes import Theme


class Component:
    """
    Wraps a dpg component with helpful handling commands.

    Use:
        component = Component(*args, **kwargs)
    """

    def __init__(self, *args, **kwargs):
        self.label: str = kwargs.get("label", "")
        # Extract a user-provided tag or create our own
        self.tag: int | str = kwargs.get("tag", dpg.generate_uuid())
        self.tags = [self.tag]
        kwargs["tag"] = self.tag
        kwargs["label"] = self.label
        self._args = args
        self._kwargs = kwargs
        self.is_enabled: bool = kwargs.get("enabled", True)

    def disable(self) -> None:
        dpg.disable_item(self.tag)
        dpg.bind_item_theme(self.tag, Theme.disabled_theme())
        self.is_enabled = False

    def enable(self) -> None:
        dpg.enable_item(self.tag)
        dpg.bind_item_theme(self.tag, Theme.global_theme())
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

    def set_help_msg(self, message):
        group = dpg.add_group(horizontal=True)
        dpg.move_item(self.tag, parent=group)
        dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
        info_tag = f"{self.tag}_info"
        t = dpg.add_text(
            "(?)",
            color=Theme._theme_collection[Theme._current_theme]["INFO"],
            tag=info_tag,
        )
        Theme.add_info_tag(f"{self.tag}", f"{self.tag}_info")
        with dpg.tooltip(t):
            dpg.add_text(message)
