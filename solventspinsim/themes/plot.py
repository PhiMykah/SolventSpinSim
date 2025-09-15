import dearpygui.dearpygui as dpg


def sim_theme_components() -> None:
    with dpg.theme_component(dpg.mvLineSeries):
        dpg.add_theme_color(
            dpg.mvPlotCol_Line,
            (76, 114, 176),
            category=dpg.mvThemeCat_Plots,
        )


def nmr_theme_components() -> None:
    with dpg.theme_component(dpg.mvLineSeries):
        dpg.add_theme_color(
            dpg.mvPlotCol_Line,
            (221, 132, 82),
            category=dpg.mvThemeCat_Plots,
        )


def region_theme_components() -> None:
    with dpg.theme_component(dpg.mvLineSeries):
        dpg.add_theme_color(
            dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots
        )
    with dpg.theme_component(dpg.mvInfLineSeries):
        dpg.add_theme_color(
            dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots
        )
