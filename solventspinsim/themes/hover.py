import dearpygui.dearpygui as dpg


def hover_theme_components(theme: dict):
    # with dpg.theme_component(dpg.mvInputFloat):
    #     dpg.add_theme_color(dpg.mvThemeCol_Text, theme["ACCENT_CONTENT"])
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Text, theme["ACCENT_CONTENT"])
