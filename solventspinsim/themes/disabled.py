import dearpygui.dearpygui as dpg

from .styles import button_style


def disabled_theme_components(theme: dict):
    with dpg.theme_component(dpg.mvButton, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            theme["BASE50"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_Button,
            theme["BASE_DISABLED"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonHovered,
            theme["BASE_DISABLED"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonActive,
            theme["BASE_DISABLED"],
        )
        button_style()

    with dpg.theme_component(dpg.mvInputFloat, enabled_state=False):
        dpg.add_theme_color(
            dpg.mvThemeCol_Button,
            theme["BASE_DISABLED"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonHovered,
            theme["BASE_DISABLED"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_ButtonActive,
            theme["BASE_DISABLED"],
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_FrameBg,
            theme["BASE_DISABLED"] + (100,),
        )
        dpg.add_theme_color(
            dpg.mvText,
            theme["BASE_DISABLED"] + (100,),
        )
        button_style()
