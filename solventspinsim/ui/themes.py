import dearpygui.dearpygui as dpg

class Theme:
    _disabled_theme = None
    _red_line_theme = None

    @classmethod
    def disabled_theme(cls):
        """
        Loads the disable theme or accesses the disabled theme

        Assumes that the dpg context has been created.
        """
        if cls._disabled_theme is None:
            with dpg.theme() as disabled_theme:
                with dpg.theme_component(dpg.mvButton, enabled_state=False):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [128, 128, 128])
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [165, 178, 194])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [165, 178, 194])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [165, 178, 194])
            cls._disabled_theme = disabled_theme
        return cls._disabled_theme
    
    @classmethod
    def red_line_theme(cls):
        """
        Load or access the red-line plot theme

        Assumes that the dpg context has been created.
        """
        if cls._red_line_theme is None:
            with dpg.theme() as red_line_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots)
                with dpg.theme_component(dpg.mvStemSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots)
                with dpg.theme_component(dpg.mvScatterSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots)

            cls._red_line_theme = red_line_theme
        return cls._red_line_theme