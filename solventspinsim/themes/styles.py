import dearpygui.dearpygui as dpg


def button_style() -> None:
    """
    Assumes function is called within theme_component(dpg.mvButton) or similar component
    """
    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3)